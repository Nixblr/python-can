import struct
from can import Message
import logging

logger = logging.getLogger(__name__)

#channels 
class Channel:
    CH1 =  0x20
    CH2 =  0x40
    CH3 =  0x60
    CH4 =  0x80
    CH5 =  0xA0
    CH6 =  0xC0
    CH7 =  0xE0

class Command:
    SYNC = 0xA5
    SYNC_ANSWER = 0x5A
    DEVICE_HW = 0x05
    DEVICE_INFO = 0x01
    DEVICE_FIRMWARE = 0x02
    DEVICE_SERIAL = 0x03
    DEVICE_MODE = 0x04
    DEVICE_OPEN = 0x08
    DEVICE_CLOSE = 0x09
    DEVICE_STAT = 0x0a
    CHANNEL_CONFIG = 0x11
    CHANNEL_OPEN = 0x18
    CHANNEL_CLOSE = 0x19
    CHANNEL_RESET = 0x1f
    FILTER_SET = 0x21
    FILTER_CLEAR = 0x22
    GATEWAY_ON = 0x31
    GATEWAY_OFF = 0x32
    GATEWAY_FILTER_SET = 0x33
    GATEWAY_FILTER_CLEAR = 0x34
    GATEWAY_ALL_CLEAR = 0x35
    MESSAGE = 0x40
    SLAVE_LIN_RESPONSE_SET = 0x4a
    SLAVE_LIN_RESPONSE_MODE = 0x4b
    BUS_ERROR = 0x48
    COMMAND_ERROR = 0xff

class FlagDeviceModes:
    FLAG_DEVICE_MODE_FULL = 0x00
    FLAG_DEVICE_MODE_CAN = 0x01
    FLAG_DEVICE_MODE_LIN = 0x02

class FlagChannelConfig:
    FLAG_CONFIG_BUS_SPEED = 0x00
    FLAG_CONFIG_BUS_SPEED_FD = 0x01
    FLAG_CONFIG_BUS_SPEED_M = 0x02
    FLAG_CONFIG_BUS_SPEED_FD_M = 0x03
    FLAG_CONFIG_TERMINATOR = 0x05
    FLAG_CONFIG_PULL_UP = 0x06
    FLAG_CONFIG_CRC_MODE = 0x07
    FLAG_CONFIG_IDLE_DELAY = 0x08
    FLAG_CONFIG_MODE = 0x09
    FLAG_CONFIG_CAN_FRAME = 0x0A

class nominalCanFDBitrate:
    NOMINAL_BITRATE_10K = 0x00
    NOMINAL_BITRATE_20K = 0x01
    NOMINAL_BITRATE_33_3K = 0x02
    NOMINAL_BITRATE_50K = 0x03
    NOMINAL_BITRATE_62_5K = 0x04
    NOMINAL_BITRATE_83_3K = 0x05
    NOMINAL_BITRATE_95_2K = 0x06
    NOMINAL_BITRATE_100K = 0x07
    NOMINAL_BITRATE_125K = 0x08
    NOMINAL_BITRATE_250K = 0x09
    NOMINAL_BITRATE_400K = 0x0a
    NOMINAL_BITRATE_500K = 0x0b
    NOMINAL_BITRATE_800K = 0x0c
    NOMINAL_BITRATE_1000K = 0x0d

class canBitrate:
    CAN_BITRATE_10K = 0x00
    CAN_BITRATE_20K = 0x01
    CAN_BITRATE_33_3K = 0x02
    CAN_BITRATE_50K = 0x03
    CAN_BITRATE_62_5K = 0x04
    CAN_BITRATE_83_3K = 0x05
    CAN_BITRATE_95K = 0x06
    CAN_BITRATE_100K = 0x07
    CAN_BITRATE_125K = 0x08
    CAN_BITRATE_250K = 0x09
    CAN_BITRATE_400K = 0x0a
    CAN_BITRATE_500K = 0x0b
    CAN_BITRATE_800K = 0x0c
    CAN_BITRATE_1000K = 0x0d
    codes = {
        10000: 0x00,
        20000: 0x01,
        33300: 0x02,
        50000: 0x03,
        62500: 0x04,
        83300: 0x05,
        95000: 0x06,
        100000: 0x07,
        125000: 0x08,
        250000: 0x09,
        400000: 0x0a,
        500000: 0x0b,
        800000: 0x0c,
        1000000: 0x0d
        }

class CHANNEL_MODES:
    MODE_NORMAL = 0x00
    MODE_LISTEN = 0x01
    MODE_LOOPBACK = 0x02

