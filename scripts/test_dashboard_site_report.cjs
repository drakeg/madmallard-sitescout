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
  let operatorToken = null;
  let requiresToken = false;
  let authorizedUrlRequests = 0;
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
      return { href: '', download: '', children: [], textContent: '',
        click() { downloads.push({ href: this.href, download: this.download }); },
        remove() {}, append(...items) { this.children.push(...items); } };
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
      if (url === '/api/remediation_review') {
        const body=JSON.parse(config.body);
        assert.match(body.csv,/Needs review/);
        return {ok:true,json:async()=>({review:{
          total:1, counts:{needs_review:1,in_progress:0,implemented:0,deferred:0},
          evidence_label:'Self-reported progress; implementation and live effectiveness not independently verified'
        }})};
      }
      if (url === '/api/checklist_review') {
        const supplied = JSON.parse(config.body);
        assert.ok(supplied.csv.includes('Not tested'), 'Must submit selected CSV content');
        return { ok: true, json: async () => ({ review: {
          total_tests: 1, counts: { not_tested: 1, passed: 0, failed: 0, blocked: 0 },
          evidence_label: 'Self-reported by reviewer; not independently verified',
        } }) };
      }
      if (url === '/api/url_report') {
        const payload=JSON.parse(config.body);
        assert.equal(payload.authorized,true);
        assert.equal(payload.url,'https://sample.example/');
        if(requiresToken&&!config.headers.Authorization)return {status:401,ok:false,json:async()=>({error:'Token required'})};
        if(requiresToken)assert.equal(config.headers.Authorization,'Bearer transient-secret');
        else assert.equal(config.headers.Authorization,undefined);
        authorizedUrlRequests++;
        return {status:200,ok:true,json:async()=>({report:{
          page_count:1,site_hostname:'sample.example',uncaptured_internal_links:['https://sample.example/contact'],
          candidate_contact_booking_pages:[],functional_requirements:{forms_to_test:[]},
          remediation_plan:{findings:[]},
        },capture_scope:'One requested public HTTPS page; no crawling or form submissions'})};
      }
      if (url === '/api/site_report') {
        responses.push(JSON.parse(config.body));
        return { ok: true, json: async () => ({ report: { page_count: responses.at(-1).length,
          pages:[{url:'https://sample.example/',title:'Sample Company',meta_description:'Services and quotes',
            html_language:'en',viewport:'width=device-width,initial-scale=1',headings:[{level:'h1',text:'Welcome'}],
            images:[{src:'https://sample.example/img.png',alt:''}],internal_links:['https://sample.example/contact'],
            external_links:[],forms:[]}],
          forms:[{page:'https://sample.example/contact',action:'/submit',method:'POST',
            fields:[{name:'email',type:'email',required:true}],verified_delivery:false}],
          functional_requirements: { forms_to_test: [{
            page: '=HYPERLINK("untrusted")',
            action: 'https://example.org/?q="hello",world',
            method: 'POST',
            required_fields: ['email'],
            test_cases: ['Submit valid form, verify "receipt"'],
          }] },
          review_guidance:{recommended_next_steps:[{priority:'high',
            title:'Verify inquiry delivery',why:'<img src=x onerror=alert(1)>',
            next_action:'Submit a synthetic test',evidence:['https://sample.example/contact'],
            status:'Not verified'}]},
          remediation_plan: { findings: [{
            code: 'missing-title', priority: 'high', page: '=HYPERLINK("bad")',
            evidence: '<script>alert("untrusted")</script>', recommendation: 'Add descriptive title',
            verification: 'Inspect rendered title'
          }] }
        } }) };
      }
      throw new Error('Unexpected network call: ' + url);
    },
    confirm: () => false, prompt: () => operatorToken, console,
  };
  vm.runInNewContext(script, ctx, { filename: 'dashboard-inline.js' });

  const liveForm=element('url-analysis-form');
  const liveResult=element('url-analysis-results');
  element('website-url').value='http://sample.example/';
  element('url-authorized').checked=true;
  await liveForm.listeners.submit({preventDefault(){}});
  assert.match(liveResult.textContent,/public HTTPS URL/);
  assert.equal(authorizedUrlRequests,0);
  element('website-url').value='https://sample.example/';
  element('url-authorized').checked=false;
  await liveForm.listeners.submit({preventDefault(){}});
  assert.match(liveResult.textContent,/Confirm you are authorized/);
  assert.equal(authorizedUrlRequests,0);
  element('url-authorized').checked=true;
  await liveForm.listeners.submit({preventDefault(){}});
  assert.equal(authorizedUrlRequests,1,'Trusted LAN mode should not prompt for token');
  assert.match(liveResult.textContent,/Analyzed 1 authorized HTTPS page/);
  requiresToken=true;
  operatorToken=null;
  await liveForm.listeners.submit({preventDefault(){}});
  assert.match(liveResult.textContent,/requires a capture token/);
  assert.equal(authorizedUrlRequests,1);
  operatorToken='transient-secret';
  await liveForm.listeners.submit({preventDefault(){}});
  assert.equal(authorizedUrlRequests,2);
  assert.match(liveResult.textContent,/Analyzed 1 authorized HTTPS page/);
  assert.match(element('site-report-highlights').textContent,/Pages analyzed: 1/);
  assert.equal(element('site-report-export').disabled,false);
  operatorToken=null;
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
  assert.equal(element('site-next-actions').children.length,1);
  const nextAction=element('site-next-actions').children[0];
  assert.match(nextAction.children[0].textContent,/Verify inquiry delivery/);
  assert.match(nextAction.children[1].textContent,/<img src=x onerror=alert\(1\)>/);
  assert.equal(nextAction.innerHTML,undefined,'Untrusted next-step text must not become HTML');

  assert.equal(element('site-pages-detail').children.length,1);
  const pageSummary=element('site-pages-detail').children[0];
  assert.match(pageSummary.children[1].textContent,/Page title: Sample Company/);
  assert.match(pageSummary.children[1].textContent,/Description: Services and quotes/);
  assert.match(pageSummary.children[2].textContent,/Mobile viewport/);
  assert.equal(element('site-forms-detail').children.length,1);
  assert.match(element('site-forms-detail').children[0].children[1].textContent,/email \(email, required\)/);
  assert.match(element('site-coverage-detail').textContent,/not a browser test/);

  assert.match(element('site-report-highlights').textContent, /Forms needing delivery tests: 1/);
  assert.match(element('site-report-highlights').textContent, /remain unverified/);
  const remediation=element('site-remediation-findings');
  assert.equal(remediation.children.length, 1);
  const entry=remediation.children[0].children[0];
  assert.match(entry.children[0].textContent, /HIGH.*missing-title/);
  assert.match(entry.children[1].textContent, /=HYPERLINK/);
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
  assert.equal(element('site-remediation-export').disabled, false);
  element('site-remediation-export').listeners.click();
  assert.equal(downloads[2].download, 'sitescout-remediation-action-plan.csv');
  const actionsCSV=await urls[2].text();
  assert.match(actionsCSV, /"Priority","Finding","Page URL"/);
  assert.ok(actionsCSV.includes("\"'=HYPERLINK(\"\"bad\"\")\""), 'Malicious formula must be quoted as text');
  assert.match(actionsCSV, /"Needs review"/);
  assert.match(actionsCSV, /"Manual verification"/);
  assert.equal(element('site-printable-export').disabled, false);
  element('site-printable-export').listeners.click();
  assert.equal(downloads[3].download, 'sitescout-printable-client-report.html');
  const printable=await urls[3].text();
  assert.match(printable, /Content-Security-Policy/);
  assert.match(printable, /Live navigation, accessibility compliance/);
  assert.match(printable, /Forms requiring human verification/);
  assert.match(printable, /Page-by-page evidence/);
  assert.match(printable,/Recommended next steps for the site owner/);
  assert.match(printable,/&lt;img src=x onerror=alert\(1\)&gt;/);

  assert.match(printable, /Sample Company/);
  assert.match(printable, /Detected form implementation details/);
  assert.match(printable, /email \(email, required\)/);

  assert.ok(printable.includes('&lt;script&gt;alert(&quot;untrusted&quot;)&lt;/script&gt;'),
    'Untrusted strings must be escaped as text');
  assert.ok(!printable.includes('<script>'), 'Downloaded report must never include executable script');



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

  const remediationFile=element('site-remediation-review-file');
  const remediationButton=element('review-site-remediation');
  await remediationButton.listeners.click();
  assert.match(element('site-remediation-review-results').textContent,/Select an updated/);
  remediationFile.files=[{size:99,text:async()=> 'Review status\\nNeeds review\\n'}];
  await remediationButton.listeners.click();
  const progress=JSON.parse(element('site-remediation-review-results').textContent);
  assert.equal(progress.counts.needs_review,1);
  assert.match(progress.evidence_label,/not independently verified/);
  remediationFile.files=[{size:512001,text:async()=>{throw Error('oversized file read')}}];
  await remediationButton.listeners.click();
  assert.match(element('site-remediation-review-results').textContent,/exceeds/);

  element('site-report-json').listeners.input();
  assert.equal(element('site-pages-detail').children.length,0);
  assert.equal(element('site-next-actions').children.length,0);
  assert.equal(element('site-forms-detail').children.length,0);
  assert.match(element('site-coverage-detail').textContent,/No live or saved report/);

  assert.match(element('site-report-highlights').textContent, /Analyze saved pages/);
  assert.equal(element('site-remediation-findings').children.length, 1);
  assert.match(element('site-remediation-findings').children[0].textContent, /No remediation/);
  assert.equal(element('site-report-export').disabled, true);
  assert.equal(element('site-report-checklist-export').disabled, true);
  assert.equal(element('site-remediation-export').disabled, true);
  assert.equal(element('site-printable-export').disabled, true);
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
