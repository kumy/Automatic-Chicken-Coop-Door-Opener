from flask import Flask
from flask_bootstrap import Bootstrap
from pathlib import Path

from .common import cache
from .door import door
from .serial import ser
from .mqtt import mqtt
from .scheduler import init_scheduler

from .frontend import frontend


def create_app(configfile=None):
    app = Flask(__name__)

    Bootstrap(app)
    app.register_blueprint(frontend)
    app.config['BOOTSTRAP_SERVE_LOCAL'] = True

    app.config['SERIAL_TIMEOUT'] = 0.2
    app.config['SERIAL_PORT'] = '/dev/ttyUSB0'
    app.config['SERIAL_BAUDRATE'] = 115200
    app.config['SERIAL_BYTESIZE'] = 8
    app.config['SERIAL_PARITY'] = 'N'
    app.config['SERIAL_STOPBITS'] = 1

    app.config['MQTT_BROKER_URL'] = '192.168.125.8'
    app.config['MQTT_BROKER_PORT'] = 1883
    # app.config['MQTT_USERNAME'] = 'user'
    # app.config['MQTT_PASSWORD'] = 'secret'
    app.config['MQTT_REFRESH_TIME'] = 1.0  # refresh time in seconds

    cache.init_app(app=app, config={"CACHE_TYPE": "redis", 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})
    door.setup()
    door.register_events()
    ser.init_app(app)
    mqtt.init_app(app)
    init_scheduler(app)

    return app
