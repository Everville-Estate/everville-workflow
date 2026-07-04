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

    # Speed-bump design (4th iteration, all verified live 2026-07-04): there is
    # NO location a headless session can reliably write a flag to — .git/ trips
    # the sensitive-path guard, ~/.cache needs a Bash grant, and .claude/ is
    # blocked by Claude Code's own config protection. So the HOOK records the
    # marker itself: first Edit/Write in an Everville repo is denied with the
    # gate instructions (forcing the verdict into attention — measured to be
    # the lever that flips compliance to 100%), and the retry passes. The model
    # never needs write permission anywhere.
    marker_dir = os.path.expanduser("~/.cache/everville-gate")
    marker = os.path.join(marker_dir, f"{sid}-{os.path.basename(repo_root)}")
    if os.path.exists(marker):
        allow()

    try:
        os.makedirs(marker_dir, exist_ok=True)
        with open(marker, "w") as fh:
            fh.write(f"denied-once cwd={repo_root} file={file_path}\n")
    except Exception:
        pass  # fail open on the next attempt regardless

    sys.stderr.write(
        "everville-workflow gate (one-time this session): before this edit —\n"
        "1) Invoke the trivial-whitelist skill and STATE the verdict (trivial / non-trivial) in your reply.\n"
        "2) If non-trivial: invoke unified-workflow and pick the track (FULL for tier-1/structural, LIGHT otherwise). Decide yourself — do not ask the user which track.\n"
        "3) Then retry the edit — it will pass. This gate fires once per session per repo.\n"
        "Retrying without stating the verdict violates the plugin contract.\n"
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
