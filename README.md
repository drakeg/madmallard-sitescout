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
