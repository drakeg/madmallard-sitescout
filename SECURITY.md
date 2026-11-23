# Security Policy

Report vulnerabilities privately through GitHub security advisories where available; do not publish exploit details in issues.

Never expose credentials, payment data, or customer PII in generated sites or logs. Treat crawled pages as untrusted input and defend against prompt injection. Sandbox generated-code execution and browser automation; enforce network restrictions and resource limits. Restrict preview access, implement expiration, and label previews as independent concepts. Obtain appropriate rights to business content and imagery. Require explicit human approval for outreach and deployment; implement opt-out suppression and audit trails.

Docker live capture is default-off and requires a configured bearer token and per-process rate limiting. Do not expose the enabled endpoint to public networks; protect transport with TLS. For multi-worker/public deployment, replace process-local throttling with shared limits, per-user authentication and durable audit logging. Never commit capture tokens.
