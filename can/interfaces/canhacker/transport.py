import threading
import queue
import logging
from typing import Any, Optional

from can.exceptions import (
    CanInitializationError,
    CanInterfaceNotImplementedError,
    error_check,
)

logger = logging.getLogger('CanHacker.' + __name__)
#: Log level for transport module messages
TRANSPORT_LOGGING_LEVEL = 8

from .message import *

try:
    import serial
except ImportError:
    logger.warning(
        "You won't be able to use the CanHacker can backend without "
        "the serial module installed!"
    )
    serial = None

class Transport:
    def __init__(
        self,
        port: str,
        ttyBaudrate: int = 115200,
        bitrate: Optional[int] = None,
        btr: Optional[str] = None,
        rtscts: bool = False,
        timeout: float = 0.001,
        **kwargs: Any,
    ) -> None:
        if serial is None:
            raise CanInterfaceNotImplementedError("The serial module is not installed")

        if not port:  # if None or empty
            raise ValueError("Must specify a serial port.")
        if "@" in port:
            (port, baudrate) = port.split("@")
            ttyBaudrate = int(baudrate)

        with error_check(exception_type=CanInitializationError):
            self.serialPort = serial.serial_for_url(
                port,
                baudrate=ttyBaudrate,
                rtscts=rtscts,
                timeout=timeout,
            )
        self.rx_ctrl_queue = queue.Queue(10)
        self.rx_msg_queue = queue.Queue(10000)
        self._stop_event = threading.Event()
        self._stop_event.clear()
        self.rx_thread = threading.Thread(target=self._rxWorker)
        self.rx_thread.start()

    def _rxWorker(self):
        self._buffer = bytearray()
        wait_len = 6
        n = 0
        with error_check("Could not read from serial device"):
            while True:
                if self._stop_event.is_set():
                    return
                new_byte = self.serialPort.read(size=1)
                if new_byte:
                    if n == 0 and new_byte[0] == 0:
                        continue
                    self._buffer.extend(new_byte)
                    n += 1
                    
                    if n == 1:  #first symbol got. Header len need be set
                        if self._buffer[0] == Command.MESSAGE:
                            wait_len = 6
                        else:
                            wait_len = 4

                    if n == wait_len:   #header got, check if we must wait data...
                        if wait_len == 4:   #command header, add data len
                            dSize = 0
                            if self._buffer[0] != Command.SYNC_ANSWER:
                                #sync frame has different format and can't have data
                                dSize = self._buffer[-1]
                                wait_len += dSize
                        elif wait_len == 6: #data header, add data len
                            dSize = struct.unpack("<xxxxH", self._buffer)[0]
                            wait_len += dSize
                        else: #if waitLen not equal 4 nor 6, we've got full packet
                            if len(self._buffer) != dSize + 6:
                                logger.warning('<- ERR: ' + self._buffer.hex(sep=' ').upper())
                                logger.warning('Wait len: ' + str(wait_len))
                            res = bytes(self._buffer)
                            self._buffer.clear()
                            n = 0
                            if res[0] == Command.MESSAGE:
                                logger.log(TRANSPORT_LOGGING_LEVEL, 'MSG <- ' + res.hex(sep=' ').upper())
                                self.rx_msg_queue.put_nowait(res)
                            else:
                                logger.log(TRANSPORT_LOGGING_LEVEL, 'CTRL <- ' + res.hex(sep=' ').upper())
                                self.rx_ctrl_queue.put_nowait(res)
                            continue
                        
                        if dSize == 0: #in case of header with 0 data len
                            res = bytes(self._buffer)
                            self._buffer.clear()
                            n = 0
                            if res[0] == Command.MESSAGE:
                                logger.log(TRANSPORT_LOGGING_LEVEL, 'MSG <- ' + res.hex(sep=' ').upper())
                                self.rx_msg_queue.put_nowait(res)
                            else:
                                logger.log(TRANSPORT_LOGGING_LEVEL, 'CTRL <- ' + res.hex(sep=' ').upper())
                                self.rx_ctrl_queue.put_nowait(res)
            

    def read_ctrl(self, timeout: Optional[float]) -> Optional[str]:
            try:
                res = self.rx_ctrl_queue.get(timeout=timeout)
            except queue.Empty:
                return None
            return res
    
    def read_msg(self, timeout: Optional[float]) -> Optional[str]:
            try:
                res = self.rx_msg_queue.get(timeout=timeout)
            except queue.Empty:
                return None
            return res
    
    def write(self, rawData: bytes) -> None:
        logger.log(TRANSPORT_LOGGING_LEVEL, '-> ' + rawData.hex(sep=' ').upper())
        with error_check("Could not write to serial device"):
            self.serialPort.write(rawData)
            self.serialPort.flush()

    def _flush(self) -> None:
        pass

    def close_port(self):
        self._stop_event.set()
        self.rx_thread.join()
        with error_check("Could not close serial port"):
            self.serialPort.close()