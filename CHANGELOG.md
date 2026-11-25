# Changelog

All notable changes will be documented here. Format follows Keep a Changelog; versions follow Semantic Versioning.

## [Unreleased]
### Added
- Sprint 0 engineering scaffold, health endpoint, Docker Compose, CI, governance and release documentation.
- Added offline HTML inventory CLI, demo fixture, and tests for Sprint 1.
- Added an offline tenant-directory external-link extractor and an Optimist Hall pilot plan.
- Added a Vercel-compatible SiteScout homepage and Python health function, with matching Docker dashboard and route tests.
- Added browser-based offline HTML inventory and directory analysis with a shared Vercel/Docker JSON endpoint.
- Added human-readable static findings and self-contained dashboard examples for website inventory and directory discovery.
- Added opt-in Docker-only authorized public HTTPS capture with DNS pinning and SSRF protection.

- Standardized verified README technology/deployment badges and dynamic GitHub CI/activity badges, with automated validation and contributor guidance.
- Hardened Docker-only live capture with mandatory bearer token, fail-closed configuration and in-memory request throttling.

- Validate live capture request parameters before any outbound request.

- Added a durable SQLite capture-job metadata store with atomic queue admission, owner-scoped lookup, sanitized audit events and retention cleanup; HTTP integration is deferred until authentication and worker isolation are ready.

- Added a single-job capture worker prototype with sanitized failure logging and explicit recovery of interrupted job metadata; not yet connected to the HTTP service.

- Added a manual operator-only capture worker CLI, opt-in Compose profile and persistent SQLite metadata volume. This does not expose or authenticate an HTTP job API.

- Serialized private CLI capture workers using persistent-volume advisory locks; added explicit guarded stale-job recovery with contention tests.

- Added owner-label-scoped, bounded private CLI listing of capture job metadata without target URLs.

- Added explicit operator-only capture result export to restricted local JSON files with limits, exclusive creation and sanitized failure states.

- Added guarded manual expiry cleanup of protected JSON capture exports, preserving recent and unrelated files.

- Added a standalone fail-closed hashed operator bearer-token identity module for future private job APIs; no HTTP routes enabled.

- Added default-off Docker-only authenticated job metadata endpoints backed by persistent SQLite, with actor derivation, ownership checks and submission throttling. Not a public-facing service.

- Added CI smoke coverage for the live Docker API's homepage, health and disabled-by-default capture/job endpoints.

- Added synthetic-token Docker smoke tests validating private job identity, worker/API shared persistence and owner isolation.

- Added manual private Docker-only job queue and status controls to the dashboard without persisting operator tokens.

- Require explicit server-side authorization assertion for queued HTTPS captures before DNS resolution.

- Added owner-scoped, default-off Docker retrieval of completed protected analysis JSON, refusing unauthorized, unfinished and unsafe result files.

- Added owner-authenticated private capture result lookup and safe manual display in the Docker dashboard.

- Added manual owner-scoped recent capture job listing in the Docker dashboard, prefilling the latest job ID.

- Added a manual-start continuous Docker capture worker profile with exclusive single-host execution and protected result exports.

- Added an offline multi-page site inventory report with navigation graph, form catalog, contact/booking candidate paths, and bounded synthetic fixture.

- Added a shared Vercel/Docker offline multi-page site-report API and dashboard workflow with synthetic demo input.

- Added evidence-based form and potential integration verification checklists to offline multi-page site reports.

- Added real Docker HTTP smoke checks for offline multi-page reports and functional requirements.

- Added client-side JSON manifest import and one-click complete site-report download, with browser-flow tests and safe input limits.

- Added a spreadsheet-safe CSV export of per-form verification tasks, with default untested status and browser integration tests covering formula/quote injection defenses.

- Bound the offline Docker dashboard to trusted LAN interfaces by default, with host-only override and CI checks for default-off capture.

- Added offline review of human-completed form-checklist CSV, with evidence requirements, status counts, blocked/failed follow-up and Vercel/Docker parity.

- Added an accessible at-a-glance summary for offline site inventory reports and automatic reset of stale metrics.

- Reconciled delivered Sprint 1 and private capture infrastructure story statuses with merged CI evidence and clarified remaining public-security and hosting gates.

- Added prioritized, evidence-based static website remediation recommendations and an accessible top-priority dashboard review list.

- Added downloadable spreadsheet-safe remediation action-plan CSV with reviewer/assignment columns for authorized SMB site audits.

- Added downloadable self-contained printable customer review HTML, with escaped source-derived strings, no external assets and explicit static-evidence limitations.

- Added offline reimport and review of human-updated remediation action plans, with evidence requirements, progress counts and unresolved follow-ups.

- Added source-verified licensing and external-service screening for six builder/runtime candidates, with immutable LICENSE blob fingerprints, risk decisions, documentation and CI validation.

- Added three standardized fictional SMB builder briefs, a bounded offline static export benchmark and an explicit unmeasured comparison scorecard for future repeatable evaluation.

- Added URL-first one-page static website report UI, reusing opt-in authenticated DNS-pinned HTTPS capture; manual saved HTML moved to advanced mode and remains available.

- Added bounded, same-host HTTPS linked-page discovery for URL-first reports, prioritizing contact and booking pages, with maximum five attempted fetches and explicit unverified gaps.

- Added opt-in same-origin trusted-LAN URL reports without repeated bearer-token prompts; token-required mode and private capture/job authentication remain available.

- Clarified SiteScout's actual static inspection scope in the dashboard and expanded per-page, form and coverage evidence, prioritized findings and printable client report; added language, viewport, description and duplicate-title review rules.

- Added readable, evidence-based recommended next actions in SiteScout reports and printouts, with manual verification guidance and no unverified functional claims.

- Added a development-only real Chromium regression test for the SiteScout dashboard, with mocked fictional website data and a separate browser QA CI workflow.
