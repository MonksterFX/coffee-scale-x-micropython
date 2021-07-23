
# advertisment PDU type
# https://www.bluetooth.com/blog/bluetooth-low-energy-it-starts-with-advertising/
# https://www.argenox.com/a-ble-advertising-primer/
SHORT_LOCAL_NAME = 0x08
COMPLETE_LOCAL_NAME = 0x09


def connected(self):
    self.timer1.deinit()
    self.timer2.deinit()


def disconnected(self):
    self.timer1.init(period=1000, mode=Timer.PERIODIC,
                     callback=lambda t: self.led(1))
    sleep_ms(200)
    self.timer2.init(period=1000, mode=Timer.PERIODIC,
                     callback=lambda t: self.led(0))
