import functools
import glob
import io
import logging

import asyncio
import json
import time

import serial_asyncio
from aioesphomeapi.api_pb2 import SwitchStateResponse, \
    SensorStateResponse, SensorStateClass, STATE_CLASS_MEASUREMENT, STATE_CLASS_TOTAL_INCREASING
from aioesphomeserver import (
    Device,
    SwitchEntity, SensorEntity, EntityListener, BinarySensorEntity,
)
import apigpio
from statistics import mean

from aioesphomeapi.model import SensorStateClass

APIGPIO_HOST = "192.168.130.196"
DEVICE_PORT = "/dev/ttyUSB0"

BUTTON_OPEN_GPIO = 17
BUTTON_CLOSE_GPIO = 18
DIRECTION_GPIO = 27  # way pin ON==open

b = type('', (), {})()
b.this_works = {}

logger = logging.getLogger(__name__)


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def can_handle(self, key, message):
        return False
        # if not isinstance(message, SensorStateResponse):
        #     return False
        # return await super().can_handle(key, message)

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
            except:
                avg = 0
            return avg

        sensor = self.device.get_entity("temperature_sensor")
        while True:
            temperature = read()
            if self._previous != temperature:
                self._previous = temperature
                await sensor.set_state(temperature)
            await asyncio.sleep(60)


class UptimeListener(EntityListener):
    async def can_handle(self, key, message):
        return False

    async def run(self):
        sensor = self.device.get_entity("uptime")
        while True:
            uptime = int(time.clock_gettime(time.CLOCK_BOOTTIME))
            print(f'reading uptime: {uptime}')
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
        sensor = self.device.get_entity("ouverture_porte")
        if sensor is not None:
            self._porte_ouverte = message.state

    async def run(self):
        while True:
            if self._previous != self._porte_ouverte:
                self._previous = self._porte_ouverte
                if self._porte_ouverte:
                    print('ouverture')
                    await gate.open()
                else:
                    print('fermeture')
                    await gate.close()
            await asyncio.sleep(0.1)


class EntityListenerFromSerial(EntityListener):
    previous_ = None

    async def can_handle(self, key, message):
        return False

    async def set_state(self, sensor, key, interval=1):
        try:
            sensor_ = self.device.get_entity(sensor)
            if sensor_ is not None and key in b.this_works:
                val = b.this_works[key]
                if val != self.previous_:
                    self.previous_ = val
                    print(f'reading {key}: {val}')
                    if val == "Opening":
                        val = True
                    elif val == "Closing":
                        val = False
                    elif key == 'uptime':
                        val = int(val/1000)
                    await sensor_.set_state(val)
                    print("DEBUG 1.0")
                # else:
                #     print("DEBUG 1.1")
            else:
                print(f"DEBUG 1.2 {key}")
                if sensor_ is None:
                    print("sensor_ is None")
                print(b.this_works)
            await asyncio.sleep(interval)
        except Exception as e:
            print(e)


class ArduinoUptimeListener(EntityListenerFromSerial):
    async def run(self):
        await asyncio.sleep(1)
        while True:
            print("DEBUG 1")
            await self.set_state("arduino_uptime", 'uptime', 60)


# class ButtonOpenListener(EntityListenerFromSerial):
#     async def run(self):
#         while True:
#             await self.set_state("button_open", 'button_open')


# class ButtonCloseListener(EntityListenerFromSerial):
#     async def run(self):
#         while True:
#             await self.set_state("button_close", 'button_close')


class SensorOpenListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("sensor_open", 'sensor_open')


class SensorCloseListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("sensor_close", 'sensor_close')


class DirectionListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("direction", 'direction')


class DirectionWantedListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("direction_wanted", 'direction_wanted')


class CompletedStepsListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("completed_steps", 'completed_steps')


class RemainingStepsListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("remaining_steps", 'remaining_steps')


class SleepingListener(EntityListenerFromSerial):
    async def run(self):
        while True:
            await self.set_state("sleeping", 'sleeping')


class OutputProtocol(asyncio.Protocol):
    buffer = None

    # context_ = None

    def __init__(self):
        super().__init__()
        self.buffer = b""

    def connection_made(self, transport):
        self.transport = transport
        print('port opened', transport)
        # transport.serial.rts = False  # You can manipulate Serial object via transport
        # transport.write(b'Hello, World!\n')  # Write serial data via transport

    def data_received(self, data):
        # print('data received', repr(data))
        self.buffer += data
        if b'\n' in data:
            if b'{' in self.buffer and b'}' in self.buffer:
                try:
                    b.this_works = json.loads(self.buffer)
                    # print(json.dumps(b.this_works, indent=2))
                except:
                    pass
            self.buffer = b""

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')


async def monitor_serial():
    loop = asyncio.get_running_loop()
    await serial_asyncio.create_serial_connection(loop, OutputProtocol, DEVICE_PORT, baudrate=115200)


async def monitor_coroutines():
    # helper to log details of all tasks
    def log_all_tasks_helper(excluded=[]):
        # get all tasks
        for task in asyncio.all_tasks():
            # skip excluded tasks
            if task in excluded:
                continue
            # print the task stack
            task.print_stack()
            print("\n\n")
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
        print('ouverture ack')

    async def close(self):
        await self.pi.write(self.gate_gpio, 0)  # Close
        print('fermeture ack')


