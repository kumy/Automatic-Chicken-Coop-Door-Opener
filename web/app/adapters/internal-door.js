import Adapter from '@ember-data/adapter';
import { service } from '@ember/service';
import BooleanTransform from 'chicken-coop-web/transforms/boolean';
import ENV from 'chicken-coop-web/config/environment';

var SOCKET = `http://${ENV.APP.CHICKEN_COOP_IP}/int/events`;
// var SOCKET = `http://${ENV.APP.INTERNAL_DOOR_IP}:8080/events`;

export default class InternalDoorAdapter extends Adapter {
  @service store;

  socket = undefined;
  data = {
    data: [
      {
        type: 'internal-door',
        id: '1',
        attributes: {},
      },
    ],
  };

  init() {
    console.log('Initializing internal door...');
    super.init();
    // this.store.pushPayload('internal-door', this.data['data'][0]);
    this.store.push(this.data);

    var es = new EventSource(SOCKET);

    es.onopen = function () {};

    es.addEventListener('state', (e) => {
      const response = JSON.parse(e.data);
      console.log('Int: New state', response.id, response.state);
      this.data['data'][0]['attributes'][response.id.replace('-', '_')] =
        new BooleanTransform().serialize(response.state);
      this.store.push(this.data);
    });

    this.socket = undefined;
  }

  findRecord() {
    return {
      data: this.data['data'][0],
    };
  }
}
