# Mad Mallard SiteScout

[![License](https://img.shields.io/github/license/drakeg/madmallard-sitescout)](https://github.com/drakeg/madmallard-sitescout/blob/main/LICENSE)


<!-- badges:start -->
[![Python 3.15](https://img.shields.io/badge/Python-3.15-3776AB?logo=python&logoColor=white)](Dockerfile)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](compose.yaml)
[![Vercel](https://img.shields.io/badge/Vercel-Deployment-000000?logo=vercel&logoColor=white)](vercel.json)

[![CI](https://github.com/drakeg/madmallard-sitescout/actions/workflows/ci.yml/badge.svg)](https://github.com/drakeg/madmallard-sitescout/actions/workflows/ci.yml)
[![Real browser QA](https://github.com/drakeg/madmallard-sitescout/actions/workflows/browser-qa.yml/badge.svg)](https://github.com/drakeg/madmallard-sitescout/actions/workflows/browser-qa.yml)
[![Open issues](https://img.shields.io/github/issues/drakeg/madmallard-sitescout)](https://github.com/drakeg/madmallard-sitescout/issues)
[![Open PRs](https://img.shields.io/github/issues-pr/drakeg/madmallard-sitescout)](https://github.com/drakeg/madmallard-sitescout/pulls)
<!-- badges:end -->

Free-software-first platform for evaluating existing small-business websites, producing **functional** redesign concepts, and preparing permission-conscious sales previews.

## Principles
- GitHub-hosted tools; self-hostable; no mandatory paid AI API.
- Verify each dependency's **commercial license**, local inference compatibility, and runtime terms before adoption.
- Do not clone proprietary content or impersonate businesses. Use authorized content and original/licensed assets.
- No unsolicited messages or public previews without human approval.
- Functional parity before visual polish: forms, navigation, booking integrations, and mobile behavior need end-to-end tests.
- Isolate untrusted websites and generated code; never expose secrets to browser workers.

## Quick start
```sh
cp .env.example .env
docker compose up --build -d
curl http://localhost:8087/health
```
The Docker dashboard now binds to `0.0.0.0:8087` by default for access from devices on a **trusted LAN**. For loopback-only access set `SITESCOUT_BIND=127.0.0.1`. Do not forward this port to the public Internet.

## Status
Working offline HTML and multi-page site report dashboard with import/export, evidence-based form checklists and manual CSV review. A protected, **default-off Docker-only** capture queue and opt-in worker also exist for trusted environments. SiteScout is **not yet a website generator**, and enabled live capture is not approved for public Internet deployment. See [SPRINTS.md](SPRINTS.md), [BACKLOG.md](BACKLOG.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [RELEASES.md](RELEASES.md).

## Candidate GitHub tools
[Open Lovable](https://github.com/firecrawl/open-lovable), [OpenPage](https://github.com/buildingopen/openpage), [Onlook](https://github.com/onlook-dev/onlook), [OpenCode](https://github.com/anomalyco/opencode), [Ollama](https://github.com/ollama/ollama), [Astro](https://github.com/withastro/astro), [Playwright](https://github.com/microsoft/playwright), [axe-core](https://github.com/dequelabs/axe-core). **Candidates only**: no license/runtime approval implied.

## Sprint 1: saved-page inventory
Analyze an HTML page you are authorized to inspect, with **no network access**:
```sh
python3 -m app.inventory fixtures/demo.html --url https://example.com/
```
Outputs JSON describing title, headings, links, images, forms and unresolved functionality. It does not crawl websites, execute JavaScript, or verify external services.

## Optimist Hall pilot
The public [Optimist Hall tenant directory](https://www.optimisthall.com/tenants) is the real-world reference for our directory workflow. See [docs/OPTIMIST_HALL_PILOT.md](docs/OPTIMIST_HALL_PILOT.md). Try the offline extractor on a **synthetic** fixture:
```sh
python3 -m app.directory fixtures/food-hall-directory.html --url https://www.optimisthall.com/tenants
```
All results are unverified external links requiring review; no network requests are made.

## Web dashboard deployment

The root `index.html` is the static dashboard for Vercel; `api/health.py` is its Python serverless health function. `vercel.json` aliases `/health` to `/api/health`. Deploy the repository root as an **Other** framework with no custom output directory or build command. Verify `/`, `/api/health`, and `/health` after deployment. Vercel does not run the local Docker/AI worker containers.

For Docker, use `docker compose up -d --build` and visit `http://HOST_LAN_IP:8087/` from a device on your trusted network, or `http://127.0.0.1:8087/` on the host. The same dashboard and health routes are served by the Python container. Do not expose unauthenticated future worker controls to the public internet.

## Browser-based offline analysis

Open the dashboard, select **Website inventory** or **Directory candidates**, provide the original source URL, and paste saved HTML (maximum 500 KiB). The dashboard POSTs to `/api/analyze` and renders structured JSON. Both Vercel and Docker use the same pure Python parser. **No arbitrary URL fetching, external API calls, persistent storage, or prospect outreach occurs.** This is an early-stage inspection tool, not a live crawler.

### Explainable results and examples

The dashboard includes two self-contained example HTML snippets, one for a page inventory and one for directory discovery. Selecting either loads and submits the example; no external site is fetched. Findings describe only what static HTML supports (such as missing titles, headings and image alternatives) and explicitly distinguish untested behavior. The JSON result remains available for inspection.

### Opt-in live capture (Docker only)

On a **trusted, access-controlled Docker host**, set `SITESCOUT_CAPTURE_ENABLED=true` in your environment and rebuild the container. The dashboard then offers an explicit-confirmation capture action for authorized **public HTTPS** pages. The Docker-only `POST /api/capture` endpoint is disabled by default and is **not available on Vercel**. It resolves DNS, rejects non-public addresses, pins the resolved public IP for the TLS connection, validates certificates, follows no redirects, limits HTML to 500 KiB and times out after eight seconds. It does not run JavaScript, crawl links, store data or bypass authentication. **Do not expose an enabled capture endpoint to the public Internet**; add authentication and rate limiting before any shared deployment.

### Docker capture access controls

Capture remains **disabled by default**. To enable on a trusted Docker test host, set `SITESCOUT_CAPTURE_ENABLED=true` and a randomly generated `SITESCOUT_CAPTURE_TOKEN` (minimum 24 characters) in the untracked `.env`. Example generation: `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'`. Rebuild with `docker compose up -d --build`. The dashboard prompts for this token only when capturing; it is sent in an Authorization header and not persisted by the UI. A single-worker in-memory throttle allows five authorized captures per minute; the token is mandatory, even when the endpoint is enabled. The API returns 401, 429 or 503 for unauthorized, throttled or misconfigured requests. **Do not expose the enabled capture endpoint publicly:** a browser-held token and process-local throttle are not substitutes for a proper user-authenticated queue, HTTPS termination, and durable abuse logging. On LAN, use a trusted private network and TLS proxy before sending credentials.

### Durable capture job infrastructure (development only)

`app/capture_jobs.py` provides a SQLite-backed **metadata-only** queue, per-actor admission limiting, owner-scoped lookups, lifecycle audit records and completed-job pruning. It records target URLs and actor identifiers but deliberately never stores raw HTML, credentials or unsanitized exception text. SQLite database paths must live on a persistent, access-controlled volume once the worker is integrated. **The store is not connected to `/api/capture` yet** and does not provide user sessions, API job endpoints or public-safe deployment; the current Docker capture route remains a protected, default-off single-worker prototype. Run `python -m unittest discover -s tests -v` for the offline tests.

### Capture worker prototype (not connected to HTTP)

`app/capture_worker.py` processes one persisted job per call using the existing HTTPS capture and HTML analyzer with injected test doubles. It returns a result to the trusted caller but **does not persist captured HTML or analysis output**. Normal capture failures are recorded without error details; unexpected programming errors are audited and re-raised. `CaptureJobStore.recover_stale(before=...)` can requeue interrupted jobs only when an operator has established that no previous worker is still processing them. Neither this worker nor the SQLite queue is automatically started in Docker, and no new API endpoints or public-capture permissions are enabled. Multi-worker leases, sessions, durable results, persistent volume and TLS are still required before public deployment.

### Opt-in private worker CLI (SS-021 incremental)

An isolated, manual Docker Compose profile now supplies a **persistent SQLite volume** for capture-job metadata without exposing an HTTP job API. The operator must control local Docker access; `--actor` is an operator-supplied audit label, **not an authenticated user session**. Keep `SITESCOUT_CAPTURE_ENABLED=false` unless performing an explicitly authorized capture on a trusted machine. Example trusted-host operations after setting `SITESCOUT_CAPTURE_ENABLED=true` in a local, untracked `.env`:

```sh
docker compose --profile capture-worker run --rm capture-worker submit --actor operator --url https://example.org/ --authorized
docker compose --profile capture-worker run --rm capture-worker work-once
docker compose --profile capture-worker run --rm capture-worker status --actor operator --job-id JOB_ID
docker compose --profile capture-worker run --rm capture-worker audit --actor operator --job-id JOB_ID
docker compose --profile capture-worker run --rm capture-worker prune --older-than-days 7
```

The `capture-jobs` volume survives container replacement; it stores URLs, audit actor labels and lifecycle data, **not HTML or analysis results**. CLI execution is one job at a time and does not start automatically. The separate dashboard still uses the prior private bearer-token capture path; it does **not** enqueue jobs. Output deliberately excludes captured HTML. Docker host access is privileged and must remain trusted. The worker requires outbound DNS/HTTPS access. Public or multi-user deployment still requires authenticated sessions, ownership binding, bounded workers/leases, TLS termination and durable protected results. For local verification run `python -m unittest discover -s tests -v` and `docker compose --profile capture-worker config`.

### Exclusive single-host worker safety

The manual `work-once` command now holds a nonblocking advisory `flock` on `/data/capture_jobs.sqlite3.worker.lock` throughout processing. Competing worker processes sharing the same local volume fail closed rather than claiming another job. Operators can explicitly requeue interrupted work with `docker compose --profile capture-worker run --rm capture-worker recover --older-than-seconds 120`; recovery also requires the exclusive lock and a minimum 60-second threshold. A lock file remains in the volume; do not delete it while jobs are running. These guarantees apply to **one host and one shared local filesystem only**. Recovery is not automatically scheduled, and this does not provide distributed worker fencing, identity sessions or an HTTP job API. Operator must ensure any previously crashed worker is no longer running before recovery.

### Private operator job listing

Use `docker compose --profile capture-worker run --rm capture-worker list --actor operator --limit 25` to inspect the newest jobs for an operator audit label. The response contains job IDs, modes, states and timestamps, but not captured HTML or target URLs. Lists are capped at 100 records; this is a trusted-local CLI, not an identity-bound public API. Treat actor labels as untrusted until authenticated sessions are introduced.

### Opt-in local analysis JSON export

For a trusted-host, authorized job, run `docker compose --profile capture-worker run --rm capture-worker work-once --save-results` to store analyzed JSON under `/data/results/JOB_ID.json` on the persistent `capture-jobs` volume. Result export is **opt-in**; normal `work-once` still discards the result. Export files are created with exclusive-create semantics and mode `0600` in an owner-private `0700` directory, capped at 256 KiB per result. Duplicate IDs cannot overwrite existing files. An export failure marks the job failed rather than claiming that a durable result exists. These reports may contain sensitive third-party page text; only authorized Docker host operators should inspect, retain or delete them. They are **not accessible via the HTTP dashboard or CLI status**, and the existing completed-job pruning does not delete exported files. Operators must manually review retention and file cleanup. Public sessions, secure customer delivery, automated retention and multi-host fencing remain blocked.

### Expiring protected result exports

Run `docker compose --profile capture-worker run --rm capture-worker prune-results --older-than-days 7` from a trusted host to remove expired exported JSON files from `/data/results`. This is **manual** and separate from `prune`, which only removes SQLite job metadata. Cleanup holds the worker lock, only processes regular files named as SiteScout job IDs, skips symlinks and unrelated files, and refuses a results directory accessible to other users. The command never deletes recent files. Automatic retention scheduling remains disabled until operator policies and worker lifecycle controls are implemented.

### Future operator identity foundation (not wired to HTTP)

`app/operator_auth.py` validates a JSON mapping of operator IDs to lowercase SHA-256 bearer-token digests from `SITESCOUT_OPERATOR_TOKEN_HASHES`. Operators must generate unpredictable 32+-character random tokens and configure **only their hashes** on the private server; token values must never be committed or logged. For example, calculate a digest locally using `python -c 'import hashlib,getpass; print(hashlib.sha256(getpass.getpass("Token: ").encode()).hexdigest())'`. The configuration defaults to fail-closed; duplicate hashes, invalid names and malformed JSON are rejected. This standalone foundation does **not** replace the current trusted Docker capture token, configure public TLS, or enable HTTP job routes. Trusted local CLI actor labels are still not authenticated. Future HTTP integration must bind the derived identity to job ownership, require TLS, enforce queue limits and prevent credential leakage.

### Experimental authenticated Docker job API (default off)

The trusted-host Docker server can now accept jobs into the persistent private SQLite queue. **Disabled by default**; enable only when `SITESCOUT_CAPTURE_ENABLED=true`, `SITESCOUT_JOBS_ENABLED=true` and `SITESCOUT_OPERATOR_TOKEN_HASHES` contains a JSON object mapping operator labels to lowercase SHA-256 digests of high-entropy tokens. The bearer token identifies the actor on the server; client-provided actor names are ignored. This experiment is **not a production session system** and must remain bound to localhost or a restricted trusted network protected by TLS. Never send bearer tokens over unencrypted LAN HTTP, publish the endpoint on the Internet or commit tokens.

Available Docker-only endpoints: `POST /api/jobs` with JSON `{"url":"https://example.org","mode":"inventory","authorized":true}` returns an accepted job ID; `GET /api/jobs` lists the authenticated operator's redacted metadata, `GET /api/jobs/JOB_ID` shows status, and `GET /api/jobs/JOB_ID/audit` displays sanitized lifecycle events. All endpoints require `Authorization: Bearer TOKEN`. Submission validates the public HTTPS destination and enforces the shared SQLite queue/actor limits; disabled/misconfigured states fail closed. The existing `/api/capture` endpoint remains independent and default-off; no public job API is deployed on Vercel. Use the private `capture-worker` Compose profile and `work-once` to process queued jobs. Results remain local, and optional protected result export is still only available to trusted Docker operators. Do not mistake local operator tokens for customer sessions, fine-grained authorization, public TLS, or a production-ready deployment.

### Private capture queue controls in dashboard

The dashboard now provides **Queue authorized capture (trusted Docker only)** and **Check queued capture status** buttons. These manually call the Docker-only `/api/jobs` endpoints and prompt for the operator token each time without using browser storage. The queued ID is copied into an editable input so the operator can check status. The worker still must be run separately (`docker compose --profile capture-worker run --rm capture-worker work-once`). The UI deliberately does not fetch or display private result files. The same static HTML may render on Vercel, but the job API does not exist there, so those controls are unavailable. These controls are only for a trusted locally protected Docker setup; do not enable them for public users until TLS, real user sessions and stronger worker isolation are implemented.

Private job submissions require literal `authorized: true` alongside the operator token. Missing, false, or non-boolean assertions are rejected before DNS resolution or queue admission. This records an explicit claim of permission; it is not independent verification of site ownership.

### Experimental owner-scoped capture results

On the **default-off, trusted-host Docker jobs API**, `GET /api/jobs/JOB_ID/result` returns a previously saved analysis JSON only when the authenticated operator owns the job, its state is `succeeded`, and a protected result file exists. For the current manual worker flow, opt in explicitly using `docker compose --profile capture-worker run --rm capture-worker work-once --save-results`; regular `work-once` does not retain results. Missing exports return 404, unfinished jobs return 409, and other operators cannot read the result. Files are read with symlink refusal, private-permission checks, and a 256 KiB cap. **Treat exports as potentially sensitive:** do not enable this route outside a TLS-protected, trusted environment or expose it to the public Internet. Operator tokens are not equivalent to account sessions. Removal still follows the manual retention policy.

### Viewing completed private capture results

After manually processing a queued job with `docker compose --profile capture-worker run --rm capture-worker work-once --save-results`, enter its job ID and click **View completed private result (trusted Docker only)**. The dashboard prompts for an operator token for that request, retrieves only the authenticated owner's completed protected JSON, and renders result data using `textContent` rather than injecting page HTML. No bearer token is saved in browser storage. Results that were not explicitly exported cannot be retrieved, and a job must be completed successfully. This remains **default-off, Docker-only, and unsuitable for public access** without TLS and real account sessions.

### Browsing private recent jobs

The dashboard's **Show my recent private jobs** control calls the default-off Docker-only `GET /api/jobs` endpoint with a freshly requested operator token and displays the server's owner-scoped, redacted metadata. The newest returned job ID is copied into the job-ID field for convenient status/result lookup. Target URLs and captured HTML are not included in the listing and the token is never stored in browser storage. This is a trusted-host operator workflow, not a public multi-user login.

### Opt-in continuous capture runner (trusted Docker only)

The separate `capture-runner` Compose profile runs an optional polling worker which processes explicitly queued authorized jobs and saves successful JSON reports to the protected persistent volume. It is **never started by normal** `docker compose up`. On an access-controlled Docker host, configure `SITESCOUT_CAPTURE_ENABLED=true`, operator tokens, and `SITESCOUT_JOBS_ENABLED=true` in the untracked environment, then start the API and optionally run `docker compose --profile capture-runner up -d capture-runner`. Stop with `docker compose --profile capture-runner stop capture-runner`. The runner checks every three seconds, uses the existing exclusive local-filesystem worker lock, and does not automatically requeue interrupted jobs or retry failed requests. Its restart policy is `no` to avoid unexpected processing after errors. The profile has no exposed ports, uses a non-root read-only container, and is disabled when capture is disabled. Do **not** deploy for publicly accessible multi-user capture: TLS, real user sessions, per-host isolation, resource management and distributed worker fencing remain required.

## Offline multi-page site inventory (SS-003)

Analyze up to **20 authorized, saved HTML pages** from the same site hostname with no network access, JavaScript execution or form submission:

```sh
python -m app.site_report fixtures/site-report.json
```

The JSON manifest is an array of `{"url":"https://site.example/path","html":"<html>…</html>"}` objects. Reports include page titles, headings, internal/external links, form fields/actions, known-page navigation edges, uncaptured internal links and possible paths to saved contact/booking pages. Uncaptured links are **not** reported as broken; a reported form is **not** verified to deliver submissions. Limits: 500 KiB per page, 2 MB total and 20 pages. This is a CLI increment that can later be connected to the web dashboard; it never crawls or contacts a website.

### Browser multi-page saved HTML report

From the SiteScout dashboard, use **Multi-page saved website report**, paste a JSON array containing up to 20 authorized saved pages with `url` and `html` properties, or click **Load three-page demo**. The browser sends only those pasted pages to `POST /api/site_report`, served by the same offline Python implementation on Vercel and Docker. Results show page inventory, navigation edges, uncaptured links, forms and candidate contact/booking paths. The endpoint never visits sites, executes JavaScript or submits forms; report paths are unverified. The request cap is 2.1 MB and the analyzer separately enforces 500 KiB per page and 2 MB total. Reports are not persisted by this endpoint.

### Functional verification checklist (SS-004)

Each multi-page site report now includes `functional_requirements`, listing every saved-page form with its action, HTTP method, field counts, required-field names, and synthetic end-to-end verification cases. Potential external form destinations, HTTP form actions, GET submissions and missing fields are flagged for human review. Contact/booking pages are listed as **candidates**, not confirmed working customer journeys. This feature never submits forms, inspects external CRM settings or asserts that leads are delivered. Use the checklist to plan a paid, permission-based SMB form-delivery verification pilot.

### Import and download multi-page reports

Use **Import saved pages manifest (.json)** to select a JSON file containing the documented array of saved authorized pages. The file is read locally in your browser into the editable manifest field; SiteScout never sends it until you select **Generate site report**. After a successful analysis, **Download report JSON** creates a local `sitescout-site-report.json` file containing the full report, including navigation, forms and functional verification tasks. Editing or reimporting the source disables download until a fresh analysis succeeds. Files exceeding 2.1 MB are rejected before reading, and the Python API still enforces per-page and aggregate HTML limits. The file and report are not saved on the server by this feature. This export is evidence for human review, not proof that contact forms, integrations or navigation work in a live browser.

### Download a form verification checklist (CSV)

After generating a multi-page saved-site report, select **Download form verification checklist CSV**. The spreadsheet lists a separate row for each observed form and each recommended verification test, including the source page, action, HTTP method, required fields, test case, and blank reviewer/observed-result/notes columns. Every status begins **Not tested**: the tool never claims a form was successfully delivered. Open the CSV in a spreadsheet editor, perform agreed synthetic submissions to the real approved destination, and record evidence. The export defends against spreadsheet formula injection by treating risky untrusted HTML-derived cells as text and quotes commas and double quotes correctly. This export is only enabled after a successful offline report; editing the manifest disables stale downloads. The CSV is generated locally in your browser and is not uploaded to SiteScout.

### Trusted-LAN container binding

The API container publishes its dashboard on `0.0.0.0:8087` by default to support development from another device on your local network; configure `SITESCOUT_PORT` for another host port or `SITESCOUT_BIND=127.0.0.1` to restrict to the Docker host. Worker/runner containers publish **no ports**. Both `SITESCOUT_CAPTURE_ENABLED` and `SITESCOUT_JOBS_ENABLED` remain `false` by default. LAN reachability does **not** make the capture/job APIs safe to enable on cleartext HTTP: bearer tokens and downloaded results require HTTPS termination, authenticated access controls, trusted network segmentation and proper operations review before exposure. Do not add public router port forwarding. CI verifies the LAN binding and default-off capture controls.

### Review a completed human verification checklist

After downloading and filling out `sitescout-form-verification-checklist.csv`, choose **Completed verification checklist (.csv)** and **Review completed checklist** in the dashboard. The built-in offline Python parser accepts the template's exact columns and the review statuses **Not tested**, **Passed**, **Failed**, or **Blocked**. For any non-untested status, both Reviewer and Observed result must be filled in. It counts tests by status and provides an actionable follow-up list for failed and blocked cases. Values are **self-reported by the human reviewer, not verified by SiteScout**: a green count must never be sold as proof that emails or CRM submissions arrived without matching external evidence. Max 1,000 rows and 500 KiB of CSV; malformed files are rejected. The CSV is processed on the selected Vercel or Docker endpoint and not stored by this feature. Don't upload customer PII or real lead details; use synthetic test identifiers only.

### Site report overview

Completed multi-page offline reports now present a concise **Report at a glance** line with page count, forms needing delivery tests, uncaptured internal links and candidate contact/booking pages. It uses verified static-analysis counts only and labels live behavior as unverified. Editing or reimporting a manifest immediately clears old metrics and disables stale exports. The detailed raw JSON and the downloadable form-verification CSV remain available.

### Prioritized evidence-based site improvements (SS-046)

The offline multi-page report now includes a `remediation_plan` with prioritized, actionable manual review items. It flags absent HTML titles/H1s, image alternative-text review, explicit HTTP form actions, GET forms containing likely personal-data fields, and uncaptured internal destinations. Every item records evidence, recommended change, a manual verification step, and `Needs review` status. These are **static observations only**, not proof of a live defect, accessibility noncompliance, SEO rankings, broken navigation or failed form delivery. For example, images with empty alt text may be deliberately decorative, and multiple H1 headings are not inherently invalid. The dashboard displays the first ten priorities using safe text nodes; the downloadable full JSON retains all findings (up to a bounded limit).

### Download a remediation action plan

After producing an offline multi-page report, click **Download remediation action plan CSV** for a practical, editable handoff. Each row includes priority, finding, page URL, observed static evidence, recommended fix, manual verification step, initial `Needs review` status, and blank assignee/evidence-link/notes columns. The same spreadsheet formula-injection protections used for form-checklist CSV apply to source-derived text. The action plan is generated locally in the browser and is never submitted to an external service. It does not establish that the website is inaccessible, unsafe, broken, or performing poorly; all findings require manual confirmation and customer authorization. Editing the original saved-page manifest disables stale downloads.

### Printable client review report

After generating a report from saved authorized HTML, select **Download printable client report** to create a self-contained HTML review you can open offline or print to PDF using your browser. It shows site inventory counts, static remediation findings and form verification requirements. All source-derived strings are escaped before inclusion, and the downloaded file includes a restrictive Content Security Policy, no scripts and no external assets. This is a review artifact—not a certification, accessibility audit, completed website-functionality test or proof that leads reach a customer's inbox or CRM. Only share reports after confirming customer permission and reviewing the findings. No source HTML, access token or live customer data is included intentionally, and the report is generated entirely in the browser. The download is disabled after editing source until a fresh report succeeds.

### Review updated remediation action plans

After exporting `sitescout-remediation-action-plan.csv`, assign owners and update **Review status** to `Needs review`, `In progress`, `Implemented` or `Deferred`. For anything beyond `Needs review`, supply **Assigned to**. `Implemented` also requires an evidence reference and notes; `Deferred` requires documented reasons. Use **Updated remediation action plan (.csv)** and **Review remediation progress** on the dashboard to import the edited file and see counts plus unresolved work. The review runs through an offline Vercel/Docker endpoint with strict template columns, 500 KiB/1,000-row bounds, and no persistence or external requests. Progress remains **self-reported**, not independent proof of deployment, accessibility compliance or real-world improvement. Never include customer credentials or personal information in review evidence.

### Builder selection and license gate (SS-005)

The first source-verified builder candidate screening is available in [docs/BUILDER_LICENSE_AUDIT.md](docs/BUILDER_LICENSE_AUDIT.md) and [docs/builder-candidates.json](docs/builder-candidates.json). It distinguishes source-code licenses from non-redistributable icons/branding, AI-model terms and required paid/hosted services. **OpenPage** is the first candidate for an offline visual-editor benchmark; **Open Lovable** requires Firecrawl/AI/sandbox services for its documented flow, and **Onlook**'s Central Icons and other protected assets must be replaced before distributing a fork. No product integration or paid API has been authorized or deployed. CI checks the source-evidence registry; top-level license screening is not a full dependency or model license approval.

### Builder benchmark harness (SS-006)

The next Sprint 2 increment includes [three identical fictional SMB briefs](fixtures/builder_benchmark_briefs.json), an [offline exported-site preflight](app/builder_benchmark.py), a [blank results ledger](docs/builder-benchmark-results.csv) and [repeatable test instructions](docs/BUILDER_BENCHMARK.md). Run `python -m app.builder_benchmark --brief contractor --output-dir /path/to/generated/export --fail-on-static` against a candidate's **already generated** static export. Objective markup checks alone are not working-form, browser QA, hosting or commercial-license approval; no builders have been run or paid services activated by this increment.

### URL-first website analysis (SS-052)

The main dashboard now starts with **Analyze a website URL**. Enter the public HTTPS page URL, affirm that you have authorization to inspect it, and select **Analyze website URL**. On an **opt-in, trusted Docker host** with `SITESCOUT_CAPTURE_ENABLED=true` and a strong `SITESCOUT_CAPTURE_TOKEN`, SiteScout prompts for the private capture token **per request** (never stored in browser storage) and fetches **one page** using DNS pinning, certificate validation, a no-redirect rule, HTTP response/HTML size bounds and shared per-worker rate limiting. Results flow directly to the same static site findings, prioritized remediation review, report JSON, printable HTML and checklist exports. The original pasted-HTML analyzer remains under **Advanced: analyze manually saved HTML** for authorized offline fixtures and on Vercel.

This is **not** a complete site crawler, JavaScript renderer or form delivery check. Uncaptured links are unverified, not broken. The URL route is disabled by default and not available on Vercel. Configure the capture token in the untracked environment, never hardcode or commit it. **Do not enter the bearer token on an untrusted plaintext HTTP LAN:** use the same-machine `http://localhost:8087` or deploy an authenticated HTTPS reverse proxy on a trusted network before sharing the token. Never publicly forward enabled capture without further safeguards. With capture disabled, the new URL UI returns an explanatory message rather than silently falling back to fake analysis.

### Bounded same-site URL discovery (SS-053)

After authorization and token validation, URL-first analysis now retrieves the supplied public HTTPS page plus **up to two linked same-host HTML pages**, prioritizing paths with contact, quote, scheduling or booking hints. Each request independently passes the existing public-DNS pinning, TLS, no-redirect, 500-KiB and timeout checks. No cross-site links, HTTP links, login/account/admin/checkout paths, URL queries, known non-HTML assets, JavaScript, form submissions or external integrations are followed. At most **five** total page fetches are attempted per report, and at most **three** successful pages are analyzed. Failed secondary pages are recorded as **not captured / unverified**, never described as broken. The report includes `capture_discovery` with counts, bounded failure records and limitations. This is not a comprehensive crawl, crawler authorization service, or verification that forms deliver inquiries. Do not point at websites without permission.

### Trusted-LAN URL analysis without repeated token prompts (SS-054)

For an isolated, personally controlled test LAN, the Docker **URL report endpoint only** can be configured to accept same-origin JSON requests without a bearer token. This is opt-in, disabled by default:

```dotenv
SITESCOUT_CAPTURE_ENABLED=true
SITESCOUT_TRUSTED_LAN_NO_TOKEN=true
SITESCOUT_TRUSTED_CAPTURE_ORIGINS=http://localhost:8087,http://192.168.0.155:8087
```

Change the sample LAN IP to the actual machine's current address, then recreate Docker via `docker compose up -d --build`. The dashboard first attempts same-origin URL analysis automatically and asks for a private capture token **only if the server responds HTTP 401**. Trusted origins must exactly match both the HTTP `Origin` and `Host` headers, requests must be JSON, cross-site browser requests are denied, and the existing strict HTTPS public-IP validation, no redirects, TLS, page/attempt limits and shared five-requests-per-minute capture admission are retained. All other authenticated endpoints, including the standalone capture endpoint and private job queue, continue to require their respective credentials. Vercel has no live URL route.

**Security boundary:** This is an opt-in **trusted-network** convenience, **not login or user authentication**; a client on the LAN capable of forging HTTP headers could invoke the bounded public-HTTPS fetcher. Do not expose port 8087 to the internet or untrusted Wi-Fi, and do not use this option in a public/shared deployment. Choose an authenticated HTTPS deployment if the LAN is not exclusively trusted. No secrets are saved in browser storage.

### Understanding the report — what is and is not checked (SS-055)

SiteScout now introduces itself as an **early-stage source-HTML inspection and improvement planner**, rather than suggesting it is a complete live audit or website generator. The dashboard explains its four-step workflow, separates observed checks from untested behavior, and renders readable **page-by-page evidence**, a list of detected **form methods/actions/fields**, **capture coverage**, and up to 40 detailed, prioritized findings. Each finding names the detected condition, page, observed evidence, suggested remediation and manual verification method. The complete findings remain available in machine-readable JSON and the CSV export; the offline **printable HTML client report** now includes source evidence by page and form field details, not only the findings.

The static parser now also records **page language**, **meta description**, and **mobile viewport declarations**, with low/medium-priority review flags when missing, and compares captured page titles for duplicates. Missing markup is an observation, not definitive SEO, responsive-design or WCAG failure: JS-rendered output may differ, and actual browser testing is outside this version. Form delivery, successful bookings, navigation behavior, speed/performance, SEO outcomes, payments, accessibility compliance, responsive behavior and vulnerabilities remain **unverified**. The capture limit is at most three successfully retrieved pages per run, and no more than five network attempts. Do not sell the report as an independent certification or end-to-end functional test.

### Evidence-led next actions (SS-056)

Every static site report now includes a bounded `review_guidance` summary with the number of captured pages, detected forms, unreviewed internal links, high/medium review findings, and up to eight **recommended manual next steps**. The dashboard and printable client report display the reasons, relevant page evidence and suggested next action for each item. Actions prioritize high-priority markup findings, permissioned **synthetic inquiry receipt tests** when a form is detected, unreviewed pages, mobile/desktop browser behavior and deeper optional audits. A site without static forms instead recommends checking whether JavaScript or embedded forms exist. All suggestions remain **Not verified**; no test, conversion, audit certification or security score is invented. This does not perform browser navigation or submit forms automatically.

### SS-057 — real-browser regression coverage (no third-party scans)

The repository now contains a real headless **Chromium** smoke test of the actual SiteScout dashboard. It opens the locally served app, fills an authorized sample URL, intercepts the URL-report request with **fictional data**, checks the rendered page/form/coverage/next-step sections, downloads the printable report, opens the advanced HTML UI and verifies stale report controls clear. This is a **browser-executed UI regression test**, not evidence that a third-party website was loaded, that a contact form delivered, or that real mobile/accessibility/performance conditions have been verified. No external URLs are requested by this smoke (the sample target is mocked). The browser runtime is a pinned dev-only Playwright dependency; the production Docker image remains Python-only and contains no browser or runtime Node dependency.

Run when the local app is available on port 8087:

```sh
npm ci --ignore-scripts
npx playwright install chromium
SITESCOUT_BROWSER_URL=http://127.0.0.1:8087 npm run test:browser
```

A dedicated [Real browser QA](.github/workflows/browser-qa.yml) GitHub Actions workflow also starts SiteScout on a GitHub runner, installs isolated Chromium, and tests that same user-visible flow. Existing Python/Node/Docker CI tests remain independent. Browser installation and CI runner resources must be available. This only verifies the SiteScout UI with synthetic results, and does not fetch prospect websites or submit inquiries.
