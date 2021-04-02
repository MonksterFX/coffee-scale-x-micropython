from utime import sleep_us, ticks_ms
from micropython import const
from ble_advertising import advertising_payload
import bluetooth
import time
import struct

# import BLE handler
from BLEx import BLEx
bt = bluetooth.BLE()
ble = BLEx(bt, "Coffee ScaleX")

limit = 100

# rx handling goes here
def on_rx():
    
    CMD_TYPES = {
        0XC0:"TARE",
        0XC1:"START",
        0XC2:"STOP",
        0xC3:"CALIBRATION"
    }

    # read bytes
    msg = ble.read()

    # CMD - 2 BYTES
    # 1 byte COMMAND - see CMD ENUM
    # 1 byte EXTRA - set to 0x00
    cmd = msg[0]
    extra = msg[1] # only important for calibaration

    print('got', msg, CMD_TYPES.get(cmd))


# register listener for write
ble.onRecive(on_rx)

n = 0

while True:
    # how to build structs https://forum.micropython.org/viewtopic.php?t=7114
    
    # create message 12 byte
    # 1 byte Datatype: 0xD0 - Data 
    # 4 byte Timestamp: '>I' usignt int - ms since start (if rtc not available) 
    # 4 byte Scale Top: '>f' signed float - gramms
    # 4 byte Scale Top: '>f' signed float - gramms
    # 1 byte stop byte: 0xFF - Not used

    msg = bytearray(14)
    msg[0] = 0xD0
    msg[-1] = 0xFF
    struct.pack_into('>I', msg, 1, ticks_ms())
    struct.pack_into('>f', msg, 5, n * 1.001)
    struct.pack_into('>f', msg, 9, n * -1.001)
    ble.send(msg)
    n = (n + 1) % 100
    print("send || ", ':'.join(['{:02x}'.format(b) for b in msg]))
    time.sleep(1)
