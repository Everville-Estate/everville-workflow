#!/usr/bin/env python3
"""Repository-scoped advisory workflow gate for Claude Code hooks.

SessionStart emits context only inside an Everville-Estate GitHub repository.
PreToolUse denies the first relevant editor call or conservatively identified
mutating Bash call once per session and repository. This is an attention
speed-bump, not proof that a skill was invoked and not a shell sandbox.

Fail-open by design: unexpected input, Git failures, and marker write failures
must never prevent work.
"""

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


OWNER = "everville-estate"
EXEMPT_REPO_PREFIXES = (
    ".claude",
    "docs/superpowers",
    "memory",
    "scratchpad",
    "tmp",
)

MUTATING_COMMAND = re.compile(
    r"(?:^|[;&|\n]\s*)(?:sudo\s+|env\s+)*"
    r"(?:rm|mv|cp|touch|mkdir|rmdir|install|chmod|chown|ln|truncate|dd|tee|"
    r"patch|apply_patch)\b"
)
INTERPRETER_COMMAND = re.compile(
    r"(?:^|[;&|\n]\s*)(?:sudo\s+|env\s+)*"
    r"(?:python(?:[0-9.]+)?|node|ruby|perl|php|bash|zsh|sh)\b"
)
MUTATING_GIT = re.compile(
    r"(?:^|[;&|\n]\s*)git(?:\s+-\S+)*\s+"
    r"(?:apply|checkout|switch|reset|clean|restore|commit|merge|rebase|"
    r"cherry-pick|revert|stash|pull)\b"
)
MUTATING_PACKAGE_MANAGER = re.compile(
    r"(?:^|[;&|\n]\s*)(?:npm|pnpm|yarn|bun)\s+"
    r"(?:add|install|remove|uninstall|update|upgrade)\b"
)
SED_IN_PLACE = re.compile(
    r"(?:^|[;&|\n]\s*)sed\b[^;&|\n]*(?:\s-i\b|\s-i[^\s]+)"
)
SHELL_REDIRECTION = re.compile(r"(?:^|[^<>])>{1,2}(?!>)")


def run_git(cwd: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", cwd, *args],
        capture_output=True,
        text=True,
        timeout=3,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def canonical_everville_remote(remote: str) -> str:
    """Return a normalized GitHub remote, or an empty string when out of scope."""
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
    if not repository:
        return ""
    return f"github.com/{OWNER}/{repository.lower()}"


def repository_identity(cwd: str):
    root = run_git(cwd, "rev-parse", "--show-toplevel")
    if not root:
        return None
    remote = canonical_everville_remote(run_git(root, "remote", "get-url", "origin"))
    if not remote:
        return None
    return os.path.realpath(root), remote


def repo_relative_path(cwd: str, repo_root: str, file_path: str):
    if not file_path:
        return None
    absolute = file_path if os.path.isabs(file_path) else os.path.join(cwd, file_path)
    absolute = os.path.realpath(absolute)
    try:
        if os.path.commonpath((repo_root, absolute)) != repo_root:
            return None
    except ValueError:
        return None
    return os.path.relpath(absolute, repo_root).replace(os.sep, "/")


def is_exempt(relative_path: str) -> bool:
    return any(
        relative_path == prefix or relative_path.startswith(prefix + "/")
        for prefix in EXEMPT_REPO_PREFIXES
    )


def bash_may_mutate(command: str) -> bool:
    """Conservatively identify common Bash mutation surfaces.

    This deliberately treats general-purpose interpreters as potentially
    mutating. It covers common bypasses but cannot prove arbitrary shell code
    is read-only; the hook remains an advisory attention gate.
    """
    if not command:
        return False
    return any(
        pattern.search(command)
        for pattern in (
            SHELL_REDIRECTION,
            MUTATING_COMMAND,
            INTERPRETER_COMMAND,
            MUTATING_GIT,
            MUTATING_PACKAGE_MANAGER,
            SED_IN_PLACE,
        )
    )


def marker_path(session_id: str, repo_root: str, remote: str) -> Path:
    identity = json.dumps(
        [session_id, os.path.realpath(repo_root), remote],
        separators=(",", ":"),
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return Path(os.path.expanduser("~/.cache/everville-gate")) / digest


def create_marker_or_allow(marker: Path) -> bool:
    """Create the marker and return True; return False to fail open."""
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        with marker.open("x", encoding="utf-8") as handle:
            handle.write("denied-once\n")
        return True
    except FileExistsError:
        return False
    except OSError:
        return False


def emit_context(data: dict) -> int:
    cwd = data.get("cwd") or os.getcwd()
    if repository_identity(cwd) is None:
        return 0
    context = Path(__file__).with_name("gate-context.md").read_text(encoding="utf-8")
    sys.stdout.write(context)
    return 0


def pre_tool_use(data: dict) -> int:
    cwd = data.get("cwd") or os.getcwd()
    identity = repository_identity(cwd)
    if identity is None:
        return 0
    repo_root, remote = identity

    tool_name = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    if tool_name == "Bash":
        command = tool_input.get("command") or ""
        if not bash_may_mutate(command):
            return 0
    elif tool_name in ("Edit", "Write", "NotebookEdit"):
        file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        relative = repo_relative_path(cwd, repo_root, file_path)
        if relative is None or is_exempt(relative):
            return 0
    else:
        return 0

    session_id = str(data.get("session_id") or "unknown")
    marker = marker_path(session_id, repo_root, remote)
    if marker.exists():
        return 0
    if not create_marker_or_allow(marker):
        return 0

    sys.stderr.write(
        "everville-workflow one-time advisory gate: before this mutation —\n"
        "1) Invoke trivial-whitelist and STATE the verdict (trivial / non-trivial).\n"
        "2) If non-trivial, invoke unified-workflow and select FULL or LIGHT yourself.\n"
        "3) Retry the tool call; this speed-bump fires once per session and repository.\n"
        "This hook covers editor tools and common mutating Bash forms; it is not a shell sandbox "
        "and does not prove that the skills were invoked.\n"
    )
    return 2


def main() -> int:
    data = json.load(sys.stdin)
    if "--context" in sys.argv[1:]:
        return emit_context(data)
    return pre_tool_use(data)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        # A broken advisory hook must never brick a Claude Code session.
        sys.exit(0)
