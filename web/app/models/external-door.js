import Model, { attr } from '@ember-data/model';

export default class ExternalDoorModel extends Model {
  @attr('boolean') binary_sensor_button;
  @attr('boolean') binary_sensor_up;
  @attr('boolean') binary_sensor_down;
  @attr('number') cover_volet;
  @attr('boolean') switch_up;
  @attr('boolean') switch_down;
}
