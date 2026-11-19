# Mad Mallard SiteScout

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
