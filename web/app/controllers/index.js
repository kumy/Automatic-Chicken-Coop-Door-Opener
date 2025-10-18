import Controller from '@ember/controller';

export default class IndexController extends Controller {
  get bgcolor() {
    // if (!this.model.int) {
    //   return;
    // }
    // console.log(this.model.int.switch_chicken_coop_ouverture_porte)
    if (this.model.int.switch_chicken_coop_ouverture_porte) {
      document.body.classList.remove('night');
      document.body.classList.add('day');
      return 'Open';
    } else {
      document.body.classList.remove('day');
      document.body.classList.add('night');
      return 'Close';
    }
  }
}
