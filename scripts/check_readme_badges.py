"""Validate supported README badges against repository files (no network needed)."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"

def validate():
    content = README.read_text(encoding="utf-8")
    title = content.splitlines()[0]
    assert title.startswith("# "), "README must begin with a project title"
    start, end = "<!-- badges:start -->", "<!-- badges:end -->"
    assert content.count(start) == content.count(end) == 1, "Exactly one badge section required"
    prefix, rest = content.split(start, 1)
    badges, remainder = rest.split(end, 1)
    assert not prefix.strip() or prefix.strip() == title, "Badges must appear immediately after title"
    assert remainder.strip(), "Preserve project description after badges"
    assert "shields.io" in badges and "github.com/" in badges
    for link in re.findall(r'\]\(([^)]+)\)', badges):
        if not link.startswith(("https://", "http://")):
            assert (ROOT / link).is_file(), f"Badge link target missing: {link}"
    docker = (ROOT / "Dockerfile").read_text()
    ci = (ROOT / ".github/workflows/ci.yml").read_text()
    assert "FROM python:3.15-slim" in docker
    assert "python-version: '3.15'" in ci
    assert "Python-3.15-" in badges
    assert (ROOT / "compose.yaml").is_file() and "Docker-Compose-" in badges
    assert (ROOT / "vercel.json").is_file() and "Vercel-Deployment-" in badges
    assert (ROOT / ".github/workflows/ci.yml").is_file()
    assert "actions/workflows/ci.yml/badge.svg" in badges
    assert "img.shields.io/github/issues/" in badges
    assert "img.shields.io/github/issues-pr/" in badges
    assert not re.search(r'(?i)(passing|failing|license-mit|release-v\d)', badges), "Unsupported hardcoded status"
    print("README badges validated")

if __name__ == "__main__":
    validate()
