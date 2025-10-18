import Route from '@ember/routing/route';
import { service } from '@ember/service';
import RSVP from 'rsvp';

export default class IndexRoute extends Route {
  @service store;

  async model() {
    return RSVP.hash({
      int: this.store.findRecord('internal-door', '1'),
      ext: this.store.findRecord('external-door', '1'),
    });
  }
}
