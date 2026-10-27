# Advanced Cookie Consent Tests (Regression & GPC)

### Test 5: Cookie Regression Detection

```javascript
// tests/cookie-consent/regression.spec.js
const { test, expect } = require('@playwright/test');
const fs = require('fs');

// Baseline of known cookies — update when new cookies are intentionally added
const KNOWN_COOKIES = new Set([
  'session_id',
  'csrf_token',
  'consent_state',
  'pinnacle_consent_eu',
  'load_balancer',
  '_ga',
  '_ga_PINNACLE',
  '_gid',
  '_fbp',
  '_fbc',
  '_gcl_au',
  '_hjSessionUser',
  '_hjSession',
  'locale',
  'currency',
  'recently_viewed',
  'cart_session',
  'auth_token',
]);

test.describe('Cookie Regression Detection', () => {
  test('no unknown cookies after Accept All', async ({ page }) => {
    await page.goto('/');
    await page.locator('[data-testid="cookie-accept-all"]').click();
    await page.waitForLoadState('networkidle');

    // Visit several pages to trigger all tag scenarios
    const pages = ['/', '/products', '/products/widget-pro', '/cart', '/about', '/blog'];
    for (const path of pages) {
      await page.goto(path);
      await page.waitForLoadState('networkidle');
    }

    const cookies = await page.context().cookies();
    const unknownCookies = cookies.filter(c => {
      // Check if cookie name matches any known prefix
      return !Array.from(KNOWN_COOKIES).some(known =>
        c.name === known || c.name.startsWith(known)
      );
    });

    if (unknownCookies.length > 0) {
      const unknownNames = unknownCookies.map(c => `${c.name} (domain: ${c.domain}, expires: ${c.expires})`);
      console.error('Unknown cookies detected:', unknownNames);

      // Write to report file for review
      fs.writeFileSync(
        'test-results/unknown-cookies.json',
        JSON.stringify(unknownCookies, null, 2)
      );
    }

    expect(unknownCookies, `Unknown cookies found: ${unknownCookies.map(c => c.name).join(', ')}`).toHaveLength(0);
  });
});
```

### Test 6: GPC Signal Handling

```javascript
// tests/cookie-consent/gpc-signal.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Global Privacy Control Signal', () => {
  test('GPC signal triggers automatic opt-out for California users', async ({ browser }) => {
    // Create context with GPC header
    const context = await browser.newContext({
      extraHTTPHeaders: {
        'Sec-GPC': '1',
      },
      locale: 'en-US',
      geolocation: { latitude: 34.0522, longitude: -118.2437 }, // Los Angeles
      permissions: ['geolocation'],
    });

    const page = await context.newPage();
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify advertising cookies are not set
    const cookies = await context.cookies();
    const adCookies = cookies.filter(c =>
      c.name === '_fbp' || c.name === '_gcl_au' || c.name.startsWith('IDE')
    );

    expect(adCookies, 'Advertising cookies set despite GPC signal').toHaveLength(0);

    await context.close();
  });
});
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow

```yaml
name: Cookie Consent Compliance Tests
on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6 AM UTC

jobs:
  cookie-consent-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Run cookie consent tests
        run: npx playwright test tests/cookie-consent/
        env:
          BASE_URL: ${{ vars.STAGING_URL }}

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: cookie-consent-test-results
          path: |
            test-results/
            playwright-report/

      - name: Post results to Slack
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "Cookie consent tests FAILED on ${{ github.ref }}. Review: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_PRIVACY_WEBHOOK }}
```

## Key Legal and Technical References

- **ePrivacy Directive 2002/58/EC, Article 5(3)** — Legal requirement that automated tests verify
- **CJEU Case C-673/17 (Planet49)** — Active consent requirements validated by banner interaction tests
- **CNIL Deliberation No. 2020-091** — Equal prominence requirement tested by button size comparison
- **CCPA/CPRA Cal. Civ. Code §1798.135(e)** — GPC signal handling tested in GPC test suite
- **Playwright Documentation** — Browser automation framework for cross-browser testing
- **WCAG 2.1 Level AA** — Accessibility requirements tested by keyboard navigation tests
- **Google Consent Mode Documentation** — Consent state parameters validated in tag firing tests