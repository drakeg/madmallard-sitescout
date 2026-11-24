# Mad Mallard SiteScout

<!-- badges:start -->
[![Python 3.15](https://img.shields.io/badge/Python-3.15-3776AB?logo=python&logoColor=white)](Dockerfile)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](compose.yaml)
[![Vercel](https://img.shields.io/badge/Vercel-Deployment-000000?logo=vercel&logoColor=white)](vercel.json)

[![CI](https://github.com/drakeg/madmallard-sitescout/actions/workflows/ci.yml/badge.svg)](https://github.com/drakeg/madmallard-sitescout/actions/workflows/ci.yml)
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
Set `SITESCOUT_BIND=0.0.0.0` for LAN testing **only on a trusted network**; add authentication before exposing a real dashboard.

## Status
Sprint 0 scaffold. The service is a health/status API, **not yet a website generator**. See [SPRINTS.md](SPRINTS.md), [BACKLOG.md](BACKLOG.md), [ARCHITECTURE.md](ARCHITECTURE.md), and [RELEASES.md](RELEASES.md).

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

For Docker, use `docker compose up -d --build` and visit `http://127.0.0.1:8087/` (or configure `SITESCOUT_BIND=0.0.0.0` for trusted LAN access). The same dashboard and health routes are served by the Python container. Do not expose unauthenticated future worker controls to the public internet.

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
