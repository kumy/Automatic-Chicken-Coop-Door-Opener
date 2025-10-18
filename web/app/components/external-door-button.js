import Component from '@glimmer/component';
import { action } from '@ember/object';
import ENV from 'chicken-coop-web/config/environment';

var EXTERNAL_DOOR_URL = `http://${ENV.APP.EXTERNAL_DOOR_IP}/cover/volet/`;

export default class ExternalDoorButton extends Component {
  @action toggle() {
    let dir = 'open';
    if (this.args.model.ext.cover_volet) {
      dir = 'close';
    }
    fetch(EXTERNAL_DOOR_URL + dir, {
      method: 'post',
    });
  }

  get button_text() {
    if (this.args.model.ext.cover_volet) {
      return 'Close';
    } else {
      return 'Open';
    }
  }
}
