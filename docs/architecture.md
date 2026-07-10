# Current architecture

This document describes the marketplace as shipped. It replaces the April 2026 proposal, which is retained under `docs/archive/` for historical context only.

## Distribution

The repository root is a Claude Code marketplace. `.claude-plugin/marketplace.json` registers three plugins whose source directories live under `plugins/`. Each plugin has its own `.claude-plugin/plugin.json` and can be installed independently.

Marketplace installs are copied into Claude Code's plugin cache. Editing this checkout does not mutate an already installed copy. Update the marketplace and plugin, then reload plugins or restart Claude Code to exercise a released version.

## Components

### `everville-workflow`

- Skills implement BYPASS/LIGHT/FULL routing, entropy control, lessons, production auditing, and CI procedures.
- Agents provide read-only pattern discovery and background CI observation.
- `/everville-workflow:explain-pr-changes` generates review-ready PR Markdown. It does not publish or mutate GitHub state.
- `SessionStart` supplies conditional workflow context.
- `PreToolUse` can block matched tool calls before execution.

The hook layer is advisory/deterministic only at its exact event and matcher boundary. It is not proof that the prescribed review happened and is not a substitute for OS permissions, protected branches, required reviews, or CI.

### `everville-handoff`

The handoff skill writes a repository-local, portable checkpoint under `.claude/handoffs/`. Repository identity is based on the Git remote and commit, not a developer's absolute checkout path. Handoffs are local by default; committing or sharing one requires an explicit decision after secret and reference validation.

### `everville-meta`

The plugin-forge skill documents and maintains this marketplace. Instruction refactoring and the skill judge/stocktake/comply tools live here so ordinary workflow users do not pay their discovery cost. These tools can scaffold, validate, or run bounded diagnostics, but release operations remain normal reviewed Git work. The plugin does not gain runtime instructions from a `CLAUDE.md` placed at its root.

## Context and loading

Claude Code loads plugin skills, commands, agents, and hooks from their documented component locations. Plugin-root `CLAUDE.md` is not a plugin component and is not loaded merely because a plugin is enabled.

Project instructions belong in the consuming repository's `CLAUDE.md` or `.claude/CLAUDE.md`. `@path` imports are expanded at session start and therefore cost context tokens even if a task never needs them. Topic rules under `.claude/rules/` may use `paths` frontmatter so they load only when matching files are read. Multi-step procedures belong in skills, whose full bodies load only when invoked.

## External dependencies

The core runtime assumes Claude Code, Git, and Python 3. The FULL workflow references the separately installed Superpowers plugin. `gh`, Beads, docs MCPs, and Playwright unlock specific optional paths. The compliance harness uses only the Python standard library. Missing optional tools must be reported or handled through the fallbacks documented by each skill; absence must not be silently presented as successful execution.

## Release contract

1. Change components on a branch; do not push directly to `main`.
2. Preserve third-party attribution and licenses.
3. Bump the plugin version in both `plugin.json` and its marketplace entry.
4. Run strict validation for the marketplace and every affected plugin, plus project tests.
5. Open a pull request and obtain the repository's required review/CI evidence.
6. After merge, update the marketplace and installed plugin, then reload or restart before verification.
