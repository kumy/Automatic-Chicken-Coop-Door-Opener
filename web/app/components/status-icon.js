import Component from '@glimmer/component';

export default class StatusIcon extends Component {
  get icon_name() {
    if (this.args.model.int.switch_chicken_coop_ouverture_porte) {
      return 'day';
    }
    return 'night';
  }
}
