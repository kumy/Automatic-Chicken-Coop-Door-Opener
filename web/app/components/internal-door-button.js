import Component from '@glimmer/component';
import { action } from '@ember/object';
import ENV from 'chicken-coop-web/config/environment';

var INTERNAL_DOOR_URL = `http://${ENV.APP.INTERNAL_DOOR_IP}:8080/switch/chicken_coop_ouverture_porte/turn_`;

export default class InternalDoorButton extends Component {
  @action toggle() {
    let dir = 'on';
    if (this.args.model.int.switch_chicken_coop_ouverture_porte) {
      dir = 'off';
    }
    fetch(INTERNAL_DOOR_URL + dir, {
      method: 'post',
    });
  }

  get button_text() {
    if (this.args.model.int.switch_chicken_coop_ouverture_porte) {
      return 'Close';
    } else {
      return 'Open';
    }
  }
}
