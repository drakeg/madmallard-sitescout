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
