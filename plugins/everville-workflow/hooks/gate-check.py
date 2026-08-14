#!/usr/bin/env python3
"""Emit factual SessionStart context in verified Everville repositories.

The hook performs one live repository-identity probe per SessionStart/resume.
Uncertain identity and subprocess failures emit no context. It never intercepts
tools, blocks work, or changes permission decisions.
"""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


OWNER = "everville-estate"


def run_command(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def run_git(cwd: str, *args: str) -> str:
    return run_command(["git", "-C", cwd, *args])


def canonical_everville_remote(remote: str) -> str:
    """Return a normalized GitHub remote, or empty when it is out of scope."""
    remote = remote.strip()
    if not remote:
        return ""

    if "://" in remote:
        parsed = urlsplit(remote)
        host = (parsed.hostname or "").lower()
        path = parsed.path
    else:
        match = re.fullmatch(r"(?:[^@/]+@)?([^:/]+):(.+)", remote)
        if not match:
            return ""
        host = match.group(1).lower()
        path = match.group(2)

    parts = [part for part in path.strip("/").split("/") if part]
    if host != "github.com" or len(parts) != 2 or parts[0].lower() != OWNER:
        return ""
    repository = parts[1]
    if repository.lower().endswith(".git"):
        repository = repository[:-4]
    return f"github.com/{OWNER}/{repository.lower()}" if repository else ""


def repository_identity(cwd: str):
    root = run_git(cwd, "rev-parse", "--show-toplevel")
    if not root:
        return None
    remote = canonical_everville_remote(
        run_git(root, "remote", "get-url", "origin")
    )
    return (os.path.realpath(root), remote) if remote else None


def emit_context(data: dict) -> int:
    cwd = data.get("cwd") or os.getcwd()
    if repository_identity(cwd) is None:
        return 0
    context = Path(__file__).with_name("gate-context.md").read_text(encoding="utf-8")
    sys.stdout.write(context)
    return 0


def main() -> int:
    return emit_context(json.load(sys.stdin))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        sys.exit(0)
