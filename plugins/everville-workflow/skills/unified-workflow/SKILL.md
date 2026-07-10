---
name: unified-workflow
description: Use when starting a non-trivial feature, bug fix, refactor, migration, or runtime-affecting change in an Everville project. Route first through trivial-whitelist, then use either the LIGHT four-phase track for ordinary non-trivial work or the FULL 11-step track for critical or structural work. Covers planning, docs, isolation, implementation, preview/E2E, stable-SHA review, verification, production audit, PR integration, and closeout with explicit fallbacks when optional tools are unavailable.
---

# Unified Workflow

Use this skill at the start of non-trivial work in an Everville project. Invoke `trivial-whitelist` first; its verdict is one of:

- **BYPASS** — direct edit plus proportionate verification.
- **LIGHT** — ordinary non-trivial work.
- **FULL** — critical or structural work.

Proceed without ceremonial permission requests. Pause only for destructive/irreversible actions, a real scope change, missing authority, or information only the user can provide.

## Choose track and tier

Use **FULL** when any condition holds:

- Critical surface: aviation, financial, investor-facing, or another explicitly Tier-1 project/surface.
- Structural or high-risk change: database schema/migration/RLS, auth/session, payments/webhooks, secrets/permissions, cross-cutting refactor, or irreversible data operation.
- The user explicitly requests FULL.

Use **LIGHT** for every other non-trivial change. Upgrade from LIGHT to FULL at the current phase if critical/structural scope appears; do not restart completed work.

Tier affects review and release gates, not whether ordinary work receives any verification:

| Tier | Default evidence | Review rule |
|---|---|---|
| 1 — Critical | Preview/E2E when a user flow exists; production audit always | Independent code review plus security/deploy review where relevant; missing independent review blocks merge |
| 2 — Active | Preview/E2E for visual or flow changes | Independent code review before merge |
| 3 — Experimental | Targeted tests; E2E optional | Independent review before merge; self-review is acceptable only for a throwaway spike that will not merge or deploy |

Read an explicit tier from project instructions. If bootstrap/tier metadata is absent, classify named critical surfaces as Tier 1 and everything else as **Tier 2**. Never infer Tier 3 merely because a repo is new.

## LIGHT — four phases

1. **ECHO** — in at most four lines, state the goal, up to three assumptions, and observable done criterion. Continue so the user can correct cheaply.
2. **IMPLEMENT** — work on a branch; inspect existing patterns before adding files or wrappers. For testable behavior, make the relevant test fail before implementation and pass afterward. Do not invent a meaningless test for prose, generated files, or pure formatting.
3. **PROVE** — run targeted local checks. If user-visible, open/update a draft PR, obtain the preview, and test the preview before review. Establish a candidate commit SHA, then obtain independent review against that SHA. A review finding that changes code creates a new candidate SHA and requires affected checks/review again.
4. **FINISH** — update the PR body from the final diff, confirm required checks and review belong to the final candidate SHA, merge through the project’s normal path, and record deviations.

If an independent reviewer is temporarily unavailable, do not relabel self-review as independent. Tier 1 remains blocked; for Tier 2 or merge-bound Tier 3, leave the PR awaiting independent review.

## FULL — 11 steps

### 1. FRAME

Create or select one Beads epic for the user-visible outcome. If `bd` is unavailable, use a checklist section in the plan; Beads is optional, outcome framing is not.

### 2. DESIGN

Inspect existing implementations before proposing a new pattern. Use `codebase-pattern-finder` when available. If multiple defensible designs or unclear domain requirements remain, use a brainstorming skill/process and write a short spec. If the request plus repository evidence determines the design, record it directly and continue.

### 3. PLAN + DOCS

Write independently verifiable milestones with a proof command or observation for each. For every production dependency whose behavior matters, query current docs through the configured docs stack before implementation. Record version-sensitive conclusions in the plan; do not claim current-doc verification when the docs tools are unavailable.

### 4. TASKS

Create one Beads issue per milestone and link real dependencies. If Beads is unavailable, maintain the same dependency order in the plan checklist. Avoid micro-tasks that add tracking without independent verification value.

### 5. ISOLATE

