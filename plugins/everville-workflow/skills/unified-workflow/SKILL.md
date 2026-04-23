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
Invoke `superpowers:brainstorming`. Output: a written spec in `docs/superpowers/specs/YYYY-MM-DD-<topic>.md`, committed. Skip only if the change is a re-run of an already-specced pattern.

### 3. PLAN — Break into tasks
Invoke `superpowers:writing-plans`. Output: a plan in `docs/superpowers/plans/YYYY-MM-DD-<topic>.md` with bite-sized TDD steps. Each task should be 2-5 minutes of work.

### 3.5. CONTEXT7 PREFETCH — Pin live docs
For every production dependency touched by the plan, resolve via `mcp__context7__resolve-library-id` and persist the library ID to `.beads/context7-libs.json`. Never ship code against library assumptions from memory — always query fresh docs.

### 4. SUB-TASKS — File in Beads
`bd create` one issue per plan task. Link dependencies with `bd dep add`:
- `blocks` / `blocked-by` — strict ordering
- `parent` / `child` — hierarchy
- `discovered-from` — scope creep from parent
- `related` — soft links

### 5. ISOLATE — Worktree
Invoke `superpowers:using-git-worktrees`. Create an isolated worktree per epic. Never modify upstream branches directly.

### 6. IMPLEMENT — TDD with discipline
Invoke `superpowers:test-driven-development`. For every unit of logic: write failing test → run to confirm RED → write minimum code → run to confirm GREEN → refactor → commit.

### 7. E2E — User-visible regression gate
If the change touches `app/(marketing)/`, dashboards, or any customer-facing flow: invoke `everville-e2e-discipline:e2e-discipline` (when installed) or write Playwright specs following the project's existing conventions. Run against preview deploy URL, not localhost.

### 8. REVIEW — Multi-agent quality pass
Invoke `superpowers:requesting-code-review`. For tier-1 projects (balicopter, aviation/financial), also dispatch `security-auditor` and `deploy-checker` in parallel.

### 9. VERIFY — Prove it works
Invoke `superpowers:verification-before-completion`. Run the actual commands (tests, builds, deploy-check) and paste output. Never claim done without verification.

### 10. FINISH — Integrate
Invoke `superpowers:finishing-a-development-branch`. Merge path depends on project (PR review, direct merge, squash).

### 11. CLOSE — Record
`bd close <epic-id> --reason "<one-line outcome>"`. This triggers the memory-bridge hook (when `everville-bootstrap` is installed) which appends the closure to the project's memory file.

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

If you catch yourself skipping steps to ship faster, stop and ask. The ritual exists because shortcuts have burned the team before. Err on the side of asking.
