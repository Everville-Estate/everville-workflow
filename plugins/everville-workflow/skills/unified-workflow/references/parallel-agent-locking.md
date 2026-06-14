# Parallel-agent locking — when subagents must share one checkout

The team has been burned by this: background build agents dispatched in parallel **share one git worktree**, collide on `HEAD` (one checks out a branch while another is mid-commit), and corrupt each other's state. The default fix is in the ISOLATE step — give each agent its own worktree (`superpowers:using-git-worktrees`) or sequence them. Parallel is safe for **read-only** analysis agents.

When agents genuinely must write to a **shared** resource (one worktree, one build dir, one scratch file) and you can't isolate, serialize the critical section with a lock. This is the protocol — adapted from AutoGPT's `pr-test` lock contract.

## The contract

A lock is a directory (atomic to create) holding a heartbeat file. Holder writes its pid + a timestamp every few seconds; a waiter reclaims the lock only if the heartbeat has gone stale (holder died without releasing). A shell `trap` releases on exit so a crash doesn't wedge the lock forever.

```bash
LOCK_DIR=".worktree.lock"
STALE_SECS=30
HEARTBEAT="$LOCK_DIR/heartbeat"

acquire_lock() {
  while true; do
    if mkdir "$LOCK_DIR" 2>/dev/null; then          # atomic: only one wins
      echo "$$" > "$LOCK_DIR/pid"
      date +%s > "$HEARTBEAT"
      trap 'rm -rf "$LOCK_DIR"' EXIT                  # release on any exit
      ( while true; do date +%s > "$HEARTBEAT"; sleep 5; done ) &
      HEARTBEAT_PID=$!
      return 0
    fi
    # Lock held — reclaim only if heartbeat is stale (holder died)
    local last; last=$(cat "$HEARTBEAT" 2>/dev/null || echo 0)
    if [ $(( $(date +%s) - last )) -gt "$STALE_SECS" ]; then
      rm -rf "$LOCK_DIR"                              # stale-reclaim
      continue
    fi
    sleep 2
  done
}

release_lock() { kill "$HEARTBEAT_PID" 2>/dev/null; rm -rf "$LOCK_DIR"; trap - EXIT; }
```

Each agent calls `acquire_lock` before touching the shared resource and `release_lock` after. Hold the lock for the smallest possible critical section (the `git` op, the build), not the whole task.

## Rules

- **Isolation beats locking.** Reach for this only when a separate worktree genuinely isn't possible. A lock serializes — it throws away the parallelism you dispatched agents to get. If the agents spend most of their time in the critical section, just sequence them instead.
- **Heartbeat interval < stale threshold.** 5s heartbeat vs 30s stale leaves margin for a slow tick before a live holder is wrongly reclaimed.
- **Always `trap` the release.** A crashed agent that took the lock without a trap wedges every waiter until the stale timeout — and if its heartbeat subshell outlives it, forever.
- **One lock per shared resource**, named for what it guards (`.worktree.lock`, `.builddir.lock`), so unrelated work doesn't contend.
