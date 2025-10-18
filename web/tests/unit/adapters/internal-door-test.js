import { setupTest } from 'chicken-coop-web/tests/helpers';
import { module, test } from 'qunit';

module('Unit | Adapter | internal door', function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function (assert) {
    const adapter = this.owner.lookup('adapter:internal-door');
    assert.ok(adapter, 'adapter exists');
  });
});
