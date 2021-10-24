
import RPi.GPIO as GPIO
import json

from time import time

from .common import cache
from .mqtt import mqtt


class Door:
    but1 = 17  # open button
    but2 = 18  # close button
    wayPin = 27  # way pin

    bounce_up = None
    bounce_down = None

    def setup(self):
        # setting up
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.but1, GPIO.IN)
        GPIO.setup(self.but2, GPIO.IN)
        GPIO.setup(self.wayPin, GPIO.OUT)
        GPIO.output(self.wayPin, GPIO.LOW)  # Default to Close
        cache.set("direction_wanted", 'Closing')

    def open(self):
        print('Open button!', flush=True)
        GPIO.output(self.wayPin, GPIO.HIGH)
        cache.set("direction_wanted", 'Opening')
        self.publish_state()

    def close(self):
        print('Close button!', flush=True)
        GPIO.output(self.wayPin, GPIO.LOW)
        cache.set("direction_wanted", 'Closing')
        self.publish_state()

    def button_open_callback(self, channel):
        print('Open button callback!', flush=True)

        if self.bounce_up is None:
            print('Bounce_up is None', flush=True)
            self.bounce_up = time()
            return
        elif time() - self.bounce_up > 1.0:
            print('Bounce_up is > 1000 ({})'.format(time() - self.bounce_up), flush=True)
            self.bounce_up = time()
            return
        elif time() - self.bounce_up < 0.5:
            print('Bounce_up is < 500 ({})'.format(time() - self.bounce_up), flush=True)
            return

        print('Bounce_up is {} -> Opening'.format(time() - self.bounce_up), flush=True)
        self.bounce_up = None
        self.open()
        self.publish_override()

    def button_close_callback(self, channel):
        print('Close button callback!', flush=True)

        if self.bounce_down is None:
            print('Bounce_down is None', flush=True)
            self.bounce_down = time()
            return
        elif time() - self.bounce_down > 1.0:
            print('Bounce_down is > 1000 ({})'.format(time() - self.bounce_down), flush=True)
            self.bounce_down = time()
            return
        elif time() - self.bounce_down < 0.5:
            print('Bounce_down is < 500 ({})'.format(time() - self.bounce_down), flush=True)
            return

        print('Bounce_down is {} -> Closing'.format(time() - self.bounce_down), flush=True)
        self.bounce_down = None
        self.close()
        self.publish_override()

    def register_events(self):
        GPIO.add_event_detect(self.but1, GPIO.RISING,
                              callback=self.button_open_callback, bouncetime=500)
        GPIO.add_event_detect(self.but2, GPIO.RISING,
                              callback=self.button_close_callback, bouncetime=500)

    def remove_events(self):
        GPIO.remove_event_detect(self.but1)
        GPIO.remove_event_detect(self.but2)

    def publish_state(self):
        data = cache.get_dict("temperature", "sensor_open", "sensor_close", "completed_steps",
                              "remaining_steps", "direction_wanted", "direction", "sleeping", "override", "uptime")
        # print("publish: {}".format(data))
        mqtt.publish('chicken-coop/tele/STATE', json.dumps(data))

    def publish_override(self, enable=True):
        # print("publish: {}".format(data))
        mqtt.publish('chicken-coop/cmnd/OVERRIDE', enable)


door = Door()
