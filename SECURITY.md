# Security Policy

Report vulnerabilities privately through GitHub security advisories where available; do not publish exploit details in issues.

Never expose credentials, payment data, or customer PII in generated sites or logs. Treat crawled pages as untrusted input and defend against prompt injection. Sandbox generated-code execution and browser automation; enforce network restrictions and resource limits. Restrict preview access, implement expiration, and label previews as independent concepts. Obtain appropriate rights to business content and imagery. Require explicit human approval for outreach and deployment; implement opt-out suppression and audit trails.

Docker live capture is default-off and requires a configured bearer token and per-process rate limiting. Do not expose the enabled endpoint to public networks; protect transport with TLS. For multi-worker/public deployment, replace process-local throttling with shared limits, per-user authentication and durable audit logging. Never commit capture tokens.

The Docker dashboard is reachable on trusted LAN interfaces by default (`SITESCOUT_BIND=0.0.0.0`), but live capture and authenticated job endpoints are still disabled by default. Never route port 8087 to the public Internet. Bearer credentials must not cross unencrypted LAN HTTP; enabling capture requires TLS termination and restricted network access. The optional worker profiles publish no host ports. Set `SITESCOUT_BIND=127.0.0.1` for host-only access.
