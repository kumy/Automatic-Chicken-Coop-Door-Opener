import { setupTest } from 'chicken-coop-web/tests/helpers';
import { module, test } from 'qunit';

module('Unit | Transform | number', function (hooks) {
  setupTest(hooks);

  // Replace this with your real tests.
  test('it exists', function (assert) {
    const transform = this.owner.lookup('transform:number');
    assert.ok(transform, 'transform exists');
  });
});
