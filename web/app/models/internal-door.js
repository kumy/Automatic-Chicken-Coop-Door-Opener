import Model, { attr } from '@ember-data/model';

export default class InternalDoorModel extends Model {
  @attr('boolean') switch_chicken_coop_ouverture_porte;
  @attr('boolean') binary_sensor_chicken_coop_button_open;
  @attr('boolean') binary_sensor_chicken_coop_button_close;
  @attr('boolean') binary_sensor_chicken_coop_sensor_open;
  @attr('boolean') binary_sensor_chicken_coop_sensor_close;
  @attr('boolean') binary_sensor_chicken_coop_direction;
  @attr('boolean') binary_sensor_chicken_coop_direction_wanted;
  @attr('number') sensor_chicken_coop_completed_steps;
  @attr('number') sensor_chicken_coop_remaining_steps;
  @attr('boolean') binary_sensor_chicken_coop_sleeping;
  @attr('number') sensor_chicken_coop_arduino_uptime;
  @attr('number') sensor_chicken_coop_uptime;
  @attr('boolean') switch_chicken_coop_mode_manuel;
  @attr('number') sensor_chicken_coop_temperature_sensor;
}
