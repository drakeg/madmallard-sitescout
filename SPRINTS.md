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
