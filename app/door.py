
import RPi.GPIO as GPIO
import json

from .common import cache
from .mqtt import mqtt


class Door:
    but1 = 17  # open button
    but2 = 18  # close button
    wayPin = 27  # way pin

    def setup(self):
        # setting up
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.but1, GPIO.IN)
        GPIO.setup(self.but2, GPIO.IN)
        GPIO.setup(self.wayPin, GPIO.OUT)
        GPIO.output(self.wayPin, GPIO.LOW)  # Default to Close
        cache.set("direction_wanted", 'Closing')

    def open(self):
        # print('Open button!', flush=True)
        GPIO.output(self.wayPin, GPIO.HIGH)
        cache.set("direction_wanted", 'Opening')
        self.publish_state()

    def close(self):
        # print('Close button!', flush=True)
        GPIO.output(self.wayPin, GPIO.LOW)
        cache.set("direction_wanted", 'Closing')
        self.publish_state()

    def button_open_callback(self, channel):
        if GPIO.input(self.but1):  # and check again the input
            self.open()
            self.publish_override()

    def button_close_callback(self, channel):
        if GPIO.input(self.but2):  # and check again the input
            self.close()
            self.publish_override()

    def register_events(self):
        GPIO.add_event_detect(self.but1, GPIO.RISING,
                              callback=self.button_open_callback, bouncetime=300)
        GPIO.add_event_detect(
            self.but2, GPIO.RISING, callback=self.button_close_callback, bouncetime=300)

    def publish_state(self):
        data = cache.get_dict("temperature", "sensor_open", "completed_steps",
                              "remaining_steps", "direction_wanted", "direction", "sleeping", "uptime", "override")
        # print("publish: {}".format(data))
        mqtt.publish('chicken-coop/tele/STATE', json.dumps(data))

    def publish_override(self, enable=True):
        # print("publish: {}".format(data))
        mqtt.publish('chicken-coop/tele/OVERRIDE', enable)


door = Door()