@apigpio.Debounce(500)
def on_bt_open(gpio, level, tick):
    print('on_bt_open {} {} {}'.format(gpio, level, tick))
    sensor = device.get_entity("ouverture_porte")
    asyncio.get_event_loop().create_task(sensor.set_state(True))
    print('ouverture sent')


@apigpio.Debounce(500)
def on_bt_close(gpio, level, tick):
    print('on_bt_close {} {} {}'.format(gpio, level, tick))
    sensor = device.get_entity("ouverture_porte")
    asyncio.get_event_loop().create_task(sensor.set_state(False))
    print('fermeture sent')


async def subscribe(pi):
    await pi.set_mode(BUTTON_OPEN_GPIO, apigpio.INPUT)
    await pi.set_mode(BUTTON_CLOSE_GPIO, apigpio.INPUT)
    await pi.set_mode(DIRECTION_GPIO, apigpio.OUTPUT)
    # Open by default
    sensor = device.get_entity("ouverture_porte")
    await sensor.set_state(True)

    gate.set_pi(pi)

    await pi.add_callback(BUTTON_OPEN_GPIO, edge=apigpio.RISING_EDGE,
                          func=on_bt_open)
    await pi.add_callback(BUTTON_CLOSE_GPIO, edge=apigpio.RISING_EDGE,
                          func=on_bt_close)


async def monitor_gpio():
    loop = asyncio.get_running_loop()
    pi = apigpio.Pi(loop)
    address = (APIGPIO_HOST, 8888)
    await pi.connect(address)
    await subscribe(pi)


def create_device():
    device = Device(
        name="Chicken Coop - DEV",
        mac_address="AC:BC:32:89:0E:C9",
        model="Chicken Coop",
        project_name="chicken-coop",
        project_version="2.0.0",
    )

    device.add_entity(
        SwitchEntity(
            name="Ouverture porte",
        )
    )

    device.add_entity(
        DoorSwitchListener(
            name="_listener_door_switch",
            entity_id="ouverture_porte"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name="Button open",
        )
    )

    # device.add_entity(
    #     ButtonOpenListener(
    #         name="_listener_button_open",
    #         entity_id="button_open"
    #     )
    # )

    device.add_entity(
        BinarySensorEntity(
            name="Button close",
        )
    )

    # device.add_entity(
    #     ButtonOpenListener(
    #         name="_listener_button_close",
    #         entity_id="button_close"
    #     )
    # )

    device.add_entity(
        BinarySensorEntity(
            name="Sensor open",
        )
    )

    device.add_entity(
        SensorOpenListener(
            name="_listener_sensor_open",
            entity_id="sensor_open"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name="Sensor close",
        )
    )

    device.add_entity(
        SensorCloseListener(
            name="_listener_sensor_close",
            entity_id="sensor_close"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name="Direction",
        )
    )

    device.add_entity(
        DirectionListener(
            name="_listener_direction",
            entity_id="direction"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name="Direction wanted",
        )
    )

    device.add_entity(
        DirectionWantedListener(
            name="_listener_direction_wanted",
            entity_id="direction_wanted"
        )
    )

    device.add_entity(
        SensorEntity(
            name="Completed steps",
        )
    )

    device.add_entity(
        CompletedStepsListener(
            name="_listener_completed_steps",
            entity_id="completed_steps"
        )
    )

    device.add_entity(
        SensorEntity(
            name="Remaining steps",
        )
    )

    device.add_entity(
        RemainingStepsListener(
            name="_listener_remaining_steps",
            entity_id="remaining_steps"
        )
    )

    device.add_entity(
        BinarySensorEntity(
            name="Sleeping",
        )
    )

    device.add_entity(
        SleepingListener(
            name="_listener_sleeping",
            entity_id="sleeping"
        )
    )

    device.add_entity(
        SensorEntity(
            name="Uptime",
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
            entity_id="uptime"
        )
    )

    device.add_entity(
        SensorEntity(
            name="Arduino uptime",
            icon="mdi:timer-outline",
            unit_of_measurement="s",
            accuracy_decimals=0,
            device_class="duration",
            state_class=STATE_CLASS_TOTAL_INCREASING,
        )
    )

    device.add_entity(
        ArduinoUptimeListener(
            name="_listener_arduino_uptime",
            entity_id="arduino_uptime"
        )
    )

    device.add_entity(
        SwitchEntity(
            name="Mode manuel",
        )
    )

    # TODO: return RPi statuses

    device.add_entity(
        SensorEntity(
            name="Temperature Sensor",
            unit_of_measurement="°C",
            accuracy_decimals=2,
            state_class=STATE_CLASS_MEASUREMENT,
            device_class="temperature",
        )
    )

    device.add_entity(
        TemperatureSensorListener(
            name="_listener_temperature_sensor",
            entity_id="temperature_sensor"
        )
    )

    return device


device = create_device()
gate = Gate()


def main():
    async def run_forever():
        async with asyncio.TaskGroup() as tg:
            tg.create_task(monitor_coroutines())
            tg.create_task(monitor_serial())
            tg.create_task(monitor_gpio())
            tg.create_task(device.run(6053, 8080))

    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
