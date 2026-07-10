# Resume checklist

## Identity and history

- [ ] Read the complete selected handoff.
- [ ] Normalize current `origin` and match the handoff `owner/repository` exactly.
- [ ] Confirm the handoff commit exists locally; fetch only when authorized and needed.
- [ ] Classify the current head as exact, advanced, or diverged using commit ancestry.
- [ ] Treat a branch-name mismatch as a reconciliation signal, not repository identity.
- [ ] Parse the created timestamp with timezone and reject invalid/future values.

## Working state

- [ ] Run `git status --short` and preserve unrelated work.
- [ ] Compare current changes with the handoff working-tree snapshot.
- [ ] Diff the handoff commit to current head and inspect every changed critical file.
- [ ] Re-check blockers, external waits, assumptions, and referenced files.
- [ ] Re-run the latest relevant validation rather than trusting old pass statements.

## Environment without disclosure

Check only whether named variables exist; never print their values:

```bash
python3 - API_URL DATABASE_URL <<'PY'
import os, sys
for name in sys.argv[1:]:
    print(f'{name}: {"set" if name in os.environ else "missing"}')
PY
```

- [ ] Verify required variable names from the handoff are present.
- [ ] Verify services/processes through health/status commands that do not expose credentials.
- [ ] Never use `env`, `printenv`, `set`, or shell tracing as handoff evidence.

## Stop and investigate

Do not follow the saved next step when:

- repository identity differs;
- the handoff commit is unavailable or not an ancestor of current head;
- critical files disappeared or changed incompatibly;
- a safety, authorization, or source-of-truth assumption is invalid;
- the handoff contains a secret, machine-only absolute path, unresolved placeholder, or missing reference;
- current dirty changes overlap the planned work and ownership is unclear.

## Continue

- [ ] Start with the first next step that remains valid after reconciliation.
- [ ] Preserve the documented patterns and rationale.
- [ ] Create a new linked handoff for a later durable boundary; do not rewrite history in the old one.
- [ ] Keep the new handoff local unless the user separately authorizes commit/share/push.
