# Sprint Plan

Cadence: 2-week planning cycles (targets, not deadlines). Each sprint has planning, scoped issues, demo, retrospective, and a recorded carryover decision. Update this document as work evolves.

| Sprint | Goal | Exit criteria | Status |
|---|---|---|---|
| 0 | Repository and engineering foundation | Docs, Compose, status API, CI tests, release policy | In progress |
| 1 | Existing-site functional inventory | Authorized URL/fixture capture; navigation, forms, content inventory; structured JSON and tests | Planned |
| 2 | Free builder evaluation | Benchmark Open Lovable, OpenPage, Onlook, local coding agent; license/cost matrix; decision record | Planned |
| 3 | Design generation | Three differentiated design directions; brand tokens; responsive concept previews | Planned |
| 4 | Working site generation | Generate Astro/React pages and functional form workflows; reproducible builds | Planned |
| 5 | QA and visual refinement | Playwright screenshots, accessibility/performance checks, repair loop, approval gate | Planned |
| 6 | Prospect discovery and audits | Permitted data sources, dedupe, scoring, evidence-based reports | Planned |
| 7 | Sales previews and CRM | Private previews, human-approved outreach, suppression list, audit trail | Planned |
| 8 | Paid handoff and operations | Customer approval, deployment checklist, backups, maintenance workflows | Planned |

## Sprint ceremony
Planning: prioritize by impact/risk and capacity. Daily: update blockers and work in progress. Review: demonstrate tested functionality. Retrospective: record improvements. Carry incomplete issues forward explicitly.

## Definition of ready
Clear user outcome, dependencies, testable acceptance criteria, security/license considerations, and estimate.

## Definition of done
Code reviewed, CI green, tests pass, docs and release notes updated, no unreviewed paid dependencies or outbound communications.

## Sprint 0 deployment recovery
SS-014: restore the Vercel homepage, add a serverless health route, and retain Docker dashboard parity. Exit requires green unit tests, container smoke tests, and a verified Vercel deployment URL. No AI generation capability is implied by this milestone.

## Sprint 1 increment
SS-015 provides a usable browser workflow for the existing offline parsers, sharing a size-limited POST API across Vercel and Docker. Next: human-readable findings, test fixtures in the UI, and authorized capture via a separately secured worker.

SS-016 increment: explainable findings, example inputs and safe browser rendering. Acceptance: warning rules are tested and clearly avoid asserting live behavior or automated outreach.

## Sprint 2 increment
SS-017 introduces opt-in Docker-only public HTTPS capture with strict network safety controls and explicit authorization confirmation. SS-018 will add authentication, rate limiting and job isolation before the feature can be exposed beyond a trusted host.

SS-019 repository-maintenance increment: verified technology, deployment and dynamic GitHub badges immediately below the README title; document the ongoing contributor/agent policy and enforce with CI. This accompanies normal Sprint 2 delivery.

SS-020: harden the trusted Docker capture prototype with a bearer token, per-process throttling and negative security tests. This does not close SS-018's public-exposure requirements: SS-021 retains durable jobs, identity and audit logging.

SS-022: reject malformed capture input before external requests; negative tests guard this prerequisite for SS-021.

### SS-021 increment A — persistent capture metadata store
SQLite-backed job lifecycle and audit metadata, owner-scoped lookup, transaction-safe shared admission, bounded pending queue, and completed-job pruning. Unit tests cover concurrent admission and restart persistence. **Not yet wired into the capture HTTP route:** still required are authenticated user sessions, a bounded background worker, secure result storage, timeout recovery, TLS and operational testing. This increment does not make public capture safe.

### SS-021 increment B — bounded worker and explicit recovery
Single-job execution path, injected capture/analyze functions for offline tests, sanitized failure audit, and explicit stale-running requeue. This remains a library-only prototype. Do not wire recovery to a recurring timer until worker leases and ownership are implemented; jobs can otherwise be processed twice.

### SS-021 increment C — operator-only CLI and persistent Compose volume
Add a default-off manual `capture-worker` Compose profile and dedicated named SQLite volume, with fail-closed operator commands for authorized job submission, work-once, owner-label-scoped metadata/audit inspection and retention pruning. No HTTP job API, server-side sessions, automatic scheduling, or public capture enablement; those remain acceptance blockers for full SS-021 completion. Test profile configuration and storage ownership in an actual Docker engine before release.

### SS-021 increment D — exclusive worker and recovery
Use advisory single-host locks for the private operator CLI to prevent concurrent `work-once` invocations and guard explicit stale-job recovery. Add contention tests and retain the public-deployment block pending authenticated sessions, distributed leases, durable result access, and TLS.

### SS-021 increment E — owner-scoped bounded job listing
Expose a private CLI listing limited to a specific operator label with no target URLs or raw results. Test isolation across actors, deterministic ordering and bounded record counts. Still requires real user authentication before browser-facing job APIs.

