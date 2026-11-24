"""Fail-closed operator bearer-token identity for future private job API.

Tokens are represented by SHA-256 digests in the environment, not plaintext.
Use unpredictable 32+-byte random tokens and TLS on any network transport.
This is a foundation only: no HTTP route or public authentication is enabled.
"""
import hashlib
import hmac
import json
import os
import re

ACTOR_NAME = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")


def load_operator_digests(value=None):
    raw = os.environ.get("SITESCOUT_OPERATOR_TOKEN_HASHES", "") if value is None else value
    try:
        mapping = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise ValueError("Operator authentication configuration is invalid") from exc
    if not isinstance(mapping, dict) or not mapping or len(mapping) > 25:
        raise ValueError("At least one and at most 25 operators are required")
    seen = set()
    for actor, digest in mapping.items():
        if not isinstance(actor, str) or not ACTOR_NAME.fullmatch(actor):
            raise ValueError("Operator name is invalid")
        if not isinstance(digest, str) or not DIGEST.fullmatch(digest):
            raise ValueError("Operator token digest must be lowercase SHA-256")
        if digest in seen:
            raise ValueError("Duplicate operator token digests are forbidden")
        seen.add(digest)
    return mapping


def authenticate_operator(headers, *, configuration=None):
    """Return (status, actor). 503 denotes invalid/missing configuration."""
    try:
        operators = load_operator_digests(configuration)
    except ValueError:
        return 503, None
    header = headers.get("Authorization", "")
    if not isinstance(header, str) or not header.startswith("Bearer "):
        return 401, None
    token = header[7:]
    if not token or len(token) < 32 or len(token) > 512:
        return 401, None
    supplied = hashlib.sha256(token.encode("utf-8")).hexdigest()
    matched_actor = None
    # Compare all configured digests; avoid early-exit account enumeration.
    for actor, expected in operators.items():
        if hmac.compare_digest(supplied, expected):
            matched_actor = actor
    return (200, matched_actor) if matched_actor else (401, None)
