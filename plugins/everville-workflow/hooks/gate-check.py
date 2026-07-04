#!/usr/bin/env python3
"""PreToolUse hard gate: deny Edit/Write in Everville repos until a whitelist
verdict has been recorded for this session.

The SessionStart reminder alone measured 0% compliance under neutral/competing
prompts (skill-comply, 2026-07-04) — this hook turns the reminder into a gate.
Fail-open by design: any unexpected error allows the edit rather than bricking
the session.
"""
import json
import os
import subprocess
import sys


def allow() -> None:
    sys.exit(0)


def main() -> None:
    data = json.load(sys.stdin)
    cwd = data.get("cwd") or os.getcwd()
    sid = data.get("session_id") or "unknown"
    tool_input = data.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""

    # Gate only Everville-Estate repos; everything else is out of scope.
    try:
        origin = subprocess.run(
            ["git", "-C", cwd, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=3,
        ).stdout.strip()
    except Exception:
        origin = ""
    if "Everville-Estate" not in origin:
        allow()

    if not file_path:
        allow()

    # Paths that never need the gate: agent bookkeeping, temp files,
    # plan/spec docs the ritual itself writes, and anything outside the repo.
    normalized = os.path.abspath(file_path).replace("\\", "/")
    repo_root = os.path.abspath(cwd)
    if not normalized.startswith(repo_root + os.sep):
        allow()
    for exempt in ("/.claude/", "/docs/superpowers/", "/tmp/", "/scratchpad/", "/memory/"):
        if exempt in normalized:
            allow()

    # The verdict flag lives in the git dir: never tracked, worktree-safe.
    try:
        git_dir = subprocess.run(
            ["git", "-C", cwd, "rev-parse", "--absolute-git-dir"],
            capture_output=True, text=True, timeout=3,
        ).stdout.strip()
    except Exception:
        git_dir = ""
    if not git_dir:
        allow()

    flag = os.path.join(git_dir, f"everville-gate-{sid}")
    if os.path.exists(flag):
        allow()

    sys.stderr.write(
        "everville-workflow gate: no whitelist verdict recorded for this session.\n"
        "1) Invoke the trivial-whitelist skill and state the verdict (trivial / non-trivial).\n"
        "2) If non-trivial: invoke unified-workflow and pick the track (FULL for tier-1/structural, LIGHT otherwise) before editing.\n"
        f"3) Record the verdict to unlock edits for this session: touch '{flag}'\n"
        "Do NOT touch the flag without doing steps 1-2 first — that defeats the gate and violates the plugin contract.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        # fail open: a broken gate must never brick editing
        sys.exit(0)
