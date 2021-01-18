import time
from utime import sleep_us
from hx711 import HX711
from machine import Pin
from scale import Scales

blue = Pin(2, Pin.OUT)

# top scales
t_scale1 = Scales(5, 22)
t_scale2 = Scales(18, 22)
t_calibration_factor = 2.32


# bottom scales
b_scale1 = Scales(19, 22)
b_scale2 = Scales(21, 22)
b_calibration_factor = 2.27

_scales = [t_scale1, t_scale2, b_scale1, b_scale2]

# tare
blue.on()
time.sleep(1)
blue.off()

# set channel
for scale in _scales:
    scale.channel = Scales.CHANNEL_A_64

time.sleep(1)

# tare
for scale in _scales:
    scale.tare() 

while True:
    sleep_us(10000)

    # measure top
    ts1_value = t_scale1.raw_value()
    ts2_value = t_scale2.raw_value()
    print('data:t:' + str((ts1_value + ts2_value) * t_calibration_factor / 1000))

    # measure bottom
    bs1_value = b_scale1.raw_value()
    bs2_value = b_scale2.raw_value()
    print('data:b:' + str((bs1_value + bs2_value) * b_calibration_factor / 1000))