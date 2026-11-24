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
        replaceChildren() {}, append() {},
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
      if (url === '/api/site_report') {
        responses.push(JSON.parse(config.body));
        return { ok: true, json: async () => ({ report: { page_count: responses.at(-1).length, functional_requirements: { forms_to_test: [] } } }) };
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

  element('site-report-export').listeners.click();
  assert.equal(downloads.length, 1);
  assert.equal(downloads[0].download, 'sitescout-site-report.json');
  assert.deepEqual(JSON.parse(await urls[0].text()), { page_count: 2, functional_requirements: { forms_to_test: [] } });

  element('site-report-json').listeners.input();
  assert.equal(element('site-report-export').disabled, true);
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
