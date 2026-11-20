# Contributing

## Workflow
1. Open an issue describing user value, scope, test plan, acceptance criteria, and sprint/backlog reference.
2. Branch `feat/<issue>-summary`, `fix/<issue>-summary`, or `docs/<issue>-summary`.
3. Make focused commits (Conventional Commits preferred), update docs/tests, and open a PR against main.
4. PR template must include change summary, risks, tests, screenshots for UI changes, licensing implications, and linked issue.
5. Require review and green CI before merging; squash merges preferred. No direct pushes to protected main.

## Local development
Python 3.12+ is recommended for the scaffold. Run `python3 -m unittest discover -s tests -v` or `docker compose up --build`. Copy `.env.example` to `.env`; never commit credentials.

## Standards
Use type hints and small modules. Avoid vendor lock-in. Include unit, integration, browser, and accessibility tests as relevant. Use fixtures or authorized demo sites rather than uncontrolled crawling of third parties. New third-party dependencies require a recorded commercial-license review.

## Code of conduct
Be respectful, constructive, and security-conscious. Report vulnerabilities privately as described in SECURITY.md.

## Badge review gate

Every PR changing stack, supported versions, CI workflows, release policy, license or deployment configuration must inspect the README badges and run `python3 scripts/check_readme_badges.py`. The CI workflow enforces badge placement, links, supported runtime claims and dynamic workflow/status conventions. Refer to `AGENTS.md` and the central repository standards for the full policy.
