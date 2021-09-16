from flask_apscheduler import APScheduler

from .door import door
from .temperature import temperature

scheduler = APScheduler()

INTERVAL_TASK_MQTT_ID = 'interval-mqtt-publish'
INTERVAL_TASK_TEMPERATURE_ID = 'interval-temperature-publish'


def mqtt_task():
    door.publish_state()


def temperature_task():
    temperature.read()


def init_scheduler(app):
    scheduler.init_app(app)

    scheduler.add_job(
        id=INTERVAL_TASK_MQTT_ID,
        func=mqtt_task,
        trigger='interval',
        seconds=30)

    scheduler.add_job(
        id=INTERVAL_TASK_TEMPERATURE_ID,
        func=temperature_task,
        trigger='interval',
        seconds=60)

    scheduler.start()
