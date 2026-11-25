"""Validate the checked-in source-verified builder candidate registry.

This never calls upstream services and does not claim current license approval.
A fresh upstream review is required before any commercial integration.
"""
import json
import re
from pathlib import Path

LICENSES = {"MIT", "Apache-2.0"}
DECISIONS = {
    "pilot-local-editor", "defer-hosted-dependency",
    "evaluate-source-only-after-asset-replacement", "evaluate-local-agent",
    "output-framework-candidate", "local-inference-candidate",
}
EXPECTED_IDS = {"openpage", "open-lovable", "onlook", "opencode", "astro", "ollama"}


def validate_registry(registry):
    if not isinstance(registry, dict) or not isinstance(registry.get("candidates"), list):
        raise ValueError("Builder registry must contain candidates")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", registry.get("reviewed_on", "")):
        raise ValueError("Builder audit must have a review date")
    seen = set()
    for candidate in registry["candidates"]:
        if not isinstance(candidate, dict):
            raise ValueError("Candidate must be an object")
        identifier = candidate.get("id")
        if identifier in seen:
            raise ValueError("Duplicate builder candidate")
        seen.add(identifier)
        repository = candidate.get("repository", "")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Invalid upstream GitHub repository")
        if candidate.get("license") not in LICENSES:
            raise ValueError("Unverified or unsupported top-level license")
        if not re.fullmatch(r"[0-9a-f]{40}", candidate.get("license_blob", "")):
            raise ValueError("Missing exact observed upstream LICENSE blob SHA")
        if candidate.get("recommendation") not in DECISIONS:
            raise ValueError("Unreviewed builder integration recommendation")
        if candidate.get("risk") not in {"low", "medium", "high"}:
            raise ValueError("Missing integration risk")
        if not isinstance(candidate.get("required_external"), list):
            raise ValueError("Mandatory external service dependencies must be explicit")
        if not isinstance(candidate.get("optional_external"), list):
            raise ValueError("Optional dependencies must be explicit")
        evidence = candidate.get("evidence", [])
        if not isinstance(evidence, list) or len(evidence) < 2:
            raise ValueError("Source evidence links required")
        prefix = "https://github.com/" + repository + "/blob/" + candidate.get("ref", "") + "/"
        if not all(isinstance(link, str) and link.startswith(prefix) for link in evidence):
            raise ValueError("Evidence must link to exact upstream branch files")
        if not any(link.endswith("/LICENSE") for link in evidence):
            raise ValueError("Every candidate requires explicit LICENSE evidence")
        for key, minimum_length in (("role", 5), ("local_mode", 15), ("commercial_note", 15)):
            if not isinstance(candidate.get(key), str) or len(candidate[key]) < minimum_length:
                raise ValueError("Required candidate assessment is missing")
    if seen != EXPECTED_IDS:
        raise ValueError("Expected builder candidate inventory is incomplete")
    return True


if __name__ == "__main__":
    data = json.loads(Path("docs/builder-candidates.json").read_text(encoding="utf-8"))
    validate_registry(data)
    print("Builder candidate license audit registry validated (source review only)")
