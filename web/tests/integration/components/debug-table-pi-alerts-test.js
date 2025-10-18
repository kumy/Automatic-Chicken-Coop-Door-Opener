import { module, test } from 'qunit';
import { setupRenderingTest } from 'chicken-coop-web/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | debug-table-pi-alerts', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<DebugTablePiAlerts />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <DebugTablePiAlerts>
        template block text
      </DebugTablePiAlerts>
    `);

    assert.dom().hasText('template block text');
  });
});
