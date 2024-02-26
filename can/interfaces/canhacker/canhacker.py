"""
Interface for CanHacker.com Adapters
"""

import io
import logging
import time
from typing import Any, Optional, Tuple

from can import BusABC, CanProtocol, Message, typechecking
from .transport import Transport

from can.exceptions import (
    CanInitializationError,
    CanInterfaceNotImplementedError,
    CanOperationError,
    error_check,
)

from can.typechecking import CanFilters

from .message import *

logger = logging.getLogger(__name__)

try:
    import serial
except ImportError:
    logger.warning(
        "You won't be able to use the slcan can backend without "
        "the serial module installed!"
    )
    serial = None


class canHacker(BusABC):
    """
    CanHacker interface
    """
    _SLEEP_AFTER_SERIAL_OPEN = 2  # in seconds

    def __init__(
        self,
        port: typechecking.ChannelStr,
        ttyBaudrate: int = 115200,
        bitrate: Optional[int] = None,
        btr: Optional[str] = None,
        sleep_after_open: float = _SLEEP_AFTER_SERIAL_OPEN,
        rtscts: bool = False,
        timeout: float = 0.001,
        **kwargs: Any,
    ) -> None:
        """
        :param str port:
            port of underlying serial or usb device (e.g. ``/dev/ttyUSB0``, ``COM8``, ...)
            Must not be empty. Can also end with ``@115200`` (or similarly) to specify the baudrate.
        :param int ttyBaudrate:
            baudrate of underlying serial or usb device (Ignored if set via the ``channel`` parameter)
        :param bitrate:
            Bitrate in bit/s
        :param btr:
            BTR register value to set custom can speed
        :param poll_interval:
            Poll interval in seconds when reading messages
        :param sleep_after_open:
            Time to wait in seconds after opening serial connection
        :param rtscts:
            turn hardware handshake (RTS/CTS) on and off
        :param timeout:
            Timeout for the serial or usb device in seconds (default 0.001)
        :raise ValueError: if both ``bitrate`` and ``btr`` are set or the channel is invalid
        :raise CanInterfaceNotImplementedError: if the serial module is missing
        :raise CanInitializationError: if the underlying serial connection could not be established
        """

        self.transport = Transport(port, ttyBaudrate, bitrate, btr, rtscts, timeout, **kwargs)
        self._can_protocol = CanProtocol.CAN_20
        self.TxMsg = CanHackerMessage(HeaderDirection.TX)

        with error_check(exception_type=CanInitializationError):
            if self.sync() != True:
                raise Exception("Syncronisation error.")
            self._deviceOpen()
            if bitrate is not None and btr is not None:
                raise ValueError("Bitrate and btr mutually exclusive.")
            if bitrate is not None:
                self.set_bitrate(bitrate)
            if btr is not None:
                self.set_bitrate_reg(btr)
            self._set_mode(CHANNEL_MODES.MODE_NORMAL)
            self.open()

        super().__init__(
            port,
            ttyBaudrate=115200,
            bitrate=None,
            rtscts=False,
            **kwargs,
        )

    def set_bitrate(self, bitrate: int) -> None:
        """
        :param bitrate:
            Bitrate in bit/s

        :raise ValueError: if ``bitrate`` is not among the possible values
        """
        if bitrate in canBitrate.codes:
            bitrate_code = canBitrate.codes[bitrate]
        else:
            bitrates = ", ".join(str(k) for k in canBitrate.codes.keys())
            raise ValueError(f"Invalid bitrate, choose one of {bitrates}.")
        flag = Channel.CH1 | FlagChannelConfig.FLAG_CONFIG_BUS_SPEED
        raw = self.TxMsg.assembly(Command.CHANNEL_CONFIG, flag, 1, bytes([bitrate_code]))
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.CHANNEL_CONFIG or rx.Header.isPositiveAnswer == False:
            raise Exception("Bitrate set error.")

    def _set_mode(self, mode: int) -> None:
        """
        :param mode:
            mode

        :raise ValueError: ---
        """
        if mode not in (CHANNEL_MODES.MODE_LISTEN, CHANNEL_MODES.MODE_LOOPBACK, CHANNEL_MODES.MODE_NORMAL):
            raise ValueError(f"Invalid mode code.")
        flag = Channel.CH1 | FlagChannelConfig.FLAG_CONFIG_MODE
        raw = self.TxMsg.assembly(Command.CHANNEL_CONFIG, flag, 1, bytes([mode]))
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.CHANNEL_CONFIG or rx.Header.isPositiveAnswer == False:
            raise Exception("Bitrate set error.")

    def set_bitrate_reg(self, btr: str) -> None:
        """
        :param btr:
            BTR register value to set custom can speed
        """
        raise NotImplemented

    def sync(self) -> bool:
        raw = self.TxMsg.assembly(Command.SYNC)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.isParsed == False:
            return False
        if rx.Header.Command == Command.SYNC_ANSWER:
            if rx.isSyncOk == True:
                return True
        return False
    
    def _deviceOpen(self) -> None:
        raw = self.TxMsg.assembly(Command.DEVICE_OPEN)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.DEVICE_OPEN or rx.Header.isPositiveAnswer == False:
            raise Exception("Device open error.")
        
    def _deviceClose(self) -> None:
        raw = self.TxMsg.assembly(Command.DEVICE_OPEN)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.DEVICE_OPEN or rx.Header.isPositiveAnswer == False:
            raise Exception("Device close error.")

    def open(self) -> None:
        raw = self.TxMsg.assembly(Command.CHANNEL_OPEN, Channel.CH1)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.CHANNEL_OPEN or rx.Header.isPositiveAnswer == False:
            raise Exception("Channel open error.")

    def close(self) -> None:
        raw = self.TxMsg.assembly(Command.CHANNEL_CLOSE, Channel.CH1)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.CHANNEL_CLOSE or rx.Header.isPositiveAnswer == False:
            raise Exception("Channel close error.")

    def _recv_internal(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[Message], bool]:
        input_raw = self.transport.read_msg(timeout)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if hasattr(rx, 'msg'):
            if rx.isERR == True:
                logger.warning("ERR FRM: " + input_raw.hex(" "))
            return rx.msg, True
        return None, False

    def send(self, msg: Message, timeout: Optional[float] = None) -> None:
        # if timeout != self.transport.serialPort.write_timeout:
        #    self.transport.serialPort.write_timeout = timeout
        flags = 0
        if msg.is_remote_frame:
            flags += FLAG_MESSAGE_CHANNELS.FLAG_MESSAGE_RTR
        if msg.is_extended_id:
            flags += FLAG_MESSAGE_CHANNELS.FLAG_MESSAGE_EXTID
        messageData = struct.pack("<IIH", flags, msg.arbitration_id, msg.dlc) + msg.data
        raw = self.TxMsg.assembly(Command.MESSAGE, FLAG_MESSAGE_CHANNELS.FLAG_MESSAGE_CHANNEL_1, len(messageData), messageData)
        self.transport.write(raw)

    def shutdown(self) -> None:
        super().shutdown()
        self.close()
        self.transport.close_port()

    def fileno(self) -> int:
        try:
            return self.serialPortOrig.fileno()
        except io.UnsupportedOperation:
            raise NotImplementedError(
                "fileno is not implemented using current CAN bus on this platform"
            )
        except Exception as exception:
            raise CanOperationError("Cannot fetch fileno") from exception

    def get_version(
        self, timeout: Optional[float]
    ) -> Tuple[Optional[int], Optional[int]]:
        """Get HW and SW version of the canHacker interface.

        :param timeout:
            seconds to wait for version or None to wait indefinitely

        :returns: tuple (hw_version, sw_version)
            WHERE
            int hw_version is the hardware version or None on timeout
            int sw_version is the software version or None on timeout
        """
        raise NotImplemented
        return None, None

    def get_serial_number(self, timeout: Optional[float]) -> Optional[str]:
        """Get serial number of the canHacker interface.

        :param timeout:
            seconds to wait for serial number or :obj:`None` to wait indefinitely

        :return:
            :obj:`None` on timeout or a :class:`str` object.
        """
        raise NotImplemented
        return None
    
    def _set_filter(self, number, filter) -> None:
        """Set filter internal command"""
        if filter['extended'] == True:
            typeStr = "extended (29 bit)"
            type = FLAG_FILTER_TYPE.FLAG_FILTER_TYPE_29BIT
        else:
            typeStr = "standard (11 bit)"
            type = FLAG_FILTER_TYPE.FLAG_FILTER_TYPE_11BIT
        logger.debug("Set filter " + str(number) + ": Id: " + hex(filter['can_id']) + " Mask: "+ hex(filter['can_mask']) + " Type: " + typeStr)
        filterData = struct.pack("<IIII", number, type, filter['can_id'], filter['can_mask'])
        raw = self.TxMsg.assembly(Command.FILTER_SET, Channel.CH1, len(filterData), filterData)
        self.transport.write(raw)
        input_raw = self.transport.read_ctrl(0.5)
        rx = CanHackerMessage(HeaderDirection.RX, input_raw)
        if rx.Header.Command != Command.FILTER_SET or rx.Header.isPositiveAnswer == False:
            raise Exception("Filter set error.")
    
    def _apply_filters(self, filters: Optional[CanFilters]) -> None:
        if filters == None:
            return
        n = 0
        for filt in filters:
            self._set_filter(n, filt)
            n += 1
