from .hx711 import HX711
from utime import sleep_us


class Scales(HX711):
    def __init__(self, d_out, pd_sck):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = 0

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=5, delay_us=500):
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        return self._stabilizer(values)

    @staticmethod
    def _stabilizer(values, deviation=10):
        return sum(values)/len(values)
        # weights = []
        # for prev in values:
        #     # devision by zero protection
        #     if prev == 0:
        #         continue
        #     weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        # return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
