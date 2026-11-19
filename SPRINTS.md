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
