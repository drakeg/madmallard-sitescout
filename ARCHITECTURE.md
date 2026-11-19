# Architecture and tool evaluation

## Initial architecture
API/status service -> queued authorized-site analysis -> structured functional inventory -> design brief -> local-model coding agent -> isolated build -> Playwright + axe + Lighthouse QA -> human approval -> private preview -> optional sales workflow.

Initial scaffold only includes a Python HTTP health endpoint. No crawling, AI or outreach is implemented yet.

## Tool candidates
- Local inference: Ollama; verify each model's commercial license and quality.
- Coding agent: OpenCode; confirm API and local-model support.
- Reconstruction: Open Lovable and screenshot-to-code; audit mandatory external services before integration.
- Structured generation: OpenPage; verify export and license.
- Visual refinement: Onlook or GrapesJS; verify integration and licensing.
- Output: Astro/Tailwind for content sites; React-based application for genuinely dynamic features.
- QA: Playwright, axe-core, Lighthouse.

## Evaluation rubric
Visual design 25%, functional completeness 30%, self-hosting/local AI 20%, maintainability 15%, license/commercial safety 10%. Hard-fail on mandatory paid runtime or incompatible commercial license.

## Trust boundaries
Web content is untrusted. Browser and code execution jobs require isolation, limited egress, no production secrets and bounded retries. Generated sites are labeled unofficial previews until authorized. All external outreach is approval-gated.

## Dual deployment surfaces
- **Vercel:** repository-root static `index.html` plus stateless `api/health.py`; no Docker, Ollama, or browser worker on Vercel.
- **Docker Compose:** `app.server` serves the same dashboard and health contract; local Python analysis and future container workers run here.
- No job submission or AI generation is advertised as operational until implemented, secured, and tested.

## Offline analysis API
`POST /api/analyze` accepts JSON `{"mode":"inventory|directory","url":"https://…","html":"…"}` and returns `{"result":…}` or `{"error":…}`. Shared implementation in `app/analyze.py` and `app/http_api.py` runs on Vercel Python Functions and the Docker HTTP server. The request is size-limited and performs no network I/O.

`app/findings.py` generates deterministic, explainable summaries of parsed HTML. Browser rendering uses DOM `textContent` for untrusted values, never injected HTML. Example inputs are embedded locally in the dashboard and are not live crawls.
