import time
from utime import sleep_us
from machine import Pin
from scale import Scales
from ble import sendData, activateBLE

blue = Pin(2, Pin.OUT)

# top scales
t_scale1 = Scales(5, 22)
t_scale2 = Scales(18, 22)
t_calibration_factor = 2.32

# bottom scales
b_scale1 = Scales(19, 22)
b_scale2 = Scales(21, 22)

# calibration
t_calibration_factor = 2.32
b_calibration_factor = 2.27

# initialization
_scales = [t_scale1, t_scale2, b_scale1, b_scale2]

# set channel
for scale in _scales:
    scale.channel = Scales.CHANNEL_A_64

print('init: set channel successfully')

time.sleep(1)

# tare


def tare():
    for x in range(4):
        sleep_us(100000)
        for scale in _scales:
            scale.tare()


tare()
print('init: tare')

activateBLE(tare)
print('init: BLE activated')

# TODO:Timer while connecting
blue.on()
time.sleep(1)
blue.off()

SERIAL_DEBUG_FRAC = 10
MEASUREMENTS_PER_SECOND = 1
MEASUREMENTS_DELAY = 1000000  # int(1000000/MEASUREMENTS_PER_SECOND)

serial_run = 1

while True:
    sleep_us(MEASUREMENTS_DELAY)

    # measure top
    ts1_value = t_scale1.raw_value()
    ts2_value = t_scale2.raw_value()

    # measure bottom
    bs1_value = b_scale1.raw_value()
    bs2_value = b_scale2.raw_value()

    if(serial_run % SERIAL_DEBUG_FRAC == 0):
        print('data:t:' + str((ts1_value + ts2_value) * t_calibration_factor / 1000))
        print('data:b:' + str((bs1_value + bs2_value) * b_calibration_factor / 1000))
        serial_run = 0

    try:
        # send ble data
        sendData(
            (ts1_value + ts2_value) * t_calibration_factor / 1000,
            (bs1_value + bs2_value) * b_calibration_factor / 1000
        )
    except Exception as e:
        import sys
        from uio import StringIO

        s = StringIO()
        sys.print_exception(e, s)

        print("an error occured \n " + s.getvalue())

        pass

    serial_run += 1
