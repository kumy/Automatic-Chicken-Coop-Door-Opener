import { module, test } from 'qunit';
import { setupRenderingTest } from 'chicken-coop-web/tests/helpers';
import { render } from '@ember/test-helpers';
import { hbs } from 'ember-cli-htmlbars';

module('Integration | Component | external-door-button', function (hooks) {
  setupRenderingTest(hooks);

  test('it renders', async function (assert) {
    // Set any properties with this.set('myProperty', 'value');
    // Handle any actions with this.set('myAction', function(val) { ... });

    await render(hbs`<ExternalDoorButton />`);

    assert.dom().hasText('');

    // Template block usage:
    await render(hbs`
      <ExternalDoorButton>
        template block text
      </ExternalDoorButton>
    `);

    assert.dom().hasText('template block text');
  });
});
