---
name: unified-workflow
description: Use when starting any non-trivial change in an Everville team project (feature, bugfix, refactor, migration). Enforces the 11-step ritual — epic, brainstorm, plan, context7, sub-tasks, isolate, implement, e2e, review, verify, finish, close. Consult trivial-whitelist skill first to decide whether the full ritual applies.
---

# Unified Workflow — 11-Step Development Ritual

Use this skill at the start of any non-trivial change on an Everville project. For one-line typo fixes, dependency bumps, or doc-only edits, check the `trivial-whitelist` skill first — those skip the ritual.

## The 11 Steps

### 1. EPIC — Frame the work
Create or pick a Beads epic (`bd create --type epic`). One epic = one deliverable outcome the user can see. If the task doesn't map to an existing or new epic, stop and ask.

### 2. BRAINSTORM — Design before code
Dispatch the `codebase-pattern-finder` agent to surface existing implementations (Next.js routes, Drizzle schemas, shadcn primitives, server actions) you can model after. If the requirements are genuinely ambiguous — multiple defensible designs, unclear user intent, new domain — invoke `superpowers:brainstorming` and commit a written spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>.md`. If the design is already clear from the request plus existing patterns, write the spec directly and move on; when you have enough information to act, act.

### 3. PLAN — Break into milestones
Invoke `superpowers:writing-plans`. Output: a plan in `docs/superpowers/plans/YYYY-MM-DD-<topic>.md`. Plan at the level of independently verifiable milestones (a migration that applies cleanly, an endpoint with passing tests, a page that renders), not micro-tasks — each milestone should have a stated check that proves it done.

### 3.5. CONTEXT7 PREFETCH — Pin live docs
For every production dependency touched by the plan, resolve via `mcp__context7__resolve-library-id` and persist the library ID to `.beads/context7-libs.json`. Never ship code against library assumptions from memory — always query fresh docs.

### 4. SUB-TASKS — File in Beads
`bd create` one issue per plan task. Link dependencies with `bd dep add`:
- `blocks` / `blocked-by` — strict ordering
- `parent` / `child` — hierarchy
- `discovered-from` — scope creep from parent
- `related` — soft links

### 5. ISOLATE — Worktree
Invoke `superpowers:using-git-worktrees`. Create an isolated worktree per epic. Never modify upstream branches directly. Before adding any new file, module, or wrapper during implementation, invoke `everville-reduce-entropy` to check whether an existing utility already covers it.

### 6. IMPLEMENT — TDD with discipline
Invoke `superpowers:test-driven-development`. Tests for a behavior exist and fail before the implementation makes them pass — that invariant is non-negotiable; the per-line choreography is not. Work at whatever unit size keeps the tests honest, and commit at each green milestone. Don't add features, abstractions, or error handling beyond what the task requires; only validate at system boundaries.

### 7. E2E — User-visible regression gate
If the change touches `app/(marketing)/`, dashboards, or any customer-facing flow: invoke `everville-e2e-discipline:e2e-discipline` (when installed) or write Playwright specs following the project's existing conventions. Run against preview deploy URL, not localhost.

### 8. REVIEW — Fresh-context verification
Dispatch a fresh-context verifier subagent that reads the spec and the diff cold and reports whether the diff satisfies the spec — separate verifiers outperform self-critique, so this is the primary gate. Dispatch reviewers in parallel and keep working while they run: `superpowers:requesting-code-review` for all tiers; `security-auditor` and `deploy-checker` additionally for tier-1 projects (balicopter, aviation/financial). `/review-self` remains available as an optional pre-pass for organizing a large diff before review. If the change introduces a new skill or SKILL.md, invoke `everville-skill-judge` as a gate before merge.

Every finding — from the verifier or any reviewer — carries one severity label so triage is consistent:
- 🔴 **Blocker** — must fix before merge (correctness, security, data loss, breaks the spec)
- 🟠 **Should-fix** — fix before merge unless explicitly deferred (clear bug, missing test on a critical path)
- 🟡 **Nice-to-have** — worth doing, non-blocking (clarity, minor edge case)
- 🔵 **Nit** — taste or style, optional

The gate passes when zero 🔴 and no un-triaged 🟠 remain. To land these findings on the GitHub PR as one formal review (atomic, de-duped against existing comments), run `/review-post`.

### 9. VERIFY — Prove it works
Invoke `superpowers:verification-before-completion`. Run the actual commands (tests, builds, deploy-check). Before reporting progress, audit each claim against a tool result from this session — only report work you can point to evidence for; if something is not yet verified, say so explicitly. If tests fail, say so with the output; if a step was skipped, say that.

### 9.5. PRODUCTION AUDIT — Release-surface gate
If this change will deploy to production, invoke `everville-production-audit` before finishing. VERIFY proves the diff works; this proves the *release surface* is safe (RLS, migration rollback, webhook/job idempotency, env fail-fast, secrets). Tier-1 (balicopter/financial/investor-facing): always. Tier-2: when the change touches a prod surface (migrations, webhooks, auth, env). A BLOCK verdict stops the merge; SHIP-WITH-RISK requires the named risk to be accepted by the user with an owner.

### 10. FINISH — Integrate
Invoke `superpowers:finishing-a-development-branch`. For any PR against an Everville repo, run `/explain-pr-changes` to generate or update the PR body from the diff. Merge path depends on project (PR review, direct merge, squash).

### 11. CLOSE — Record
`bd close <epic-id> --reason "<one-line outcome>"`. This triggers the memory-bridge hook (when `everville-bootstrap` is installed) which appends the closure to the project's memory file. If the work exposed a pattern worth propagating across Everville repos (regression caught, gotcha found, surprising constraint), invoke `everville-lesson-learned` and persist the lesson as an auto-memory `feedback_*.md` entry.

## Required upstream skills

This workflow assumes you have the following skills installed (via `superpowers` plugin):
- `superpowers:brainstorming`
- `superpowers:writing-plans`
- `superpowers:test-driven-development`
- `superpowers:using-git-worktrees`
- `superpowers:requesting-code-review`
- `superpowers:verification-before-completion`
- `superpowers:finishing-a-development-branch`

Install with:
```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

## When to skip steps

Steps 7 (E2E) and 8 (review) are gated by tier:

| Tier | E2E required | Extra reviewers |
|------|-------------|-----------------|
| 1 — Critical (aviation, financial, prod user-facing) | Yes | security-auditor, deploy-checker |
| 2 — Active (internal tools, admin UIs) | If visual/flow changes | code-reviewer only |
| 3 — Experimental (prototypes, spikes) | No | Self-review OK |

Projects declare tier in their `./CLAUDE.md` (set by `/bootstrap-project` when `everville-bootstrap` is installed).

## Hard rule

Don't silently skip steps to ship faster — the ritual exists because shortcuts have burned the team before. But don't over-correct into asking permission for everything either: pause for the user when the work genuinely requires it — a destructive or irreversible action, a real scope change, or input only they can provide — and otherwise use your judgment and proceed, noting any deviation from a step in the PR body.
