import argparse
import glob
import logging
import os
import sys

import asyncio
import json
import socket
import time
import uuid

import serial_asyncio
from aioesphomeapi.api_pb2 import SwitchStateResponse, \
    STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL_INCREASING
from aioesphomeserver import (
    Device,
    SwitchEntity, SensorEntity, EntityListener, BinarySensorEntity,
)
import apigpio
from statistics import mean

from aioesphomeapi.model import SensorStateClass

APIGPIO_HOST = "192.168.130.196"
DEVICE_PORT = "/dev/ttyUSB0"

ENTITY_PREFIX = "Chicken Coop"
ENTITY_SLUG_PREFIX = "chicken_coop"

BUTTON_OPEN_GPIO = 17
BUTTON_CLOSE_GPIO = 18
DIRECTION_GPIO = 27  # way pin ON==open

# b = type('', (), {})()
# b.this_works = {}

logger = logging.getLogger(__name__)

# Double-press safety feature: buttons must be pressed twice within time window
DOUBLE_PRESS_MIN_DELAY = 0.5  # seconds - minimum time between presses (prevents bounce)
DOUBLE_PRESS_MAX_DELAY = 3.0  # seconds - maximum time between presses (timeout)
button_press_state = {
    'open': {'count': 0, 'timestamp': 0},
    'close': {'count': 0, 'timestamp': 0}
}


