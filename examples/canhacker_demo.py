from can.interfaces.canhacker import canHacker
from can import Message
import logging
import time

logging.basicConfig(level=logging.DEBUG)
filters = [
    {"can_id": 0x738, "can_mask": 0x7FF, "extended": False},
    {"can_id": 0x0, "can_mask": 0x0, "extended": False}
           ]
bus = canHacker('COM3@115200', bitrate=500000, can_filters=filters)

msg = Message(is_extended_id = False)
bus.send(msg)

n = 0
while n < 30:
    rx_msg = bus.recv(1.0)
    if rx_msg == None:
        break
    n += 1
    print("Time: {t:d} ID: {id:X} DLC: {dlc:d} Data: [{data}]".format(t=rx_msg.timestamp, id=rx_msg.arbitration_id, dlc=rx_msg.dlc, data=rx_msg.data.hex(' ').upper()))

time.sleep(3)
    
bus.shutdown()
           
   # ...
