# everville-workflow - agent context

Claude Code plugin marketplace for the Everville Estate team. The repository ships three independent plugins:

- `plugins/everville-workflow/` - scoped workflow guidance, hooks, CI/release skills, and verification tools.
- `plugins/everville-meta/` - opt-in plugin authoring, instruction refactoring, skill-quality, inventory, and compliance diagnostics.
- `plugins/everville-handoff/` - cross-machine and cross-agent handoffs.

## Source of truth

- Marketplace inventory and versions: `.claude-plugin/marketplace.json`.
- Plugin metadata: `plugins/*/.claude-plugin/plugin.json`.
- Runtime behavior: each plugin's `skills/`, `agents/`, `commands/`, and `hooks/` directories.
- Current operational state: `.codex/handoff.md`.
- Stable repository navigation: `.codex/project-index.md`.
- Historical architecture proposals belong under `docs/archive/`; do not treat them as current behavior.

## Canonical verification

Run `scripts/validate_repository.py`, the strict marketplace/per-plugin validation commands, and `scripts/validate_marketplace_install.sh` as documented in `.codex/orchestrator.toml`. Hook and harness behavior must have deterministic tests; ad-hoc session evidence is not a substitute.

## Authoring rules

- Keep plugin versions synchronized between the marketplace and plugin manifest.
- Bump the affected plugin version for every published behavior change.
- Keep skills concise and move large supporting material into explicitly routed references.
- Plugin-root `CLAUDE.md` is not runtime context. Ship behavior through skills, agents, hooks, or supported settings.
- Use current Claude Code event names and schemas; validate against first-party documentation.
- Skills with external side effects must make that boundary explicit and require deliberate invocation or authorization.
- Preserve third-party attribution and license files.

## Orchestration

- Simple work stays local. Medium/complex work uses `orchestrator-stage` and `task-router`.
- Create/select a Beads task before delegated or long-running file changes when Beads is available; otherwise record the missing tool and use the active Codex goal plus `.codex/handoff.md`.
- Medium/complex work starts with a Parallel Decomposition Matrix.
- Authorized delegated streams use separate spawned Codex agents and isolated worktrees; inline summaries are not a substitute.
- Subagents inherit model/reasoning by default. Record the rationale for any override.
- Every delegated prompt includes Documentation and Asset Routing blocks, a bounded write zone, success criteria, verification, and stop rules.
- A subagent return is not acceptance. Review its diff and verification before integration.
- No silent technical debt. Any defer must be bounded, tracked, and listed in `.codex/handoff.md`.

## Delivery boundaries

- Work on a feature branch; do not push directly to `main`.
- A pull request and independent review are required for release changes.
- Do not push, merge, publish a release, or alter repository protection without explicit user authorization.