def setup_logging(log_level: str = "DEBUG") -> None:
    """Configure logging with the specified level.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, log_level.upper(), logging.DEBUG)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(numeric_level)


# Serial receive status as json 115200
# {
#     "sensor_open": true/false,
#     "sensor_close": true/false,
#     "completed_steps": 0,
#     "remaining_steps": 0,
#     "direction_wanted": "Opening/Closing",
#     "direction": "Opening/Closing",
#     "sleeping": true/false,
#     "uptime": 0
# }

class TemperatureSensorListener(EntityListener):
    _previous = None

    async def can_handle(self, key, message):
        return False

    async def run(self):
        def read():
            devices = glob.glob("/sys/bus/w1/devices/28*/temperature")
            temperatures = []
            for device in devices:
                with open(device) as f:
                    t = f.read()
                    if t != '':
                        temperatures.append(int(t) / 1000.0)
            try:
                avg = round(mean(temperatures), 1)
            except (ValueError, ZeroDivisionError, Exception) as e:
                logger.warning(f"Temperature calculation failed: {e}")
                avg = None
            return avg

        sensor = self.device.get_entity(f"{ENTITY_SLUG_PREFIX}_temperature_sensor")
        while True:
            temperature = read()
            if temperature is not None and self._previous != temperature:
                self._previous = temperature
                await sensor.set_state(temperature)
            await asyncio.sleep(60)


class UptimeListener(EntityListener):
    async def can_handle(self, key, message):
        return False

    async def run(self):
        sensor = self.device.get_entity(f"{ENTITY_SLUG_PREFIX}_uptime")
        while True:
            uptime = int(time.clock_gettime(time.CLOCK_BOOTTIME))
            logger.debug(f'reading uptime: {uptime}')
            await sensor.set_state(uptime)
            await asyncio.sleep(60)


class DoorSwitchListener(EntityListener):
    _porte_ouverte = None
    _previous = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def can_handle(self, key, message):
        if not isinstance(message, SwitchStateResponse):
            return False
        return await super().can_handle(key, message)

    async def handle(self, key, message):
        sensor = self.device.get_entity(f"{ENTITY_SLUG_PREFIX}_ouverture_porte")
        if sensor is not None:
            self._porte_ouverte = message.state

    async def run(self):
        while True:
            if self._previous != self._porte_ouverte:
                self._previous = self._porte_ouverte
                if self._porte_ouverte:
                    logger.info('ouverture')
                    await gate.open()
                else:
                    logger.info('fermeture')
                    await gate.close()
            await asyncio.sleep(0.1)


class EntityListenerFromSerial(EntityListener):
    # previous_ = None

    async def can_handle(self, key, message):
        return False

    # def set_state(self, sensor, key, interval=1):
    #     try:
    #         sensor_ = self.device.get_entity(f"{ENTITY_SLUG_PREFIX}_{sensor}")
    #         if sensor_ is not None and key in b.this_works:
    #             val = b.this_works[key]
    #             if val != self.previous_:
    #                 self.previous_ = val
    #                 print(f'reading {key}: {val}')
    #                 if val == "Opening":
    #                     val = True
    #                 elif val == "Closing":
    #                     val = False
    #                 elif key == 'uptime':
    #                     val = int(val/1000)
    #                 # await sensor_.set_state(val)
    #                 sensor_.set_state(val)
    #                 print("DEBUG 1.0")
    #             # else:
    #             #     print("DEBUG 1.1")
    #         else:
    #             print(f"DEBUG 1.2 {key}")
    #             if sensor_ is None:
    #                 print("sensor_ is None")
    #             print(b.this_works)
    #         # await asyncio.sleep(interval)
    #     except Exception as e:
    #         print(e)


class OutputProtocol(asyncio.Protocol):
    buffer = None
    payload = None

    def __init__(self):
        super().__init__()
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        logger.info(f'port opened: {transport}')
        # transport.serial.rts = False  # You can manipulate Serial object via transport
        # transport.write(b'Hello, World!\n')  # Write serial data via transport

    def data_received(self, data):
        # print('data received', repr(data))
        self.buffer += data
        if b'\n' in data:
            if b'{' in self.buffer and b'}' in self.buffer:
                try:
                    self.payload = json.loads(self.buffer)
                    # print(json.dumps(b.this_works, indent=2))
                    asyncio.create_task(self.process_payload())
                    # await self.process_payload()
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from Arduino: {self.buffer!r}, error: {e}")
                except Exception as e:
                    logger.exception(f"Unexpected error processing serial data: {e}")
            self.buffer = b""

    def connection_lost(self, exc):
        logger.info('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        logger.debug(f'pause writing, buffer size: {self.transport.get_write_buffer_size()}')

    def resume_writing(self):
        logger.debug(f'resume writing, buffer size: {self.transport.get_write_buffer_size()}')

    async def process_payload(self):
        for key, val in self.payload.items():
            if key == 'uptime':
                key = 'arduino_uptime'
                val = int(val/1000)
            sensor_ = device.get_entity(f"{ENTITY_SLUG_PREFIX}_{key}")
            # print(f"processing: {key}={val} ({sensor_._state})")
            if key == 'arduino_uptime' and val - sensor_._state < 60:
                continue
            if val == "Opening":
                val = True
            elif val == "Closing":
                val = False
            # print(f"processing: {key}={val}")
            # print(sensor_)
            if sensor_ is not None and sensor_._state != val:
                await sensor_.set_state(val)

        # print("")


async def monitor_serial():
    loop = asyncio.get_running_loop()
    await serial_asyncio.create_serial_connection(loop, OutputProtocol, DEVICE_PORT, baudrate=115200)


async def monitor_coroutines():
    # helper to log details of all tasks
    def log_all_tasks_helper(excluded=[]):
        # get all tasks
        for task in asyncio.all_tasks():
            # # skip excluded tasks
            # if task in excluded:
            #     continue
            # # print the task stack
            # task.print_stack()
            logger.debug(task)
    while True:
        log_all_tasks_helper()
        await asyncio.sleep(10)


class Gate(object):
    """
    Chicken Coop Gate
    """

    def __init__(self, pi=None, gpio=DIRECTION_GPIO):
        self.pi = pi
        self.gate_gpio = gpio

    def set_pi(self, pi):
        self.pi = pi

    async def open(self):
        await self.pi.write(self.gate_gpio, 1)  # Open
        logger.info('ouverture ack')

    async def close(self):
        await self.pi.write(self.gate_gpio, 0)  # Close
        logger.info('fermeture ack')


@apigpio.Debounce(1000)
def on_bt_open(gpio, level, tick):
    logger.debug(f'on_bt_open: gpio={gpio} level={level} tick={tick}')

    # Double-press safety: require two presses within time window
    current_time = time.time()
    state = button_press_state['open']
    time_since_last = current_time - state['timestamp'] if state['timestamp'] > 0 else 999

    logger.debug(f'on_bt_open: state before check: count={state["count"]}, time_since_last={time_since_last:.2f}s')

    # Check if this is a valid second press (within time window)
    if state['count'] > 0:
        time_diff = current_time - state['timestamp']
        if DOUBLE_PRESS_MIN_DELAY <= time_diff <= DOUBLE_PRESS_MAX_DELAY:
            # Second press within valid window - execute action
            logger.info(f'on_bt_open: second press detected after {time_diff:.2f}s, executing action')
            sensor = device.get_entity(f"{ENTITY_SLUG_PREFIX}_ouverture_porte")
            asyncio.get_event_loop().create_task(sensor.set_state(True))
            logger.info('on_bt_open: ouverture sent')
            # Reset state
            state['count'] = 0
            state['timestamp'] = 0
        elif time_diff < DOUBLE_PRESS_MIN_DELAY:
            # Too fast - likely bounce, ignore
            logger.debug(f'on_bt_open: press too fast ({time_diff:.2f}s < {DOUBLE_PRESS_MIN_DELAY}s), ignoring')
        else:
            # Timeout - treat as new first press
            logger.info(f'on_bt_open: timeout ({time_diff:.2f}s > {DOUBLE_PRESS_MAX_DELAY}s), treating as first press')
            state['count'] = 1
            state['timestamp'] = current_time
    else:
        # First press - wait for second press
        logger.info(f'on_bt_open: first press detected, waiting for second press in {DOUBLE_PRESS_MIN_DELAY}s-{DOUBLE_PRESS_MAX_DELAY}s window')
        state['count'] = 1
        state['timestamp'] = current_time


@apigpio.Debounce(1000)
def on_bt_close(gpio, level, tick):
    logger.debug(f'on_bt_close: gpio={gpio} level={level} tick={tick}')

    # Double-press safety: require two presses within time window
    current_time = time.time()
    state = button_press_state['close']
    time_since_last = current_time - state['timestamp'] if state['timestamp'] > 0 else 999

    logger.debug(f'on_bt_close: state before check: count={state["count"]}, time_since_last={time_since_last:.2f}s')

    # Check if this is a valid second press (within time window)
    if state['count'] > 0:
        time_diff = current_time - state['timestamp']
        if DOUBLE_PRESS_MIN_DELAY <= time_diff <= DOUBLE_PRESS_MAX_DELAY:
            # Second press within valid window - execute action
            logger.info(f'on_bt_close: second press detected after {time_diff:.2f}s, executing action')
            sensor = device.get_entity(f"{ENTITY_SLUG_PREFIX}_ouverture_porte")
            asyncio.get_event_loop().create_task(sensor.set_state(False))
            logger.info('on_bt_close: fermeture sent')
            # Reset state
            state['count'] = 0
            state['timestamp'] = 0
        elif time_diff < DOUBLE_PRESS_MIN_DELAY:
            # Too fast - likely bounce, ignore
            logger.debug(f'on_bt_close: press too fast ({time_diff:.2f}s < {DOUBLE_PRESS_MIN_DELAY}s), ignoring')
        else:
            # Timeout - treat as new first press
            logger.info(f'on_bt_close: timeout ({time_diff:.2f}s > {DOUBLE_PRESS_MAX_DELAY}s), treating as first press')
            state['count'] = 1
            state['timestamp'] = current_time
    else:
        # First press - wait for second press
        logger.info(f'on_bt_close: first press detected, waiting for second press in {DOUBLE_PRESS_MIN_DELAY}s-{DOUBLE_PRESS_MAX_DELAY}s window')
        state['count'] = 1
        state['timestamp'] = current_time


async def subscribe(pi):
    await pi.set_mode(BUTTON_OPEN_GPIO, apigpio.INPUT)
    await pi.set_mode(BUTTON_CLOSE_GPIO, apigpio.INPUT)
    await pi.set_mode(DIRECTION_GPIO, apigpio.OUTPUT)
    # Open by default
    sensor = device.get_entity(f"{ENTITY_SLUG_PREFIX}_ouverture_porte")
    await sensor.set_state(True)

    gate.set_pi(pi)

    await pi.add_callback(BUTTON_OPEN_GPIO, edge=apigpio.FALLING_EDGE,
                          func=on_bt_open)
    await pi.add_callback(BUTTON_CLOSE_GPIO, edge=apigpio.FALLING_EDGE,
                          func=on_bt_close)


async def monitor_gpio():
    loop = asyncio.get_running_loop()
    pi = apigpio.Pi(loop)
    address = (APIGPIO_HOST, 8888)
    await pi.connect(address)
    await subscribe(pi)


def create_device():
    device = Device(
        name=f"Chicken Coop",
        friendly_name=f"Chicken Coop - {socket.gethostname()}",
        mac_address=(':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])),
        model="Chicken Coop",
        suggested_area="Chickens",
        project_name="chicken-coop",
        project_version="2.0.0",
        board="Raspberry Pi",
        platform="ARM64",
    )

    ouverture_porte = SwitchEntity(
        name=f"{ENTITY_PREFIX} Ouverture porte",
    )
    ouverture_porte.set_key(f"{ENTITY_SLUG_PREFIX}_ouverture_porte")
    device.add_entity(
        ouverture_porte,
    )

    device.add_entity(
        DoorSwitchListener(
            name="_listener_door_switch",
            entity_id=f"{ENTITY_SLUG_PREFIX}_ouverture_porte"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Button open",
        )
    )

    # device.add_entity(
    #     ButtonOpenListener(
    #         name="_listener_button_open",
    #         entity_id=f"{ENTITY_SLUG_PREFIX}_button_open"
    #     )
    # )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Button close",
        )
    )

    # device.add_entity(
    #     ButtonOpenListener(
    #         name="_listener_button_close",
    #         entity_id=f"{ENTITY_SLUG_PREFIX}_button_close"
    #     )
    # )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Sensor open",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_sensor_open",
            entity_id=f"{ENTITY_SLUG_PREFIX}_sensor_open"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Sensor close",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_sensor_close",
            entity_id=f"{ENTITY_SLUG_PREFIX}_sensor_close"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Direction",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_direction",
            entity_id=f"{ENTITY_SLUG_PREFIX}_direction"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Direction wanted",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_direction_wanted",
            entity_id=f"{ENTITY_SLUG_PREFIX}_direction_wanted"
        )
    )

    device.add_entity(
        SensorEntity(
            name=f"{ENTITY_PREFIX} Completed steps",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_completed_steps",
            entity_id=f"{ENTITY_SLUG_PREFIX}_completed_steps"
        )
    )

    device.add_entity(
        SensorEntity(
            name=f"{ENTITY_PREFIX} Remaining steps",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_remaining_steps",
            entity_id=f"{ENTITY_SLUG_PREFIX}_remaining_steps"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name=f"{ENTITY_PREFIX} Sleeping",
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_sleeping",
            entity_id=f"{ENTITY_SLUG_PREFIX}_sleeping"
        )
    )

    device.add_entity(
        SensorEntity(
            name=f"{ENTITY_PREFIX} Arduino uptime",
            icon="mdi:timer-outline",
            unit_of_measurement="s",
            accuracy_decimals=0,
            device_class="duration",
            state_class=STATE_CLASS_TOTAL_INCREASING,
        )
    )

    device.add_entity(
        EntityListenerFromSerial(
            name="_listener_arduino_uptime",
            entity_id=f"{ENTITY_SLUG_PREFIX}_arduino_uptime"
        )
    )

    device.add_entity(
        SensorEntity(
            name=f"{ENTITY_PREFIX} Uptime",
            icon="mdi:timer-outline",
            unit_of_measurement="s",
            accuracy_decimals=0,
            device_class="duration",
            state_class=STATE_CLASS_TOTAL_INCREASING,
        )
    )

    device.add_entity(
        UptimeListener(
            name="_listener_uptime",
        )
    )

    device.add_entity(
        SwitchEntity(
            name=f"{ENTITY_PREFIX} Mode manuel",
        )
    )

    # TODO: return RPi statuses

    device.add_entity(
        SensorEntity(
            name=f"{ENTITY_PREFIX} Temperature Sensor",
            unit_of_measurement="°C",
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT,
            device_class="temperature",
        )
    )

    device.add_entity(
        TemperatureSensorListener(
            name="_listener_temperature_sensor",
            entity_id=f"{ENTITY_SLUG_PREFIX}_temperature_sensor"
        )
    )

    return device


device = create_device()
gate = Gate()


def main():
    """Main entry point for the chicken coop application.

    Can be called directly or via gunicorn for production deployment.
    Runs the async event loop internally.
    """
    # Setup logging from environment variable or default to DEBUG
    log_level = os.getenv('LOG_LEVEL', 'DEBUG')
    setup_logging(log_level)

    logger.info(f"Starting Chicken Coop application with log level: {log_level}")

    async def run_forever():
        async with asyncio.TaskGroup() as tg:
            # tg.create_task(monitor_coroutines())
            tg.create_task(monitor_serial())
            tg.create_task(monitor_gpio())
            tg.create_task(device.run(6053, 8080))

    # Run the async event loop
    asyncio.run(run_forever())


def cli_main():
    """CLI entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Chicken Coop Door Automation System',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='DEBUG',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level'
    )

    args = parser.parse_args()

    # Set environment variable for main() to use
    os.environ['LOG_LEVEL'] = args.log_level

    # Call main which handles its own event loop
    main()


if __name__ == "__main__":
    cli_main()