class FLAG_MESSAGE_CHANNELS:
    FLAG_MESSAGE_CHANNEL_1 = 0x2000
    FLAG_MESSAGE_CHANNEL_2 = 0x4000
    FLAG_MESSAGE_CHANNEL_3 = 0x6000
    FLAG_MESSAGE_CHANNEL_4 = 0x8000
    FLAG_MESSAGE_CHANNEL_5 = 0xA000
    FLAG_MESSAGE_CHANNEL_6 = 0xC000
    FLAG_MESSAGE_CHANNEL_7 = 0xE000

    FLAG_MESSAGE_CONFIRM_REQUIRED = 0x0001

    # 29-bit message identifier
    FLAG_MESSAGE_EXTID = 0x00000001
    # Remote frame
    FLAG_MESSAGE_RTR = 0x00000002
    # CAN-FD frame
    FLAG_MESSAGE_FDF = 0x00000004
    # CAN-FD bit rate switch
    FLAG_MESSAGE_BRS = 0x00000008
    # CAN-FD Error status indicator
    FLAG_MESSAGE_ESI = 0x00000010
    # Block TX
    FLAG_MESSAGE_BLOCK_TX = 0x30000000

class FLAG_FILTER_TYPE:
    FLAG_FILTER_TYPE_11BIT = 0x00
    FLAG_FILTER_TYPE_29BIT = 0x01

class HWId:
    # Old identifier for CAN-Hacker on F105 mcu with dual CAN channels and single LIN channel */
    HW_CH30 = 0xFF
    # Old identifier for CAN-Hacker in ODB interface with single CAN channel and single LIN channel */
    HW_ODB_OLD = 0x02
    # CAN-Hacker 3.2 on F105 mcu with dual CAN channels and single LIN channel */
    HW_CH32 = 0x01
    # CAN-Hacker in ODB interface on F105 mcu with single CAN channel and single LIN channel */
    HW_ODB = 0x04
    # CAN-Hacker CH-P on F105 mcu with dual CAN channels and single LIN channel */
    HW_CHP = 0x03
    # CAN-Hacker 3.3 on F407 mcu with dual CAN channels and single LIN channel */
    HW_CH33 = 0x11
    # CAN-Hacker CH-P on F407 mcu with dual CAN channels and single LIN channel */
    HW_CHPM03 = 0x13
    # CAN-Hacker in ODB interface on G431 mcu with single CAN channel and single LIN channel */
    HW_ODB_FD = 0x14
    # CAN-Hacker CH-P on G473 mcu with dual CAN channels and single LIN channel */
    HW_FDL2 = 0x06
    textNames = {
        0xFF : "CAN-Hacker on F105 mcu with dual CAN channels and single LIN channel (Old Id)",
        0x02 : "CAN-Hacker in ODB interface with single CAN channel and single LIN channel (Old Id)",
        0x01 : "CAN-Hacker 3.2 on F105 mcu with dual CAN channels and single LIN channel",
        0x04 : "CAN-Hacker in ODB interface on F105 mcu with single CAN channel and single LIN channel",
        0x03 : "CAN-Hacker CH-P on F105 mcu with dual CAN channels and single LIN channel",
        0x11 : "CAN-Hacker 3.3 on F407 mcu with dual CAN channels and single LIN channel",
        0x13 : "CAN-Hacker CH-P on F407 mcu with dual CAN channels and single LIN channel",
        0x14 : "CAN-Hacker in ODB interface on G431 mcu with single CAN channel and single LIN channel",
        0x06 : "CAN-Hacker CH-P on G473 mcu with dual CAN channels and single LIN channel"
    }

class CmdType:
    CONTROL = 0
    DATA = 1

class HeaderDirection:
    TX = 0
    RX = 1