Use a dedicated branch/worktree. Never modify a protected/upstream branch directly. Before introducing a wrapper, helper, module, or abstraction, invoke `everville-reduce-entropy` and compare against existing utilities. Parallel writers require disjoint worktrees; if they must share a resource, load and follow [`references/parallel-agent-locking.md`](references/parallel-agent-locking.md) in full.

### 6. IMPLEMENT

Use test-driven development for testable behavior: observe the relevant test fail for the intended reason, implement the smallest correct change, then observe it pass. Preserve safety, types, observability, and system-boundary validation required by the task. Commit at coherent green milestones.

### 7. PREVIEW + E2E

Run local preflight checks before publishing. For a customer-facing page, dashboard, or user flow:

1. Push the current commit and open/update a draft PR.
2. Generate the PR body with `/explain-pr-changes` when available, or write the same evidence manually.
3. Wait for the preview deployment associated with that commit.
4. Run the project’s E2E suite against the preview URL, using `everville-e2e-discipline:e2e-discipline` when installed or the repository’s existing Playwright convention.

Never claim preview E2E from localhost. Fixes from E2E create a new candidate commit and require a new matching preview.

### 8. REVIEW A STABLE SHA

After preview/E2E changes settle, record the candidate commit SHA and give the spec plus diff for that exact SHA to a fresh-context reviewer. Use `superpowers:requesting-code-review`, built-in `/code-review`, a verifier subagent, or an independent human/platform reviewer, depending on what is available.

Tier 1 additionally needs security and deploy review when those concerns apply. New or modified `SKILL.md` files require `everville-skill-judge` before merge.

Every finding gets one severity:

- **Blocker** — correctness, security, data loss, or spec failure; must fix.
- **Should-fix** — clear bug or missing critical-path test; fix or explicitly defer with owner.
- **Nice-to-have** — worthwhile and non-blocking.
- **Nit** — optional style/taste.

The gate passes with zero blockers and no untriaged should-fix findings. Any code change after review invalidates the stable-SHA claim: create a new candidate SHA and rerun affected verification/review. If publishing GitHub comments manually, de-duplicate them and submit one coherent review; never post a stale-SHA approval.

### 9. VERIFY + PRODUCTION AUDIT

Run actual tests, build, type checks, and project release checks against the candidate SHA. Audit every completion claim against output from the current run.

If deploying to production, invoke `everville-production-audit` for:

- every Tier-1 release; and
- Tier-2 releases touching migrations/RLS, webhooks/jobs, auth, env/secrets, or another production control surface.

A BLOCK verdict stops merge. SHIP-WITH-RISK requires explicit acceptance of the named risk and an owner. Missing optional audit tooling does not make the audit pass: perform the checklist manually and record the fallback; Tier 1 stays blocked if required evidence cannot be produced.

### 10. FINISH

Update the PR body from the final diff. Watch CI with `loop-on-ci` when available, otherwise use the repository’s native checks. Before merge, prove the PR head SHA, preview/E2E evidence, required review, and required checks all correspond to the current local HEAD. Merge through the project’s configured path.

### 11. CLOSE

Close the epic/checklist with a one-line outcome. If the work revealed a reusable Everville lesson, persist it through `everville-lesson-learned` when available or record it in the project’s normal handoff/knowledge surface.

## Optional dependency policy

Named plugins and skills improve consistency but are not silently assumed:

- When a named skill/tool is available, invoke it at the stated phase.
- When it is unavailable, perform the documented equivalent locally and record the fallback in the plan or PR.
- Never report an unavailable tool as invoked or its evidence as produced.
- Do not install plugins or create external resources without user authorization.
- A fallback may preserve process but cannot waive a Tier-1 evidence gate.

Common optional helpers include Superpowers planning/TDD/worktree/review/verification skills, Beads, codebase-pattern-finder, E2E discipline, loop-on-ci, and explain-pr-changes.

## Hard rules

- Keep process proportional: BYPASS, LIGHT, and FULL are distinct outcomes.
- Review the commit that will merge, not an earlier diff.
- A preview-dependent check happens only after a matching preview exists.
- Never substitute narrative confidence for missing evidence.
- Record deviations; do not silently skip required gates.
