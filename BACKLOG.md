# Product Backlog

Status `DONE` means the scoped story's acceptance criteria were implemented and validated in CI, **not** that live third-party form delivery, Vercel production deployment, or public capture safety has been verified.

Priority order: P0 > P1 > P2. Track implementation in GitHub Issues; this file is the roadmap index. Status values: TODO / IN PROGRESS / DONE.

| ID | Priority | Sprint | Story | Acceptance criteria | Status |
|---|---|---|---|---|---|
| SS-001 | P0 | 0 | Project scaffold | Health endpoint, Compose, tests and CI | IN PROGRESS |
| SS-002 | P0 | 0 | Engineering governance | AGENTS, contributing, security, releases, PR template | IN PROGRESS |
| SS-003 | P0 | 1 | Site inventory | Extract page list, internal links and contact/booking journeys from authorized fixtures | DONE |
| SS-004 | P0 | 1 | Functional requirements | Structured inventory of forms and integrations, unknowns flagged | DONE |
| SS-005 | P0 | 2 | Builder license audit | SPDX, commercial restrictions, required hosted services and model terms documented | IN PROGRESS (upstream top-level licenses and service risks; transitive dependencies and model terms pending) |
| SS-006 | P0 | 2 | Builder benchmark | Same 3 demo briefs, objective scoring, screenshots, repeatable costs | IN PROGRESS (fictional briefs, offline artifact preflight and empty scorecard; actual builders/visual QA/costs pending) |
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
| SS-016 | P0 | 1 | Explainable results and demo fixtures | Human-readable static findings, examples, raw JSON preserved | DONE |
| SS-017 | P0 | 2 | Opt-in authorized HTTPS capture | Docker-only, default-off, public-address DNS pinning, TLS validation, no redirects, size/time limits | IN PROGRESS |
| SS-018 | P0 | 2 | Authenticated capture jobs | Authentication, rate limits, queue and audit log before any public exposure | BACKLOG |

| SS-019 | P1 | 2 | Verified README badge maintenance | Actual-stack badges, dynamic CI/issues/PR badges, documented convention and CI validation; no fabricated release/license | DONE |
| SS-020 | P0 | 2 | Capture access guard | Token auth, default-off, per-worker rate limit, security tests and deployment instructions | DONE |
| SS-021 | P0 | 2 | Durable capture queue and audit | Per-user identity, shared throttling, durable jobs and logs for public exposure | IN PROGRESS (private Docker API, worker and protected results implemented; public safety gates outstanding) |

| SS-022 | P0 | 2 | Capture preflight validation | Reject invalid JSON shapes, capture modes, and oversized URLs before outbound requests | DONE |

| SS-023 | P0 | 2 | Private capture worker CLI | Opt-in Compose profile, persistent SQLite volume, disabled-by-default manual job submission and safe audit/status output | DONE |

| SS-024 | P0 | 2 | Exclusive operator worker | File lock for single-host work-once and explicit guarded stale recovery; contention tests | DONE |

| SS-025 | P1 | 2 | Private capture job listing | Show bounded owner-labelled job history without URLs or captured content | DONE |

| SS-026 | P0 | 2 | Optional protected result export | Save bounded local analysis JSON only on explicit opt-in with owner-private permissions and no overwrite | DONE |

| SS-027 | P0 | 2 | Protected result retention | Explicit worker-locked removal of expired result JSON; preserve unrelated paths/symlinks | DONE |

| SS-028 | P0 | 2 | Operator identity foundation | Fail-closed high-entropy hashed token mapping, actor derivation, rejection tests; not publicly exposed | DONE |

| SS-029 | P0 | 2 | Private authenticated queue HTTP API | Default-off Docker-only job create/status/list/audit, derived actor identity, shared limits, ownership tests | DONE |

| SS-030 | P0 | 2 | Docker HTTP smoke gates | CI verifies live Docker API homepage/health and fail-closed jobs/capture defaults | DONE |

| SS-031 | P0 | 2 | Authenticated Docker integration smoke | CI verifies operator token identity, shared SQLite volume and cross-actor isolation across actual containers | DONE |

| SS-032 | P1 | 2 | Manual private queue dashboard | Submit authorized jobs and check status from browser without storing bearer tokens; Docker-only API | DONE |

| SS-033 | P0 | 2 | Server-side capture authorization assertion | Require boolean authorization acknowledgement before DNS lookup and enqueue | DONE |

| SS-034 | P0 | 2 | Owner-scoped private result retrieval | Authenticated completed-job results only, bounded protected files, negative ownership and symlink tests | DONE |

