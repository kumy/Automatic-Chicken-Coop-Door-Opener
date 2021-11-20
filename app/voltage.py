import subprocess

from .common import cache

GET_THROTTLED_CMD = 'vcgencmd get_throttled'
MESSAGES = {
    0: 'Under-voltage!',
    1: 'ARM frequency capped!',
    2: 'Currently throttled!',
    3: 'Soft temperature limit active',
    16: 'Under-voltage has occurred since last reboot.',
    17: 'Throttling has occurred since last reboot.',
    18: 'ARM frequency capped has occurred since last reboot.',
    19: 'Soft temperature limit has occurred'
}

class Voltage:

    def read(self):
        throttled_output = subprocess.check_output(GET_THROTTLED_CMD, shell=True)
        throttled_binary = bin(int(throttled_output.split(b'=')[1], 0))

        warnings = list()
        for position, message in MESSAGES.items():
            # Check for the binary digits to be "on" for each warning message
            if len(throttled_binary) > position and throttled_binary[0 - position - 1] == '1':
                warnings.append(message)
        cache.set("voltage", warnings)

voltage = Voltage()
