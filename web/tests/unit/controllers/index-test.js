import { module, test } from 'qunit';
import { setupTest } from 'chicken-coop-web/tests/helpers';

module('Unit | Controller | index', function (hooks) {
  setupTest(hooks);

  // TODO: Replace this with your real tests.
  test('it exists', function (assert) {
    let controller = this.owner.lookup('controller:index');
    assert.ok(controller);
  });
});
