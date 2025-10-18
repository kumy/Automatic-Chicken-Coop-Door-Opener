import { setupTest } from 'chicken-coop-web/tests/helpers';
import { module, test } from 'qunit';

module('Unit | Adapter | external door', function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function (assert) {
    const adapter = this.owner.lookup('adapter:external-door');
    assert.ok(adapter, 'adapter exists');
  });
});
