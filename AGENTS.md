# everville-workflow — agent context

A **Claude Code plugin marketplace** for the Everville Estate team. Plugins shipped here enforce a consistent development workflow across every Everville project (balicopter, eva.mba, everville-team, etc.).

## What's inside

```
plugins/
  everville-workflow/    11-step unified ritual + trivial-change whitelist
  everville-meta/        plugin authoring helpers (skills, marketplace mgmt)
  everville-handoff/     handoff doc generator for context-window transfers
docs/                    plugin authoring notes
LICENSE / LICENSES       MIT for the marketplace, see plugin.json per plugin
marketplace.json         marketplace manifest consumed by Claude Code
```

Currently shipped versions: `everville-workflow@0.8.0`, `everville-meta@0.2.0`, `everville-handoff@0.3.0`. `everville-copy` retired 2026-07-02 — prose discipline lives in the `humanizer-ru` skill (BRAND/Personal_Brand, desktop skills-plugin).

## Plugin contract (Claude Code)

Each subdirectory under `plugins/` is one plugin and **must** contain:

- `plugin.json` with `name`, `version`, `description`, `components: { skills, commands, agents, hooks }`
- A `skills/` directory with one `SKILL.md` per skill. Frontmatter must specify a clear `description` so Claude's discovery layer can route correctly. The triggering language matters more than the body.
- Optional `commands/`, `agents/`, `hooks/`.

The marketplace itself is registered with `claude plugin marketplace add Everville-Estate/everville-workflow` and individual plugins are installed via `claude plugin install <plugin>@everville-workflow`.

## Versioning

- Plugin `version` is independent per plugin. Bump in the plugin's own `plugin.json`.
- The marketplace `marketplace.json` lists each plugin's current version — update it in the same PR that bumps the plugin.
- After publishing a release, tag the repo `<plugin-name>@vX.Y.Z` so users can pin.

## Skill quality bar

Use `everville-skill-judge` (lives in `everville-workflow` plugin) to evaluate every new SKILL.md before merging. It scores 9 dimensions out of 130 — anything below 80 needs revision. Description quality, trigger language, and concrete examples are the highest-leverage dimensions.

## Authoring conventions

- Skills override default system prompt behavior but **user CLAUDE.md instructions always win** — don't write a skill that contradicts a user instruction.
- Skills are loaded into a fresh subagent's context — keep them tight (under 500 lines unless absolutely needed).
- Don't bundle ceremony (multi-agent reviews, deep brainstorming) into skills meant for trivial changes — see lesson `overengineering`.
- For automated behaviors ("from now on when X"), the right primitive is a **hook** in `settings.json`, not a skill.

## Don't

- Don't add a plugin without an entry in `marketplace.json` — installs will fail silently.
- Don't ship a skill that requires a specific agent runtime (Claude Code, Codex, Hermes) without naming it in the description.
- Don't break backward compat of an installed skill — bump the plugin's major version if you must.

## Lessons that bite here

- `overengineering` — skills should keep the budget proportional to the task. A 7-step ritual for renaming a variable is wrong.
- `magic-mcp-canvas-github` — never enable the canvas+github mode of an MCP that can `git add -A`; secrets leak.
