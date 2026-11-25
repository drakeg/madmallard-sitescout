// Browser-free integration test for SiteScout's report import/analyze/export flow.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

async function main() {
  const html = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
  const script = html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
  assert.ok(script, 'Dashboard script should exist');
  const events = new Map();
  const elements = new Map();
  const downloads = [];
  const urls = [];
  const responses = [];
  function element(id) {
    if (!elements.has(id)) {
      elements.set(id, {
        value: '', disabled: id === 'site-report-export', textContent: '',
        files: [], listeners: {},
        addEventListener(name, fn) { this.listeners[name] = fn; },
        requestSubmit() { return this.listeners.submit?.({ preventDefault() {} }); },
        children: [], replaceChildren() { this.children = []; },
        append(...items) { this.children.push(...items); },
      });
    }
    return elements.get(id);
  }
  const document = {
    getElementById: element,
    body: { append() {} },
    createElement() {
      return { href: '', download: '', click() { downloads.push({ href: this.href, download: this.download }); }, remove() {}, append() {} };
    },
    createTextNode(text) { return { text }; },
  };
  const ctx = {
    document, TextEncoder, Blob,
    URL: {
      createObjectURL(blob) { urls.push(blob); return 'blob:test-report'; },
      revokeObjectURL(url) { assert.equal(url, 'blob:test-report'); },
    },
    fetch: async (url, config) => {
      if (url === '/api/health') return { ok: true, json: async () => ({ status: 'ok' }) };
      if (url === '/api/checklist_review') {
        const supplied = JSON.parse(config.body);
        assert.ok(supplied.csv.includes('Not tested'), 'Must submit selected CSV content');
        return { ok: true, json: async () => ({ review: {
          total_tests: 1, counts: { not_tested: 1, passed: 0, failed: 0, blocked: 0 },
          evidence_label: 'Self-reported by reviewer; not independently verified',
        } }) };
      }
      if (url === '/api/site_report') {
        responses.push(JSON.parse(config.body));
        return { ok: true, json: async () => ({ report: { page_count: responses.at(-1).length,
          functional_requirements: { forms_to_test: [{
            page: '=HYPERLINK("untrusted")',
            action: 'https://example.org/?q="hello",world',
            method: 'POST',
            required_fields: ['email'],
            test_cases: ['Submit valid form, verify "receipt"'],
          }] },
          remediation_plan: { findings: [{
            code: 'missing-title', priority: 'high', page: '<b>untrusted</b>',
            evidence: 'No HTML title', recommendation: 'Add descriptive title',
            verification: 'Inspect rendered title'
          }] }
        } }) };
      }
      throw new Error('Unexpected network call: ' + url);
    },
    confirm: () => false, prompt: () => null, console,
  };
  vm.runInNewContext(script, ctx, { filename: 'dashboard-inline.js' });

  const manifest = [
    { url: 'https://sample.example/', html: '<h1>Home</h1><a href="/contact">Contact</a>' },
    { url: 'https://sample.example/contact', html: '<h1>Contact</h1><form action="/submit"></form>' },
  ];
  const file = element('site-report-file');
  file.files = [{ size: 120, text: async () => JSON.stringify(manifest) }];
  await file.listeners.change({ target: file });
  assert.equal(JSON.parse(element('site-report-json').value).length, 2);
  assert.match(element('site-report-results').textContent, /Manifest imported/);
  assert.equal(element('site-report-export').disabled, true);

  await element('site-report-form').listeners.submit({ preventDefault() {} });
  assert.equal(responses.length, 1);
  assert.equal(element('site-report-export').disabled, false);
  assert.equal(JSON.parse(element('site-report-results').textContent).page_count, 2);
  assert.match(element('site-report-highlights').textContent, /Pages analyzed: 2/);
  assert.match(element('site-report-highlights').textContent, /Forms needing delivery tests: 1/);
  assert.match(element('site-report-highlights').textContent, /remain unverified/);
  const remediation=element('site-remediation-findings');
  assert.equal(remediation.children.length, 1);
  const entry=remediation.children[0].children[0];
  assert.match(entry.children[0].textContent, /HIGH.*missing-title/);
  assert.match(entry.children[1].textContent, /<b>untrusted<\/b>/);
  assert.equal(remediation.innerHTML, undefined, 'Remediation display must use safe DOM text nodes');


  element('site-report-export').listeners.click();
  assert.equal(downloads.length, 1);
  assert.equal(downloads[0].download, 'sitescout-site-report.json');
  assert.equal(JSON.parse(await urls[0].text()).functional_requirements.forms_to_test.length, 1);
  assert.equal(element('site-report-checklist-export').disabled, false);
  element('site-report-checklist-export').listeners.click();
  assert.equal(downloads[1].download, 'sitescout-form-verification-checklist.csv');
  const csv=await urls[1].text();
  assert.match(csv, /"Page URL","Form action","Method"/);
  assert.ok(csv.includes("\"'=HYPERLINK(\"\"untrusted\"\")\""), 'Formula-like cell must be escaped');
  assert.ok(csv.includes("\"Submit valid form, verify \"\"receipt\"\"\""), 'CSV quotes and commas must be escaped');
  assert.match(csv, /"Not tested"/);

  const reviewFile=element('site-checklist-file');
  const reviewButton=element('review-site-checklist');
  await reviewButton.listeners.click();
  assert.match(element('site-checklist-review-results').textContent, /Select a completed/);
  reviewFile.files=[{ size: 100, text: async () => 'Status,Observed result\\nNot tested,\\n' }];
  await reviewButton.listeners.click();
  const review=JSON.parse(element('site-checklist-review-results').textContent);
  assert.equal(review.counts.not_tested, 1);
  assert.match(review.evidence_label, /not independently verified/);
  reviewFile.files=[{ size: 600000, text: async () => { throw new Error('Oversized file was read'); } }];
  await reviewButton.listeners.click();
  assert.match(element('site-checklist-review-results').textContent, /exceeds/);

  element('site-report-json').listeners.input();
  assert.match(element('site-report-highlights').textContent, /Analyze saved pages/);
  assert.equal(element('site-remediation-findings').children.length, 1);
  assert.match(element('site-remediation-findings').children[0].textContent, /No remediation/);
  assert.equal(element('site-report-export').disabled, true);
  assert.equal(element('site-report-checklist-export').disabled, true);
  file.files = [{ size: 2100001, text: async () => { throw new Error('Too large file was read'); } }];
  await file.listeners.change({ target: file });
  assert.match(element('site-report-results').textContent, /exceeds/);
  file.files = [{ size: 8, text: async () => '{broken' }];
  await file.listeners.change({ target: file });
  assert.match(element('site-report-results').textContent, /Could not import manifest/);
  assert.equal(element('site-report-json').value, '');
  console.log('Site report browser flow: import, submit, export, stale state, oversize and malformed input passed');
}

main().catch(error => { console.error(error); process.exitCode = 1; });
