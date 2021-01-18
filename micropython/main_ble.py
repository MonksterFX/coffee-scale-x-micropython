from utime import sleep_us
from micropython import const
from ble_advertising import advertising_payload
import bluetooth
import time

# import BLE handler
from BLEx import BLEx
bt = bluetooth.BLE()
ble = BLEx(bt, "Coffee ScaleX")

limit = 100


def on_rx():
    # handling goes here
    print('got', ble.read().decode().strip())


# register listener for write
ble.onRecive(on_rx)

n = 0

while True:
    # how to build structs https://forum.micropython.org/viewtopic.php?t=7114
    ble.send(str(n))
    n = (n + 1) % 100
    print("send", n)
    time.sleep(5)
