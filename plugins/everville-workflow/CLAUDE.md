# everville-workflow — Plugin Rules

When this plugin is enabled, Claude Code must consult the `unified-workflow` skill at the start of any non-trivial task. Use the `trivial-whitelist` skill to decide whether a change is trivial.

## Skills in this plugin

- `unified-workflow` — 11-step development ritual (see `skills/unified-workflow/SKILL.md`)
- `trivial-whitelist` — hard list of ritual-skip change types (see `skills/trivial-whitelist/SKILL.md`)
- `everville-skill-judge` — 130-point rubric for accepting new skills (adapted from softaworks, adds D9 Everville Fit)
- `everville-reduce-entropy` — bias toward deletion; invoked during ISOLATE step
- `everville-agent-md-refactor` — split bloated repo CLAUDE.md files via progressive disclosure
- `everville-lesson-learned` — extract SE lessons from diffs; optional auto-memory feedback persistence
- `everville-production-audit` — pre-deploy ship/block readiness gate on the release surface (RLS, migration rollback, idempotency, env fail-fast); invoked at the verify→finish boundary
- `everville-skill-stocktake` — audit the standing skill set for rot/overlap/drift (Keep/Improve/Update/Retire/Merge); orchestrates `everville-skill-judge` per skill, adds cross-skill overlap detection
- `everville-skill-comply` — measure runtime skill compliance via `claude -p` (does a skill get obeyed when the prompt competes against it?); bundled harness + scenarios; completes the judge→stocktake→comply trio (design → set → behavior)

## Agents in this plugin

- `codebase-pattern-finder` — read-only Sonnet agent for BRAINSTORM step; surfaces existing Next.js/Supabase/Drizzle/shadcn patterns before new design

## Commands in this plugin

- `/explain-pr-changes` — generate PR body from diff; creates or updates PR; grades any existing body against Why/What/How
- `/review-self` — self-review diff as mental model before requesting code review
- `/review-post` — post severity-tagged review findings onto the PR as one atomic, de-duped review with an APPROVE/REQUEST_CHANGES/COMMENT verdict

## Install prerequisites

This plugin's `unified-workflow` skill references several `superpowers:*` skills. Users must install `superpowers` separately:

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

## Plugin versioning

- 0.1.0 — Initial release: unified-workflow + trivial-whitelist skills (Phase 0)
- 0.1.1 — Doc fix: remove invalid `github:` prefix from marketplace add commands
- 0.2.0 — Adopted 7 items from softaworks/agent-toolkit (MIT): everville-skill-judge (with 9th dimension "Everville Fit"), everville-reduce-entropy, everville-agent-md-refactor, everville-lesson-learned, codebase-pattern-finder agent, /explain-pr-changes, /review-self. Attribution in `LICENSES/softaworks-MIT.txt`.
- 0.3.0 — Workflow de-prescription pass (derived from current Anthropic prompting guidance): milestone-level plans replace 2-5-minute micro-tasks, brainstorm gated on genuine ambiguity, TDD invariant kept but per-line choreography dropped, REVIEW step now leads with a fresh-context verifier subagent (parallel reviewers by default, /review-self demoted to optional pre-pass), VERIFY adds evidence-grounded progress claims, "err on the side of asking" relaxed to pause-only-when-user-input-is-genuinely-required (also in trivial-whitelist edge cases), stale /mental-model usage examples fixed.
- 0.4.0 — Model-agnostic recalibration: the 0.3.0 guidance is sound on any current model, but two items were calibrated to one model's failure modes and are now balanced both ways — handoff triggers restore context-checkpointing without encouraging premature wrap-up, and the unified-workflow hard rule warns against both skipping steps and over-asking. Stripped model-name branding from the changelog and plugin-forge commit-trailer example.
- 0.5.0 — REVIEW upgrade (mined from top community skills — AutoGPT, NousResearch): a 4-tier severity taxonomy (🔴 Blocker / 🟠 Should-fix / 🟡 Nice-to-have / 🔵 Nit) is now the required vocabulary for the REVIEW step's findings; new `/review-post` command lands those findings on the GitHub PR as one atomic, de-duped review with an APPROVE/REQUEST_CHANGES/COMMENT verdict; `/explain-pr-changes` now grades any existing PR body against Why/What/How instead of blindly overwriting it.
- 0.6.0 — New `everville-production-audit` skill (adapted from affaan-m/ECC production-audit): a release-surface ship/block gate added as step 9.5 (verify→finish). Local-evidence-only audit of RLS/authz, migration reversibility, webhook/job idempotency, env fail-fast, and secrets, with hard score-caps (BLOCK at 69 for missing RLS / non-idempotent webhook / irreversible migration / leakable secret) and mandatory Evidence-checked / Evidence-missing output. Tuned to the Everville stack (Supabase/Drizzle/Vercel/Next) and house hard rules.
- 0.7.0 — New `everville-skill-stocktake` skill (adapted from affaan-m/ECC skill-stocktake): periodic marketplace rot/overlap/drift audit that orchestrates `everville-skill-judge` per skill and adds cross-skill overlap clustering; Keep/Improve/Update/Retire/Merge verdicts with a decision-enabling reason rule (name the defect + the replacement, ban "superseded"); read-only, defers deletion to user sign-off + `everville-reduce-entropy`. Plus a `parallel-agent-locking` reference under unified-workflow (heartbeat lock contract from AutoGPT pr-test) wired into the ISOLATE step to address the shared-worktree collision burn.
- 0.8.0 — New `everville-skill-comply` skill (adapted from affaan-m/ECC skill-comply): a runtime compliance harness that runs scenarios through `claude -p` in plan mode inside a real Everville repo and classifies whether the expected skills fired, reporting a compliance rate per competition level (supportive/neutral/competing) with a THEATER WARNING when a skill folds under a competing prompt. Bundled `scripts/skill_comply.py` + seed scenarios for unified-workflow and trivial-whitelist. Completes the judge→stocktake→comply trio (design → set → behavior). Budget-truncated runs are scored INCONCLUSIVE, not non-compliant (a real correctness fix found during live verification).

## Maintainers

@nikoasta, @balicopter, @maslennikov-ig
