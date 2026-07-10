# everville-workflow changelog

This file is release history for maintainers. It is not loaded as plugin instructions. Runtime behavior comes from the plugin's skills, commands, agents, and hooks.

## Unreleased remediation

- Scope workflow hook context and gate behavior to verified Everville repositories.
- Treat the edit gate as an advisory workflow guardrail, not a security or compliance boundary.
- Expand the matched mutation surface to `Edit|Write|NotebookEdit|Bash`, while documenting that external processes and unmatched tools remain outside the guarantee.
- Resolve the actual Git root, anchor bookkeeping exemptions, isolate markers by repository/session, and fail open on internal hook errors.
- Make `/explain-pr-changes` an explicitly invoked, generation-only command. Creating branches, pushing, and creating/editing PRs require a separate authorized action.
- Correct CLAUDE.md refactoring guidance to use `@imports` or path-scoped `.claude/rules`.
- Replace machine-path handoff identity with sanitized repository/commit identity and fail-closed validation.
- Remove the obsolete plugin-root `CLAUDE.md` runtime claim.

## 0.11.4

- Changed the workflow gate to a one-time per-session speed bump.

## 0.11.0

- Added `loop-on-ci` and the background `ci-watcher` agent, adapted from cursor-team-kit with attribution retained under `LICENSES/cursor-MIT.txt`.

## 0.10.0

- Added the initial `PreToolUse` edit gate for Everville repositories.

## 0.9.0

- Introduced the LIGHT/FULL workflow split and SessionStart workflow context.
- Added stocktake-driven fixes to lesson persistence, compliance paths, handoff staleness, and docs routing.
- Retired `/review-post` and `/review-self`; consolidated reviewer-oriented output in `/explain-pr-changes`.

## 0.8.0

- Added the skill compliance harness and seed scenarios.

## 0.7.0

- Added skill stocktake and parallel-agent locking guidance.

## 0.6.0

- Added the production readiness audit.

## 0.5.0

- Added review severity vocabulary and PR review-posting guidance (later retired/consolidated).

## 0.4.0

- Recalibrated workflow guidance to be model-agnostic.

## 0.3.0

- Replaced micro-task prescription with milestone-level plans and evidence-grounded verification.

## 0.2.0

- Added adapted skill-judge, entropy, agent-instruction refactor, lesson, pattern-finder, and PR explanation components. Attribution is retained under `LICENSES/softaworks-MIT.txt`.

## 0.1.x

- Initial unified workflow and trivial whitelist release, followed by an installation documentation correction.
