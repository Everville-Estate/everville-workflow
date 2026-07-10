---
name: everville-plugin-forge
description: Create and maintain Claude Code plugins in the everville-workflow marketplace. Use for scaffolding components, choosing safe skill invocation controls, auditing dependencies and side effects, synchronizing versions, validating manifests, or preparing a reviewed release branch.
---

<!--
  Adapted from softaworks/agent-toolkit (plugin-forge) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: marketplace-specific layout, current Claude Code
  component contracts, side-effect controls, and reviewed release workflow.
-->

# Everville Plugin Forge

Build and maintain plugins in `Everville-Estate/everville-workflow` without relying on undocumented loading behavior.

## Runtime contract

- Plugin components live at the plugin root: `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, and optional manifest-declared component paths.
- `.claude-plugin/plugin.json` contains metadata; component directories are its siblings, never children of `.claude-plugin/`.
- A plugin-root `CLAUDE.md` is **not** loaded because the plugin is enabled. Put runtime guidance in a skill, hook context, agent, command, or in the consuming project's `CLAUDE.md`/`.claude/rules`.
- Hook event names are case-sensitive Claude Code lifecycle names, including `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionEnd`, and `PreCompact`.
- Use `${CLAUDE_PLUGIN_ROOT}` for bundled read-only files and `${CLAUDE_PLUGIN_DATA}` for state or dependencies that must survive plugin updates. Marketplace cache directories are versioned and ephemeral.

## Before creating anything

1. Search shipped, project, and installed skills with `rg`, then check Everville knowledge and sibling marketplaces.
2. Read any external candidate completely, including scripts, hooks, tool permissions, network calls, credential access, and license.
3. Prefer extending or composing an existing skill. Use `everville-skill-stocktake` when overlap is unclear.
4. Define the component's inputs, outputs, dependencies, side effects, and failure behavior before scaffolding.

## Scaffold

Create a marketplace plugin under `plugins/`; `claude plugin init` instead creates a skills-directory plugin under the user's Claude configuration and is not the default workflow for this repository.

```bash
NAME=my-plugin
mkdir -p "plugins/$NAME/.claude-plugin" "plugins/$NAME/skills"
```

Create `plugins/$NAME/.claude-plugin/plugin.json` with at least a stable kebab-case `name`, and normally `version`, `description`, author, repository, license, and keywords. Register the relative source in `.claude-plugin/marketplace.json`.

Do not add `CLAUDE.md` as a runtime mechanism. A human changelog may live at `CHANGELOG.md`; plugin-specific operating guidance belongs in a component that Claude Code actually loads.

## Choose invocation and side-effect boundaries

For every skill or command, classify it:

- **Reference/procedure with no material side effect:** model invocation may remain enabled.
- **Commit, deploy, publish, send, delete, create PR, mutate remote state, or other timing-sensitive action:** add `disable-model-invocation: true`. The user must invoke it explicitly.
- **Background knowledge not meaningful as a slash command:** use `user-invocable: false`.

Even explicitly invoked skills must distinguish preparation from publication. Generate an artifact first, show the proposed mutation, and require explicit authorization for external writes unless the user's invocation unambiguously requested that exact action.

Declare:

- required executables, runtimes, packages, environment variable **names**, and supported platforms;
- files/directories written and whether they persist across updates;
- network services and authentication scopes used;
- cleanup and rollback behavior;
- whether absence of a dependency is a hard failure or has a documented fallback.

Never print secret values. Never install dependencies into `${CLAUDE_PLUGIN_ROOT}` at runtime; use `${CLAUDE_PLUGIN_DATA}` when persistent installation is genuinely required.

## Component summary

| Component | Default location | Important contract |
| --- | --- | --- |
| Skill | `skills/<directory>/SKILL.md` | Frontmatter starts at byte 1; directory controls command name; body loads when invoked |
| Command | `commands/<name>.md` | Legacy flat skill format; use skill frontmatter controls for side effects |
| Agent | `agents/<name>.md` | Declare model/tools deliberately; plugin agents cannot ship permission mode or MCP servers |
| Hook | `hooks/hooks.json` | Exact event and matcher names; use exec form or quote path placeholders |
| MCP | `.mcp.json` | Declare server, args, env names, and dependency lifecycle |

See `references/plugin-structure.md` for supported paths and `references/marketplace-schema.md` for catalog entries.

## Validate

Run first-party validation from the marketplace root:

```bash
claude plugin validate . --strict
claude plugin validate "plugins/$NAME" --strict
```

Exact semantics:

- `claude plugin validate <path>` validates the plugin or marketplace manifest and reports unrecognized fields as warnings.
- Warnings do not prevent normal validation or loading. `--strict` turns warnings into failures and is the release/CI mode.
- Wrong field types and structurally invalid manifests fail validation.
- Validation does not prove scripts work, dependencies exist, hooks behave safely, every referenced path is portable, or every skill's behavior matches its prose. Test those separately.

Also run repository tests, parse every changed frontmatter block, exercise hook fixtures, and use `git diff --check`. PyYAML may be used for local linting only if declared as a development dependency; do not make an undeclared package a hidden release prerequisite.

## Version and test locally

Keep versions synchronized between:

1. `plugins/<name>/.claude-plugin/plugin.json`
2. the matching entry in `.claude-plugin/marketplace.json`

Use semantic versioning: breaking contract change = major, new capability = minor, compatible fix/docs = patch.

Marketplace installs run from Claude Code's cache. After a released version is available:

```bash
claude plugin marketplace update everville-workflow
claude plugin update <plugin-name>@everville-workflow --scope <user|project|local>
```

Restart is required after `plugin update`. For in-place skills-directory plugins, `SKILL.md` edits can be detected live, while hooks, agents, MCP/LSP components, and other non-skill changes require `/reload-plugins` or restart. A marketplace cache is not a development write target; test an unpublished checkout with a local marketplace or a temporary `--plugin-dir` session.

## Release through review

1. Work on a dedicated branch.
2. Preserve attribution and licenses for adapted work.
3. Update both version declarations and release notes when appropriate.
4. Run strict manifest validation and behavioral tests.
5. Review the diff for new dependencies, permissions, hooks, network calls, persistent writes, and secrets.
6. Commit intentionally and open a pull request only when authorized.
7. Obtain required independent review and CI evidence before merge.

Never push directly to `main`. This skill prepares changes; it does not grant authority to push, merge, publish, update a marketplace, or mutate a remote repository.

## References

- `references/plugin-structure.md` — component layout and loading rules
- `references/marketplace-schema.md` — marketplace entry shape and scopes
- `references/workflows.md` — reviewed create, test, update, and release flow
