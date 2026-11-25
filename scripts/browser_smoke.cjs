/* Real Chromium end-to-end smoke against the locally served SiteScout dashboard.
 * External websites are NEVER contacted; URL analysis is mocked at the
 * network boundary with fictional site data. This is not live-site QA.
 */
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

async function main() {
  const origin = process.env.SITESCOUT_BROWSER_URL || 'http://127.0.0.1:8087';
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ acceptDownloads: true });
    page.setDefaultTimeout(10000);
    await page.route('**/api/url_report', async route => {
      const req = route.request();
      const body = req.postDataJSON();
      assert.equal(body.url, 'https://sample.example/');
      assert.equal(body.authorized, true);
      assert.equal(req.headers().authorization, undefined, 'Trusted browser should not send a token');
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          report: {
            site_hostname: 'sample.example',
            page_count: 2,
            pages: [
              { url: 'https://sample.example/', title: 'Sample Home',
                meta_description: 'Sample description', html_language: 'en',
                viewport: 'width=device-width, initial-scale=1',
                headings: [{ level: 'h1', text: 'Welcome' }],
                images: [{src: 'https://sample.example/hero.jpg', alt: ''}],
                forms: [], internal_links: ['https://sample.example/contact'], external_links: [] },
              { url: 'https://sample.example/contact', title: 'Contact',
                meta_description: '', html_language: 'en',
                viewport: '', headings: [{ level: 'h1', text: 'Get in touch' }],
                images: [], forms: [{ method: 'POST',
                  action: 'https://sample.example/send',
                  fields: [{ name: 'email', type: 'email', required: true }] }],
                internal_links: [], external_links: [] },
            ],
            forms: [{ page: 'https://sample.example/contact',
              method: 'POST', action: 'https://sample.example/send',
              fields: [{ name: 'email', type: 'email', required: true }],
              verified_delivery: false }],
            uncaptured_internal_links: [],
            candidate_contact_booking_pages: ['https://sample.example/contact'],
            functional_requirements: { forms_to_test: [{
              page: 'https://sample.example/contact',
              action: 'https://sample.example/send', method: 'POST',
              required_fields: ['email'], test_cases: ['Verify synthetic delivery'] }] },
            remediation_plan: { findings: [{
              code: 'missing-viewport', priority: 'medium',
              page: 'https://sample.example/contact',
              evidence: 'No viewport tag in saved HTML',
              recommendation: 'Add a responsive viewport',
              verification: 'Confirm with a mobile browser' }] },
            review_guidance: { recommended_next_steps: [{
              title: 'Verify inquiry delivery', priority: 'high',
              why: 'A static form was detected without a receipt test',
              next_action: 'Test with a permitted synthetic inquiry',
              evidence: ['https://sample.example/contact'], status: 'Not verified' }] },
            capture_discovery: { max_pages: 3, additional_page_failures: [] },
          },
        }),
      });
    });
    const response = await page.goto(origin, { waitUntil: 'domcontentloaded' });
    assert.equal(response.status(), 200);
    assert.equal(await page.locator('#how-it-works').innerText(), 'What SiteScout actually does');
    assert.match(await page.locator('main').innerText(), /Not tested:/);
    await page.locator('#website-url').fill('https://sample.example/');
    await page.locator('#url-authorized').check();
    await page.locator('#analyze-website-url').click();
    await page.locator('#url-analysis-results').getByText('Analyzed 2 authorized HTTPS page(s)', { exact: false }).waitFor();
    assert.equal(await page.locator('#site-pages-detail article').count(), 2);
    assert.equal(await page.locator('#site-forms-detail article').count(), 1);
    assert.equal(await page.locator('#site-next-actions article').count(), 1);
    assert.match(await page.locator('#site-coverage-detail').innerText(), /not a browser test/);
    assert.match(await page.locator('#site-remediation-findings').innerText(), /Missing mobile viewport declaration/);
    assert.equal(await page.locator('#site-report-export').isEnabled(), true);
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.locator('#site-printable-export').click(),
    ]);
    assert.equal(download.suggestedFilename(), 'sitescout-printable-client-report.html');
    const fs = require('node:fs');
    const printable = fs.readFileSync(await download.path(), 'utf8');
    assert.match(printable, /Page-by-page evidence/);
    assert.match(printable, /Recommended next steps for the site owner/);
    assert.match(printable, /Delivery: NOT TESTED/);
    await page.locator('#advanced-html-analysis summary').click();
    assert.equal(await page.locator('#analyzer').isVisible(), true);
    await page.locator('#site-report-json').fill('[]');
    assert.equal(await page.locator('#site-report-export').isDisabled(), true);
    assert.equal(await page.locator('#site-next-actions article').count(), 0);
    console.log('Chromium SiteScout smoke: URL submission, report evidence, form inventory, next steps, download, advanced mode and reset passed');
    await page.close();
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
