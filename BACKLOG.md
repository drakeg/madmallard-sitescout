# Product Backlog

Priority order: P0 > P1 > P2. Track implementation in GitHub Issues; this file is the roadmap index. Status values: TODO / IN PROGRESS / DONE.

| ID | Priority | Sprint | Story | Acceptance criteria | Status |
|---|---|---|---|---|---|
| SS-001 | P0 | 0 | Project scaffold | Health endpoint, Compose, tests and CI | IN PROGRESS |
| SS-002 | P0 | 0 | Engineering governance | AGENTS, contributing, security, releases, PR template | IN PROGRESS |
| SS-003 | P0 | 1 | Site inventory | Extract page list, internal links and contact/booking journeys from authorized fixtures | TODO |
| SS-004 | P0 | 1 | Functional requirements | Structured inventory of forms and integrations, unknowns flagged | TODO |
| SS-005 | P0 | 2 | Builder license audit | SPDX, commercial restrictions, required hosted services and model terms documented | TODO |
| SS-006 | P0 | 2 | Builder benchmark | Same 3 demo briefs, objective scoring, screenshots, repeatable costs | TODO |
| SS-007 | P0 | 3 | Design directions | Three genuinely different responsive concepts per brief | TODO |
| SS-008 | P0 | 4 | Functional code generation | Builds reproducibly, navigates, and submits forms to a test endpoint | TODO |
| SS-009 | P0 | 5 | Visual/browser QA | Desktop/mobile screenshots, E2E tests and accessibility gates | TODO |
| SS-010 | P1 | 6 | Prospect discovery | Permitted source, dedupe and opt-out handling | TODO |
| SS-011 | P1 | 7 | Preview approvals | Human review before publication or outreach | TODO |
| SS-012 | P1 | 7 | CRM | Reply tracking, suppression and communication audit | TODO |
| SS-013 | P1 | 8 | Customer delivery | Export, handoff and rollback instructions | TODO |

## Non-goals for MVP
Bulk unsolicited emailing, impersonation, unlicensed content copying, paid-only runtime integrations, production deployment of unreviewed generated code.

## Deployment recovery (current)
| ID | Priority | Sprint | Story | Acceptance criteria | Status |
|---|---|---|---|---|---|
| SS-014 | P0 | 0 | Vercel/Docker dashboard parity | Root homepage and health endpoints work in both environments; docs and tests updated | IN PROGRESS |
| SS-015 | P0 | 1 | Dashboard offline HTML analyzer | Paste saved HTML, select inventory/directory, view JSON in both runtimes; no outbound fetch | IN PROGRESS |
| SS-016 | P0 | 1 | Explainable results and demo fixtures | Human-readable static findings, examples, raw JSON preserved | IN PROGRESS |
| SS-017 | P0 | 2 | Opt-in authorized HTTPS capture | Docker-only, default-off, public-address DNS pinning, TLS validation, no redirects, size/time limits | IN PROGRESS |
| SS-018 | P0 | 2 | Authenticated capture jobs | Authentication, rate limits, queue and audit log before any public exposure | BACKLOG |

| SS-019 | P1 | 2 | Verified README badge maintenance | Actual-stack badges, dynamic CI/issues/PR badges, documented convention and CI validation; no fabricated release/license | IN PROGRESS |
| SS-020 | P0 | 2 | Capture access guard | Token auth, default-off, per-worker rate limit, security tests and deployment instructions | DONE |
| SS-021 | P0 | 2 | Durable capture queue and audit | Per-user identity, shared throttling, durable jobs and logs for public exposure | IN PROGRESS (SQLite metadata foundation; not connected to HTTP) |

| SS-022 | P0 | 2 | Capture preflight validation | Reject invalid JSON shapes, capture modes, and oversized URLs before outbound requests | DONE |

| SS-023 | P0 | 2 | Private capture worker CLI | Opt-in Compose profile, persistent SQLite volume, disabled-by-default manual job submission and safe audit/status output | IN PROGRESS |

| SS-024 | P0 | 2 | Exclusive operator worker | File lock for single-host work-once and explicit guarded stale recovery; contention tests | IN PROGRESS |

| SS-025 | P1 | 2 | Private capture job listing | Show bounded owner-labelled job history without URLs or captured content | IN PROGRESS |

| SS-026 | P0 | 2 | Optional protected result export | Save bounded local analysis JSON only on explicit opt-in with owner-private permissions and no overwrite | IN PROGRESS |

| SS-027 | P0 | 2 | Protected result retention | Explicit worker-locked removal of expired result JSON; preserve unrelated paths/symlinks | IN PROGRESS |

| SS-028 | P0 | 2 | Operator identity foundation | Fail-closed high-entropy hashed token mapping, actor derivation, rejection tests; not publicly exposed | IN PROGRESS |

| SS-029 | P0 | 2 | Private authenticated queue HTTP API | Default-off Docker-only job create/status/list/audit, derived actor identity, shared limits, ownership tests | IN PROGRESS |

| SS-030 | P0 | 2 | Docker HTTP smoke gates | CI verifies live Docker API homepage/health and fail-closed jobs/capture defaults | IN PROGRESS |

| SS-031 | P0 | 2 | Authenticated Docker integration smoke | CI verifies operator token identity, shared SQLite volume and cross-actor isolation across actual containers | IN PROGRESS |

| SS-032 | P1 | 2 | Manual private queue dashboard | Submit authorized jobs and check status from browser without storing bearer tokens; Docker-only API | IN PROGRESS |
