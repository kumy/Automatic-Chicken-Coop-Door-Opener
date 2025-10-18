import { setupTest } from 'chicken-coop-web/tests/helpers';
import { module, test } from 'qunit';

module('Unit | Model | external door', function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function (assert) {
    const store = this.owner.lookup('service:store');
    const model = store.createRecord('external-door', {});
    assert.ok(model, 'model exists');
  });
});
