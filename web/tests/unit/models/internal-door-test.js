import { setupTest } from 'chicken-coop-web/tests/helpers';
import { module, test } from 'qunit';

module('Unit | Model | internal door', function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function (assert) {
    const store = this.owner.lookup('service:store');
    const model = store.createRecord('internal-door', {});
    assert.ok(model, 'model exists');
  });
});
