import { module, test } from 'qunit';
import { setupRenderingTest } from 'chicken-coop-web/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | status-icon', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<StatusIcon />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <StatusIcon>
        template block text
      </StatusIcon>
    `);

    assert.dom().hasText('template block text');
  });
});
