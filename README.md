# Everville Workflow

Claude Code plugins used by the Everville Estate team. The marketplace currently ships three independent plugins:

| Plugin | What it provides | Side effects |
| --- | --- | --- |
| `everville-workflow` | BYPASS/LIGHT/FULL routing, proportional hardening of approved multi-component specifications, production and CI guidance, two agents, an explicit PR-summary skill, and repository-scoped context | A fast `SessionStart` hook identifies a verified Everville repository and adds concise factual routing context. It never intercepts tools or makes permission decisions. Some skills call `git` or `gh` when invoked. |
| `everville-handoff` | Create and resume portable cross-machine or cross-agent checkpoints | Writes under `.claude/handoffs/` only when the skill is used. It never commits or pushes a handoff automatically. |
| `everville-meta` | Marketplace authoring, instruction refactoring, skill judging/stocktaking, and the runtime skill-invocation harness | May scaffold or modify plugin files when explicitly used. The compliance harness can run bounded `claude -p` experiments only after an explicit non-dry-run invocation. Publishing remains a separate, reviewed Git operation. |

See [the current architecture](docs/architecture.md) for component and trust boundaries. The original April design is preserved as a [historical proposal](docs/archive/architecture-2026-04-proposal.md).

## Workflow model

`everville-workflow` has three outcomes:

- **BYPASS**: a narrow hard-list skip such as a typo-only change. Use proportionate verification without invoking the workflow track.
- **LIGHT**: the normal non-trivial path: echo assumptions, implement with tests, obtain independent verification, then ship with evidence.
- **FULL**: the 11-step path for tier-1, structural, migration, auth, financial, aviation, or otherwise high-risk changes.

The hook is context, not a security boundary. It does not intercept tools, prove that a skill ran, or replace review, permissions, branch protection, CI, or repository policy. Scope installation deliberately.

`everville-spec-hardening` is intentionally narrower than the general workflow. It applies to an existing implementation-bound specification that crosses components or critical operational boundaries, or when explicitly requested. It does not turn brainstorming, routine changes, code review, or prose cleanup into a heavyweight specification process.

## Requirements and optional tools

Required for the workflow plugin:

- Claude Code with plugin support
- `git`
- `python3` for the shipped hook

Recommended for the intended FULL workflow:

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

Optional capabilities:

- `gh`, authenticated to GitHub, for CI/PR inspection skills
- Beads (`bd`); without it, the workflow uses a plan checklist
- `neuledge-context`, with Context7 as fallback, for current library documentation
- Playwright or the repository's existing E2E runner for user-facing changes
- `everville-meta` for maintainers who need instruction refactoring, skill-quality audits, or the standard-library-only compliance harness

## Install

Add the marketplace once:

```bash
claude plugin marketplace add Everville-Estate/everville-workflow
```

Install only what the project needs:

```bash
claude plugin install everville-workflow@everville-workflow --scope project
claude plugin install everville-handoff@everville-workflow --scope user
claude plugin install everville-meta@everville-workflow --scope local
```

Scopes matter:

- `project` writes shared project configuration and is the recommended scope for the workflow in Everville repositories.
- `local` is project-specific and gitignored; it is useful for maintainer-only tooling such as `everville-meta`.
- `user` is the CLI default and enables a plugin across projects. It is appropriate for the explicit-only handoff skill when cross-project availability is intentional; do not use it for the workflow or maintainer plugin.
- `managed` is controlled by organization policy and cannot be selected by ordinary installs.

Installing `everville-workflow` at user scope makes its hooks available in every project session. The hook implementation checks repository identity before applying Everville behavior, but project scope remains the required operational boundary. Non-Everville repositories must not enable it. See [deployment scope](docs/deployment-scope.md).

## Verify

```bash
claude plugin list
claude plugin details everville-workflow@everville-workflow
claude plugin validate . --strict
claude plugin validate plugins/everville-workflow --strict
claude plugin validate plugins/everville-meta --strict
claude plugin validate plugins/everville-handoff --strict
scripts/validate_marketplace_install.sh
```

Run `/hooks` inside Claude Code to inspect loaded hook events and their source. After changing or updating hooks, agents, MCP servers, or other plugin components, run `/reload-plugins` or restart Claude Code. A marketplace install runs from Claude Code's plugin cache, not this checkout.

## Update

```bash
claude plugin marketplace update everville-workflow
claude plugin update everville-workflow@everville-workflow --scope project
claude plugin update everville-handoff@everville-workflow --scope user
claude plugin update everville-meta@everville-workflow --scope local
```

Restart Claude Code after an installed plugin update. Mid-session hook and server processes may continue using the previous cached version until reload or restart.

## Disable or uninstall

Disable temporarily:

```bash
claude plugin disable everville-workflow@everville-workflow
```

Uninstall from the same scope used for installation:

```bash
claude plugin uninstall everville-workflow@everville-workflow --scope project
claude plugin uninstall everville-handoff@everville-workflow --scope user
claude plugin uninstall everville-meta@everville-workflow --scope local
```

Use `--keep-data` when uninstalling if a plugin's persistent data should remain. Uninstalling a plugin does not delete repository files that a skill previously created.

## Maintainers

@nikoasta, @pakvovan, @dev-eva-mba

## License

MIT © Everville Estate PTE LTD. Third-party adaptations retain their attribution under `LICENSES/`.
