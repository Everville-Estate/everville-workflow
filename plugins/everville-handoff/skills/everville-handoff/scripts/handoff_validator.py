#!/usr/bin/env python3
"""Fail-closed structural and safety validation for Everville handoffs."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sys


SAFE_SLUG_RE = re.compile(r"[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?")
HANDOFF_FILENAME_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}-\d{6}-([a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?)\.md"
)
REQUIRED_METADATA = ("Created", "Repository", "Branch", "Head", "Continues from")
REQUIRED_SECTIONS = (
    "Current state",
    "Verification at checkpoint",
    "Recent commits",
    "Working tree",
    "Work completed",
    "Immediate next steps",
    "Decisions and rationale",
    "Critical files",
    "Blockers and external waits",
    "Environment requirements",
    "Assumptions and gotchas",
    "Pending and deferred",
    "Sharing status",
)
PLACEHOLDER_RE = re.compile(r"<[A-Z][A-Z0-9_-]*(?::[A-Z0-9_-]+)?>")
SECRET_PATTERNS = {
    "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
    "AWS access key": r"\bAKIA[0-9A-Z]{16}\b",
    "GitHub token": r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
    "provider secret": r"\b(?:sk_(?:live|test)_[A-Za-z0-9]{12,}|sk-[A-Za-z0-9_-]{20,})\b",
    "bearer credential": r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}",
    "credentialed URL": r"(?i)\b[a-z][a-z0-9+.-]*://[^\s/@:]+:[^\s/@]+@",
    "assigned secret value": r"(?im)^\s*(?:[-*]\s+)?(?:api[_-]?key|password|access[_-]?token|refresh[_-]?token|client[_-]?secret)\s*[:=]\s*(?!<|\[|REDACTED\b|NOT_SET\b)[\"']?[A-Za-z0-9._~+/=-]{8,}",
}


def validated_slug(raw: str) -> str:
    slug = raw.strip()
    if not SAFE_SLUG_RE.fullmatch(slug):
        raise ValueError(
            "slug must be 1-64 lowercase letters, digits, dots, underscores, or hyphens; "
            "it must start and end with a letter or digit"
        )
    return slug


def _metadata_values(text: str, label: str) -> list[str]:
    pattern = re.compile(rf"^\*\*{re.escape(label)}:\*\*\s*(.*?)\s*$", re.MULTILINE)
    return pattern.findall(text)


def _section_values(text: str, heading: str) -> list[str]:
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(?P<body>.*?)(?=^##\s|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return [match.group("body").strip() for match in pattern.finditer(text)]


def _meaningful(value: str) -> bool:
    return bool(re.search(r"[A-Za-z0-9]", PLACEHOLDER_RE.sub("", value)))


def validate_handoff(path: Path, repo_root: Path) -> list[str]:
    issues: list[str] = []
    path = path.resolve()
    repo_root = repo_root.resolve()
    expected_dir = repo_root / ".claude" / "handoffs"

    if path.parent != expected_dir:
        issues.append("handoff must be stored directly under .claude/handoffs/")
    if not HANDOFF_FILENAME_RE.fullmatch(path.name):
        issues.append("filename must be YYYY-MM-DD-HHMMSS-<safe-slug>.md")

    if not path.is_file():
        return [f"handoff does not exist: {path}", *issues]

    text = path.read_text(encoding="utf-8")
    titles = re.findall(r"^# Handoff:\s*(.*?)\s*$", text, re.MULTILINE)
    if len(titles) != 1 or not _meaningful(titles[0] if titles else ""):
        issues.append("exactly one non-empty '# Handoff: <title>' is required")

    for placeholder in PLACEHOLDER_RE.findall(text):
        issues.append(f"placeholder remains: {placeholder}")

    metadata: dict[str, str] = {}
    for label in REQUIRED_METADATA:
        values = _metadata_values(text, label)
        if len(values) != 1:
            issues.append(f"metadata '{label}' must appear exactly once")
            continue
        metadata[label] = values[0].strip()
        if not _meaningful(metadata[label]):
            issues.append(f"metadata '{label}' must have a non-placeholder value")

    created = metadata.get("Created")
    if created:
        try:
            parsed = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError("timezone missing")
            if parsed.astimezone(timezone.utc) > datetime.now(timezone.utc) + timedelta(minutes=5):
                issues.append("Created timestamp is in the future")
        except ValueError:
            issues.append("Created must be valid ISO 8601 and include a timezone")

    repository = metadata.get("Repository")
    if repository and not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        issues.append("Repository must be sanitized owner/repository")
    branch = metadata.get("Branch")
    if branch and (branch == "HEAD" or re.search(r"\s", branch)):
        issues.append("Branch must be a non-detached Git branch name without whitespace")
    head = metadata.get("Head")
    if head and not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", head):
        issues.append("Head must be a full 40- or 64-character commit SHA")
    predecessor = metadata.get("Continues from")
    if predecessor and predecessor.lower() != "none":
        if Path(predecessor).name != predecessor or not predecessor.endswith(".md"):
            issues.append("Continues from must be 'None' or a handoff filename without a path")

    for heading in REQUIRED_SECTIONS:
        values = _section_values(text, heading)
        if len(values) != 1:
            issues.append(f"section '## {heading}' must appear exactly once")
        elif not _meaningful(values[0]):
            issues.append(f"section '## {heading}' must contain a non-placeholder value")

    for label, pattern in SECRET_PATTERNS.items():
        if re.search(pattern, text):
            issues.append(f"possible {label}")

    if re.search(r"(?i)(?:/Users/[^/\s]+|/home/[^/\s]+|[A-Z]:\\Users\\[^\\\s]+)", text):
        issues.append("machine-specific home path found; use repository-relative paths")

    refs = set(
        re.findall(
            r"`((?:\.?/)?(?:[A-Za-z0-9_.@-]+/)+[A-Za-z0-9_.@-]+(?::\d+)?)`",
            text,
        )
    )
    for ref in sorted(refs):
        candidate = re.sub(r":\d+$", "", ref).removeprefix("./")
        if candidate.startswith((".claude/handoffs/", "http://", "https://")):
            continue
        if not (repo_root / candidate).exists():
            issues.append(f"missing referenced file: {ref}")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    slug_parser = subparsers.add_parser("slug", help="validate and print a safe filename slug")
    slug_parser.add_argument("value")
    validate_parser = subparsers.add_parser("validate", help="validate a handoff document")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    if args.command == "slug":
        try:
            print(validated_slug(args.value))
        except ValueError as error:
            print(f"INVALID SLUG: {error}", file=sys.stderr)
            return 2
        return 0

    issues = validate_handoff(args.path, args.repo_root)
    if issues:
        print("HANDOFF INVALID")
        for issue in issues:
            print(f"- {issue}")
        return 1
    print("HANDOFF VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
