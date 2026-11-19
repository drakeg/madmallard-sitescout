# Releases and Versioning

Use [Semantic Versioning](https://semver.org/) for published releases and maintain CHANGELOG.md.

- **Patch** `x.y.Z`: backward-compatible bug, documentation, dependency security or accessibility fixes.
- **Minor** `x.Y.0`: backward-compatible capabilities, such as a new builder adapter, audit or dashboard feature.
- **Major** `X.0.0`: incompatible API/schema/configuration or user-facing workflow changes requiring migration.
- Before 1.0, breaking changes may occur in minor releases, but must be called out explicitly.
- Prerelease tags: `v0.1.0-alpha.1`, `v0.1.0-beta.1`, `v0.1.0-rc.1`.

## Release triggers
Release when a meaningful tested increment is ready, not automatically after every PR. Target a minor release at the end of a completed sprint when user-facing functionality warrants it; patch promptly for fixes. Major only for documented incompatible changes.

## Release checklist
1. Scope and acceptance criteria complete; CI and security scans green.
2. Review dependencies, licensing and generated artifacts; confirm no secrets.
3. Update CHANGELOG and migration instructions; confirm rollback path.
4. Build immutable artifact, tag reviewed main commit, publish GitHub release with notes.
5. Verify Compose deployment and smoke tests; document known limitations.

No release is implied by a merge. Sprint 0 scaffold is unreleased until checks are complete.
