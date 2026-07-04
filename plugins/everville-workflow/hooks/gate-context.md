<everville-workflow-gate>
Standing gate for this session (from the everville-workflow plugin):

1. Before ANY code change, get a verdict from the `trivial-whitelist` skill: trivial → edit directly; non-trivial → invoke `unified-workflow` and pick the track (FULL for tier-1/structural, LIGHT otherwise). Do not start implementing before the verdict. In Everville-Estate repos this is enforced: the first Edit/Write is denied until you record the verdict by touching a flag under `~/.cache/everville-gate/` (the deny message gives the exact path). Touching the flag without steps above violates the plugin contract. **The gate is never a reason to ask the user anything** — decide the verdict and the track yourself, record the flag, proceed, and note the choice in one line; pause for the user only where the unified-workflow hard rule genuinely requires it (destructive/irreversible action, real scope change, input only they hold).
2. Verifier ≠ implementer: every non-trivial change gets an independent check (fresh-context verifier or /code-review) before merge; tier-1 (balicopter/financial/investor-facing) always.
3. When asking the user for approval: ≤3 lines — what changes → blast radius → rollback; one decision per ask.
4. Note any consciously skipped step in the PR body — skipping silently is the one hard NO.
</everville-workflow-gate>