class MsgHeader:
    def __init__(self, dir: int, inputData: bytes = None) -> None:
        if dir  != HeaderDirection.TX and dir != HeaderDirection.RX:
            raise ValueError("Incorrect direction argument")
        self.dir = dir
        self.sequence = 0
        if dir == HeaderDirection.RX and inputData is not None and len(inputData) > 0:
            self.parse(inputData)

    def getBytes(self,
                 command: int,
                 flags: int = 0,
                 dSize: int = 0) -> bytes:
        if self.dir != HeaderDirection.TX:
            raise Exception("getByte() can be only be called for TX frame.")
        if command < 1 or command > 0x7f and command != Command.SYNC:
            raise ValueError("Command must be in range: 0x01..0x7f")
        #sync - non standard command, so process it separatly...
        if command == Command.SYNC:
            self.sequence = 0 #set sequence counter to zero, when sync
            return(bytes([Command.SYNC, 0x00, Command.SYNC, 0x00]))
        seq = self.sequence
        self.sequence += 1
        self.sequence &= 0xff
        if command == Command.MESSAGE: 
            return struct.pack("<BBhh", command, seq, flags, dSize)
        else:
            return struct.pack("<BBBB", command, seq, flags, dSize)

    def sequenceReset(self) -> None:
        self.sequence = 0

    def parse(self,
              inputData: bytes) -> None:
        if self.dir != HeaderDirection.RX:
            raise Exception("getByte() can be only be called for RX frame.")
        if False:
            raise Exception("Input data too short")
        if inputData[0] == 0:
            raise Exception("Input data is started from zero.")
        if inputData[0] == 0x40:
            if len(inputData) < 6:
                raise Exception("Input data is too short.")
            unpackedInput = struct.unpack("<BBhh", inputData[:6])
            self.headerLen = 6
        else:
            if len(inputData) < 4:
                raise Exception("Input data is too short.")
            unpackedInput = struct.unpack("<BBBB", inputData[:4])
            self.headerLen = 4
        self.Command = unpackedInput[0]
        self.sequence = unpackedInput[1]
        self.flags = unpackedInput[2]
        self.dLen = unpackedInput[3]
        self.isPositiveAnswer = False
        if self.Command != Command.COMMAND_ERROR:
            if self.Command & 0x80 != 0:
                self.isPositiveAnswer = True
            self.Command &= 0x7f

class CanHackerMessage:
    def __init__(self, dir: int, inputData: bytes = None) -> None:
        self.Header = MsgHeader(dir)
        self.direction = dir
        self.isParsed = False
        if dir == HeaderDirection.RX and inputData is not None:
            if len(inputData) >= 4:
                self.parse(inputData)
            else:
                raise Exception("InputData too short.")
    

    def assembly(self,
                 command: int,
                 flags: int = 0,
                 dSize: int = 0,
                 data: bytes = bytes()) -> bytes:
        if self.direction != HeaderDirection.TX:
            raise Exception("assembly() can be only be called for TX message.")
        if type(data) != bytes:
            raise TypeError("data has incorrect type.")
        headerBytes = self.Header.getBytes(command, flags, dSize)
        if dSize == 0:
            return headerBytes
        else:
            return headerBytes + data
    
    def parse(self, inputData: bytes) -> None:
        self.Header = MsgHeader(HeaderDirection.RX, inputData)

        #Command types decode

        if self.Header.Command == Command.SYNC_ANSWER:
            if inputData[1] == 0 and inputData[2] == 0x5a and inputData[3] == 0:
                self.isSyncOk = True
            else:
                self.isSyncOk = False

        elif self.Header.Command == Command.DEVICE_HW:
            self.hardware = inputData[self.Header.headerLen]
            if self.hardware in HWId.textNames:
                self.hardwareString = HWId[self.hardware]
            else:
                self.hardwareString = "Unknown hardware"
        
        elif self.Header.Command == Command.DEVICE_INFO:
            self.info = inputData[self.Header.headerLen : self.Header.headerLen + self.Header.dLen].decode("ascii")

        elif self.Header.Command == Command.DEVICE_FIRMWARE:
            self.firmware = inputData[self.Header.headerLen : self.Header.headerLen + self.Header.dLen].decode("ascii")

        elif self.Header.Command == Command.MESSAGE:
            self.channel = self.Header.flags
            payload = inputData[self.Header.headerLen:]
            msgBody = struct.unpack("<IIIIH", payload[:18])
            #print('<- $' + inputData.hex(sep=' ').upper())
            #print('PL: ' + payload.hex(sep=' ').upper())
            self.msg = Message(
                arbitration_id = msgBody[3],
                is_extended_id = msgBody[0] & FLAG_MESSAGE_CHANNELS.FLAG_MESSAGE_EXTID != 0,
                timestamp = msgBody[1],
                is_remote_frame = msgBody[0] & FLAG_MESSAGE_CHANNELS.FLAG_MESSAGE_RTR != 0,
                dlc= msgBody[4],
                data=payload[18:],
            )
            if self.msg.dlc != len(self.msg.data):
                es = " ERR"
                self.isERR = True
            else:
                es = ""
                self.isERR = False
            #print("ID: " + hex(self.msg.arbitration_id) + " DLC: " + hex(self.msg.dlc) + " D: " + self.msg.data.hex(sep=" ").upper() + es)

        self.isParsed = True