# everville-workflow - agent context

Claude Code plugin marketplace for the Everville Estate team. The repository ships three independent plugins:

- `plugins/everville-workflow/` - scoped workflow guidance, hooks, CI/release skills, and verification tools.
- `plugins/everville-meta/` - opt-in plugin authoring, instruction refactoring, skill-quality, inventory, and compliance diagnostics.
- `plugins/everville-handoff/` - cross-machine and cross-agent handoffs.

## Source of truth

- Marketplace inventory and versions: `.claude-plugin/marketplace.json`.
- Plugin metadata: `plugins/*/.claude-plugin/plugin.json`.
- Runtime behavior: each plugin's `skills/`, `agents/`, and `hooks/` directories.
- Current operational state: `.codex/handoff.md`.
- Stable repository navigation: `.codex/project-index.md`.
- Historical architecture proposals belong under `docs/archive/`; do not treat them as current behavior.

## Canonical verification

Run the unit suite, `scripts/validate_repository.py`, strict marketplace/per-plugin validation, and `scripts/validate_marketplace_install.sh`. Hook and harness behavior must have deterministic tests; ad-hoc session evidence is not a substitute.

## Authoring rules

- Keep plugin versions synchronized between the marketplace and plugin manifest.
- Bump the affected plugin version for every published behavior change.
- Keep skills concise and move large supporting material into explicitly routed references.
- Plugin-root `CLAUDE.md` is not runtime context. Ship behavior through skills, agents, hooks, or supported settings.
- Use current Claude Code event names and schemas; validate against first-party documentation.
- Skills with external side effects must make that boundary explicit and require deliberate invocation or authorization.
- Preserve third-party attribution and license files.

## Execution

- Keep simple work local. Use a concise plan for multi-stage changes.
- Use bounded subagents only when independent parallel work materially helps; give writers separate worktrees or non-overlapping files.
- A subagent return is evidence, not acceptance. Review its diff and verification before integration.
- Keep `.codex/handoff.md` current when work must survive the session. Do not create parallel stage ledgers or orchestration artifacts.
- No silent technical debt. Record a concrete owner and next action for every defer.

## Delivery boundaries

- Work on a feature branch; do not push directly to `main`.
- A pull request and independent review are required for release changes.
- Do not push, merge, publish a release, or alter repository protection without explicit user authorization.