| SS-035 | P1 | 2 | Private result dashboard | Manually retrieve and render completed owner-authenticated capture results without browser token storage | DONE |

| SS-036 | P1 | 2 | Recent capture jobs dashboard | List owner-scoped jobs, prefill most recent ID, avoid token persistence and untrusted HTML injection | DONE |

| SS-037 | P0 | 2 | Opt-in private background worker | Manual-start Docker runner profile, exclusive single-host processing, protected results, unit and Compose tests | DONE |

| SS-038 | P0 | 1 | Multi-page report dashboard | Paste authorized saved pages JSON, generate navigation/form report with Vercel/Docker parity and size limits | DONE |

| SS-039 | P0 | 1 | End-to-end offline site report smoke | Verify real Docker HTTP site report and functional checklist with synthetic saved HTML | DONE |

| SS-040 | P0 | 1 | Offline report JSON import/export | Import authorized saved-page JSON, edit, analyze, download full report, reject bad/oversized input and test browser flow | DONE |

| SS-041 | P0 | 1 | Form verification checklist CSV | Convert saved form inventory into editable per-test CSV, prevent formula injection and keep untested evidence explicit | DONE |

| SS-042 | P0 | 0 | Trusted LAN Docker dashboard | Default all-interface dashboard binding, capture endpoints disabled and no published worker ports; CI Compose check | DONE |

| SS-043 | P0 | 1 | Import completed form verification checklist | Upload manually reviewed CSV, validate evidence, count statuses and surface failed/blocked tests without claiming automated verification | DONE |

| SS-044 | P1 | 1 | Site report overview | Display pages, forms needing tests, uncaptured links and contact candidates without claiming live verification | DONE |

| SS-045 | P1 | 0 | Reconcile delivered backlog status | Mark merged and CI-validated scoped increments done while retaining public security/hosting blockers | DONE |

| SS-046 | P0 | 1 | Prioritized site remediation plan | Explainable findings from authorized saved HTML, severity/evidence/fix/test steps, safely rendered in dashboard | DONE |

| SS-047 | P0 | 1 | Remediation action-plan CSV | Export prioritized findings with fixes, verification tasks, assignee/evidence columns and formula-injection protection | DONE |

| SS-048 | P0 | 1 | Offline printable client review | Generate self-contained, CSP-restricted HTML with static findings and verification caveats; escape source-derived text and browser-test malicious markup | DONE |

| SS-049 | P0 | 1 | Remediation action progress review | Reimport reviewed action-plan CSV, require owners/evidence, report pending work with no unverified completion claims | DONE |

| SS-050 | P0 | 2 | Machine-verifiable builder candidate registry | Track LICENSE blob SHA, hosted APIs, assets restrictions and candidate status; enforce sources in CI | DONE |

| SS-051 | P0 | 2 | Deterministic static output benchmark harness | Same three fictional SMB briefs and offline HTML checks with zero invented scores or paid providers | DONE |

| SS-052 | P0 | 1 | URL-first authorized website analysis | Public HTTPS URL primary; consent, private opt-in capture token, single-page report and safe default-off route; HTML fallback advanced | DONE |

| SS-053 | P0 | 1 | Bounded URL-linked page discovery | Capture up to 3 same-host HTTPS pages per request, 5-attempt limit, prioritized contact pages, ignore unsafe links and clearly flag unverified failures | DONE |

| SS-054 | P0 | 1 | Trusted-LAN URL analysis without token prompts | Opt-in exact-origin local report requests, strict Host/Origin/JSON checks, preserve rate limits and bearer fallback | DONE |

| SS-055 | P0 | 1 | Explain SiteScout's actual limits and provide detailed in-app/printable reports | Document checks vs unverified behavior, show pages/forms/coverage and actionable findings, add metadata checks | DONE |

| SS-056 | P0 | 1 | Evidence-based next steps in dashboard and printable report | Prioritize high source findings, synthetic form verification, uninspected pages, browser checks; cap suggestions and never assert unrun tests | DONE |

| SS-057 | P0 | 1 | Real Chromium dashboard smoke | Run real browser against dashboard with mocked URL report, assert visible findings, downloadable report and stale state reset; separate browser QA CI | DONE |

| SS-058 | P1 | 1 | Reconcile merged website QA and README workflow badges | Update closed scope status for confirmed merged and tested stories, add real-browser QA dynamic CI badge, maintain accurate distinction between UI smoke and live-site verification | DONE (dynamic browser QA badge present; CI validation guard added; live third-party verification remains out of scope) |
