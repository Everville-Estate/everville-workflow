# everville-workflow — Plugin Rules

When this plugin is enabled, Claude Code must consult the `unified-workflow` skill at the start of any non-trivial task. Use the `trivial-whitelist` skill to decide whether a change is trivial. Since 0.9.0 this gate is also injected by a SessionStart hook (`hooks/gate-context.md`) — enforcement no longer relies on description-matching alone.

## Skills in this plugin

- `unified-workflow` — two-track development ritual: FULL 11-step for tier-1/structural changes, LIGHT 4-step (echo → implement → independent verify → ship) otherwise (see `skills/unified-workflow/SKILL.md`)
- `trivial-whitelist` — hard list of ritual-skip change types (see `skills/trivial-whitelist/SKILL.md`)
- `everville-skill-judge` — 130-point rubric for accepting new skills (adapted from softaworks, adds D9 Everville Fit)
- `everville-reduce-entropy` — bias toward deletion; invoked during ISOLATE step
- `everville-agent-md-refactor` — split bloated repo CLAUDE.md files via progressive disclosure
- `everville-lesson-learned` — extract SE lessons from diffs; optional auto-memory feedback persistence
- `everville-production-audit` — pre-deploy ship/block readiness gate on the release surface (RLS, migration rollback, idempotency, env fail-fast); invoked at the verify→finish boundary
- `everville-skill-stocktake` — audit the standing skill set for rot/overlap/drift (Keep/Improve/Update/Retire/Merge); orchestrates `everville-skill-judge` per skill, adds cross-skill overlap detection
- `everville-skill-comply` — measure runtime skill compliance via `claude -p` (does a skill get obeyed when the prompt competes against it?); bundled harness + scenarios; completes the judge→stocktake→comply trio (design → set → behavior)
- `loop-on-ci` — fail → diagnose → smallest fix → push → re-watch cycle for PR checks via `gh`; encodes the Everville CI traps (E2E suite serialization, stale same-name runs, kb:map drift, Review Gate re-arm, headRefOid merge race). Merged adaptation of cursor-team-kit fix-ci + loop-on-ci (MIT)

## Agents in this plugin

- `codebase-pattern-finder` — read-only Sonnet agent for BRAINSTORM step; surfaces existing Next.js/Supabase/Drizzle/shadcn patterns before new design
- `ci-watcher` — background Haiku agent that watches PR checks and reports the first actionable error with a pre-existing-on-main verdict; dispatch instead of polling CI in the main session (adapted from cursor-team-kit, MIT)

## Commands in this plugin

- `/explain-pr-changes` — generate PR body from diff; creates or updates PR; grades any existing body against Why/What/How; changesets are dependency-ordered and end with a Gotchas section (absorbed `/review-self` in 0.9.0)

## Hooks in this plugin

- `SessionStart` — injects the workflow gate (`hooks/gate-context.md`) into every session: trivial-whitelist verdict before any change, verifier ≠ implementer, 3-line approval format, no silent step-skipping
- `PreToolUse` (Edit|Write|NotebookEdit) — `hooks/gate-check.py` hard gate: in Everville-Estate repos the first edit is **denied** until a whitelist verdict is recorded (`touch <git-dir>/everville-gate-<session_id>`). Exempt: non-Everville repos, paths outside the repo, `.claude/`, `docs/superpowers/`, temp/memory paths. Fail-open on script error

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

- 0.9.0 — Stocktake actions (full audit 2026-07-04, all 14 components judged + usage data from 63 sessions: 318 merged PRs vs 5 ritual invocations). **Enforcement:** new SessionStart gate hook — the ritual no longer relies on description-matching alone. **Two-track ritual:** FULL 11-step reserved for tier-1/structural changes; new LIGHT 4-step track (echo assumptions → TDD implement → independent verify → ship) for everything else non-trivial — friction was the main reason the ritual was skipped. **Fixes:** lesson-learned persisted memory to a previous machine's hardcoded path (silent total failure) — now resolves the memory root by glob; skill-comply cache path was missing the version segment — now resolves latest; explain-pr-changes template was truncated mid-file (unclosed fence) — completed, plus `Close #N` auto-close fix; handoff staleness check used GNU/BSD-incompatible date parsing that broke on macOS — now python3 ISO-8601; trivial-whitelist stale `knowledge/decisions/` path → everville-core KB, and closed the loophole where SKILL.md/agent files passed as "doc-only". **Retired:** `/review-post` (built-in `/code-review --comment` covers posting; severity→verdict mapping folded into unified-workflow step 8) and `/review-self` (dependency-ordered changesets + Gotchas absorbed into `/explain-pr-changes`). **Rewritten:** codebase-pattern-finder agent from 237 verbatim-upstream lines (generic Express examples) to a 40-line documentarian contract with Everville-stack output shape. **Re-routed:** step 3.5 CONTEXT7 PREFETCH → DOCS PREFETCH (neuledge-context L1, context7 L2 fallback), matching the global docs-routing rule; Beads gets an explicit no-`bd` fallback. Handoff 0.3.1: scope note — native resume covers same-machine continuation; handoff is for cross-machine/cross-agent boundaries.

- 0.10.0 — Hard gate (follow-up to the 0.9.0 comply measurement: supportive 100% / neutral 0% / competing 0% — the SessionStart reminder alone is theater). New PreToolUse hook `gate-check.py` denies the first Edit/Write in an Everville-Estate repo until the session's whitelist verdict is recorded as a flag in the git dir; deny message walks the agent through whitelist → track choice → flag. Scoped: non-Everville repos and agent-bookkeeping paths are exempt; fails open on any script error so a broken gate can never brick editing.

- 0.11.0 — Adopted the CI trio from cursor/plugins cursor-team-kit (MIT, `LICENSES/cursor-MIT.txt`): `fix-ci` + `loop-on-ci` merged into one `loop-on-ci` skill (their triggers overlap — "fix failing CI" ⊂ "loop until green"; intake-time merge per stocktake doctrine) and a `ci-watcher` background Haiku agent so waiting on CI is a dispatch, not main-session polling. Both adapted with the team's burned-in CI lessons: E2E suites share one test project (serialize, incl. main's push CI), latest-run-per-name when re-triggers leave a stale fail, Review Gate evidence expires on push, `pnpm kb:map` drift on any new root file, and the headRefOid merge race. Passed skill-judge intake gate before merge.

## Maintainers

@nikoasta, @balicopter, @maslennikov-ig
