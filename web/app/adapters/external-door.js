import Adapter from '@ember-data/adapter';
import { service } from '@ember/service';
import BooleanTransform from 'chicken-coop-web/transforms/boolean';
import ENV from 'chicken-coop-web/config/environment';

var SOCKET = `http://${ENV.APP.CHICKEN_COOP_IP}/ext/events`;
// var SOCKET = `http://${ENV.APP.EXTERNAL_DOOR_IP}/events`;

export default class ExternalDoorAdapter extends Adapter {
  @service store;

  socket = undefined;
  data = {
    data: [
      {
        type: 'external-door',
        id: '1',
        attributes: {},
      },
    ],
  };

  init() {
    console.log('Initializing external door...');
    super.init();
    // this.store.pushPayload('internal-door', this.data['data'][0]);
    this.store.push(this.data);

    var es = new EventSource(SOCKET);

    es.onopen = function () {};

    es.addEventListener('state', (e) => {
      const response = JSON.parse(e.data);
      console.log('Ext: New state', response.id, response.state);
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

  // findRecord() {
  //   return {
  //     data: {
  //       type: 'external-door',
  //       id: '1',
  //       attributes: {
  //         binary_sensor_button: false,
  //         binary_sensor_up: false,
  //         binary_sensor_down: false,
  //         cover_volet: 1,
  //         switch_up: false,
  //         switch_down: false,
  //       },
  //     },
  //   };
  // }
}
