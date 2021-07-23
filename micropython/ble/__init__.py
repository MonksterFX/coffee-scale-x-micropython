# micropython modules
import ubluetooth
import time
import struct
from utime import sleep_us, ticks_ms
from micropython import const

# custom modules
from .BLEx import BLEx

# init BLE
bt = ubluetooth.BLE()
ble = BLEx(bt)
_on_tare = None


def activateBLE(on_tare):
    # register listener for write
    global _on_tare
    _on_tare = on_tare

    ble.onRecive(on_rx)
    print('init: listing for commands')


def on_rx():
    # defines messages
    CMD_TYPES = {
        0XC0: "TARE",
        0XC1: "START",
        0XC2: "STOP",
        0xC3: "CALIBRATION"
    }

    # read bytes
    msg = ble.read()

    # CMD - 2 BYTES
    # 1 byte COMMAND - see CMD ENUM
    # 1 byte EXTRA - set to 0x00
    cmd = msg[0]
    extra = msg[1]  # only important for calibaration

    # TODO: react to commands
    print('irq -> command received - ', CMD_TYPES.get(cmd))

    if CMD_TYPES.get(cmd) == "TARE":
        if _on_tare:
            _on_tare()


def sendData(topScale, bottomScale):
    # how to build structs https://forum.micropython.org/viewtopic.php?t=7114

    # create message 12 byte
    # 1 byte Datatype: 0xD0 - Data
    # 4 byte Timestamp: '>I' usignt int - ms since start (if rtc not available)
    # 4 byte Scale Top: '>f' signed float - gramms
    # 4 byte Scale Bottom: '>f' signed float - gramms
    # 1 byte stop byte: 0xFF - Not used

    msg = bytearray(14)
    msg[0] = 0xD0
    struct.pack_into('>I', msg, 1, ticks_ms())
    struct.pack_into('>f', msg, 5, topScale)
    struct.pack_into('>f', msg, 9, bottomScale)
    msg[-1] = 0xFF

    # send message
    ble.send(msg)

    # print('ble: msg send')
    # print("send || ", ':'.join(['{:02x}'.format(b) for b in msg]))
