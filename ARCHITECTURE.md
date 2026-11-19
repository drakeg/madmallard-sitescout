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