### SS-021 increment F — opt-in private results
Add explicit opt-in local JSON analysis-result export in a restricted persistent-volume directory; secure file creation, no overwrite, byte caps and fail-closed job lifecycle tests. Future requirements: controlled retrieval, result deletion/retention, authentication, worker leases, encryption/backup policy and public exposure safety.

### SS-021 increment G — result-export retention
Provide manual exclusive-worker cleanup of expired private JSON exports, with strict filename/type validation and tests that preserve recent files, symlinks and unrelated content. Production automation, identity and customer retention policies remain future acceptance gates.

### SS-021 increment H — hashed operator identity foundation
Standalone fail-closed mapping of identity labels to SHA-256 digests of high-entropy bearer tokens, with exact actor derivation and negative security tests. No HTTP wiring or public authorization is claimed. Subsequent acceptance requires authenticated job submission/retrieval, TLS termination and abuse controls.

### SS-021 increment I — private authenticated job API (experimental)
Connect default-off Docker-only POST/GET job metadata endpoints to the persistent queue with server-derived hashed-token actor identities, request validation, rate limiting, ownership-scoped status/list/audit, and negative tests. No Vercel endpoint, client-supplied actor or raw captured content is permitted. Public use remains blocked by TLS termination, real user sessions, distributed worker fencing, durable protected result delivery, operational hardening and threat review.

### SS-021 increment J — live Docker smoke gate
CI starts the actual Compose API container and checks homepage/health plus default-off job/capture HTTP behavior; this is a test-environment contract, not evidence of production authentication or public deployment safety.

### SS-021 increment K — authenticated Compose integration smoke
CI boots the real API container with synthetic local tokens, seeds an offline fixture job from a separate worker container into the shared SQLite volume, and verifies owner-bound listing/status/audit and rejected credentials over loopback. No third-party fetching or production API exposure.

### SS-021 increment L — manual private job UI
Add explicit-authorization job submission and manual status lookup controls to the existing dashboard. Prompt for operator token on each request without persisting it, render untrusted responses as text, and preserve default-off backend behavior. No automatic polling or publicly exposed queues.

### SS-021 increment M — server-side permission assertion
Require private job submissions to include literal boolean `authorized: true` and verify missing/non-boolean assertions are denied before DNS or queue admission.

### SS-021 increment N — owner-scoped private result retrieval
Enable an experimental Docker-only, default-off owner-authenticated result read for completed jobs, enforcing private file permissions, regular-file and size limits, and no cross-operator leakage. Tests cover incomplete, missing and other-owner result access. Public access remains blocked until TLS, user-session controls, storage threat review and lifecycle hardening are complete.

### SS-021 increment O — manual private result display
Add dashboard retrieval for protected completed-job JSON, prompting for operator identity each time, safely rendering source data as text, and preserving Vercel's lack of capture-job APIs.

### SS-021 increment P — private recent-job dashboard
Expose existing owner-authenticated job-history listing through a manual dashboard action with short-lived in-memory token use and redacted text rendering. Do not auto-poll or expose on Vercel.

### SS-021 increment Q — opt-in continuous trusted-host worker
Add a manual-start Compose runner profile that polls the durable queue using the existing exclusive single-host lock and opt-in private result persistence. Tests cover bounded cycles, cancellation and contention; CI validates Compose configuration. It is not a production distributed worker.

### SS-003 increment — offline multi-page website relationships
Deliver a zero-network multi-page manifest analyzer that joins saved page inventories, links, form actions, and candidate paths to contact or booking pages without claiming successful interactions. Use deterministic synthetic fixtures and negative security tests. Follow with a browser upload workflow and deeper form/integration requirements inventory.

### SS-003 increment B — browser and serverless offline site reports
Provide a shared, size-limited Vercel/Docker endpoint for saved multi-page manifests, a pasted-JSON dashboard form with a synthetic demo, and tests for invalid inputs. Explicitly avoid fetch/crawl/outreach and preserve human review for form functionality.

### SS-004 increment — functional requirements from static site evidence
Derive a deterministic form-testing checklist, potential third-party action-host list, transport/method cautions, and explicit unknowns from offline multi-page reports. Follow with customer-approved live verification and reporting; never imply that static HTML proves integration delivery.

### SS-003/SS-004 CI follow-up — live Docker report smoke
Run the actual Docker API with a synthetic two-page saved-HTML request; assert page count, contact-page candidates, unverified form functionality, and invalid JSON-shape rejection. No external sites are contacted.

### SS-040 — Import/export usability for offline site reports
Add a local JSON file picker for saved-page manifests, preserve an editable manifest field, and offer downloadable complete report JSON only after successful analysis. Reject oversized and malformed imports, revoke temporary blob URLs, and test actual browser event workflows in CI using a dependency-free Node harness. No web crawling or external page requests.
