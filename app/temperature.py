
import glob

from statistics import mean

from .common import cache


class Temperature:

    def read(self):
        devices = glob.glob("/sys/bus/w1/devices/28*/temperature")
        temperatures = []
        for device in devices:
            with open(device) as f:
                t = f.read()
                if t is not '':
                    temperatures.append(int(t) / 1000.0)
        avg = round(mean(temperatures), 1)
        cache.set("temperature", avg)
        return avg


temperature = Temperature()
