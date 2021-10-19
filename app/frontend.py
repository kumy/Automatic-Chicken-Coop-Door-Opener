# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/

from flask import Blueprint, send_file, render_template, flash, redirect, url_for, request
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from urllib.parse import urlparse
from distutils.util import strtobool
import json

from .serial import ser
from .mqtt import mqtt

from markupsafe import escape

from .common import cache
from .door import door
from .temperature import temperature

frontend = Blueprint('frontend', __name__)


@ser.on_message()
def handle_message(msg):
    data = json.loads(msg)
    # import pprint
    # pprint.pprint(data)
    # print('', flush=True)
    cache.set_many(data)


@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('chicken-coop/cmnd/ACTION')
    mqtt.subscribe('chicken-coop/tele/OVERRIDE')
    temperature.read()
    door.publish_override(False)
    door.publish_state()
    cache.set('override', None)


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    if data["topic"] == 'chicken-coop/cmnd/ACTION':
        if data["payload"] == 'OPEN':
            print('MQTT Open!', flush=True)
            door.open()
        elif data["payload"] == 'CLOSE':
            print('MQTT Close!', flush=True)
            door.close()
    if data["topic"] == 'chicken-coop/tele/OVERRIDE':
        cache.set('override', bool(strtobool(data["payload"])))


@frontend.route('/')
def index():
    o = urlparse(request.base_url)
    data = {
        'picture': 'day.svg' if cache.get('direction_wanted') == 'Opening' else 'night.svg',
        'host': o.hostname,
        'cache': cache,
    }
    return render_template('index.html', data=data)


@frontend.route('/open')
def open_door():
    door.open()
    door.publish_override()
    return redirect(url_for('.index'))


@frontend.route('/close')
def close_door():
    door.close()
    door.publish_override()
    return redirect(url_for('.index'))


@frontend.route('/disable-override')
def disable_override():
    door.publish_override(False)
    return redirect(url_for('.index'))
