# SS-006 — Reproducible builder benchmark

This is the **offline benchmark harness**, not a record of completed builder runs. No vendor, subscription, LLM, sandbox or hosted deployment has been activated or paid for.

## Comparable briefs

Source of truth: [fixtures/builder_benchmark_briefs.json](../fixtures/builder_benchmark_briefs.json). Each is entirely fictional, with no customer data, and each candidate must receive the **same written brief, expected pages and form requirements**. Do not customize evaluation standards for a particular builder.

| Brief ID | Fictional SMB | Required pages | Functional workflow to verify later |
|---|---|---|---|
| `contractor` | Blue Ridge Home Repair | Home, services, quote | Synthetic quote inquiry received by authorized local endpoint |
| `cafe` | Maple Street Café | Home, menu, contact | Synthetic contact inquiry received; no real reservation claim |
| `rv-repair` | Trailside RV Service | Home, services, request-service | Synthetic repair request received; no live dispatch integration claimed |

Every brief expects named `name`, `email` and `message` fields in a POST form on its designated contact/request page. This is a **static markup requirement only**, not validation of correct delivery.

## Baseline CLI

1. Build a generated website using a candidate in an authorized, isolated development environment. Save its export under a disposable directory with the required relative paths (e.g. `index.html`, `services/index.html`, `quote/index.html`).
2. Run the same offline preflight for each candidate and brief:

```sh
python -m app.builder_benchmark --brief contractor --output-dir /path/to/export --fail-on-static
python -m app.builder_benchmark --brief cafe --output-dir /path/to/export --fail-on-static
python -m app.builder_benchmark --brief rv-repair --output-dir /path/to/export --fail-on-static
```

3. Save stdout JSON with candidate name, revision, platform/hardware and chosen model/provider information in a separately maintained benchmark results record. Do **not** infer costs or task time from the static parser.
4. Perform the listed **manual gates** with a real browser and a local synthetic inquiry destination. Observe desktop/mobile navigation, keyboard/screen-reader accessibility, responsive screenshots, true form receipt, performance, usage cost and asset/model licensing.
5. Compare the same three briefs across OpenPage, Onlook and a local agent workflow when their installation and licensing gates permit. Open Lovable's documented external service requirements prevent it from serving as the initial zero-paid-dependency baseline; do not activate subscriptions without authorization.

## Automated checks versus unknowns

The script reads at most 50 HTML pages and 500 KiB per required page; it refuses symlinked HTML and unsafe page paths and **never executes** generated code. For each required page it checks: file exists, nonempty HTML title, H1 and a device-width viewport. On the specified form page it requires a POST form with expected named fields. The output reports objective pass/fail counts only. **It cannot assert that the page looks good, links navigate, form submissions arrive, customers convert, third-party assets are licensed, or a deployment is secure.**

Record those items separately using the provided manual gates. Report **unverified** rather than marking them passed without observed evidence.

## Scorecard template

Use [builder-benchmark-results.csv](builder-benchmark-results.csv) as the controlled results ledger. All rows begin **Not run**, cost **Unmeasured**, and live checks **Unverified**. Record candidate source SHA, command, actual measured time/cost, manual test evidence and environment details after a genuine run. Do not report fabricated scores or outcomes.

## Security

Use fictional copy and synthetic forms only. Do not send private customer content into unapproved hosted model services. Inspect generated code before executing it in a sandboxed container/browser. Review [builder license gate](BUILDER_LICENSE_AUDIT.md) and the license of each chosen model, package, font and image. Deploy only after functional QA, appropriate authorization and human approval.
