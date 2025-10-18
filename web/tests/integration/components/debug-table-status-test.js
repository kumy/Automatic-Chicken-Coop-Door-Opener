import { module, test } from 'qunit';
import { setupRenderingTest } from 'chicken-coop-web/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | debug-table-status', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<DebugTableStatus />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <DebugTableStatus>
        template block text
      </DebugTableStatus>
    `);

    assert.dom().hasText('template block text');
  });
});
