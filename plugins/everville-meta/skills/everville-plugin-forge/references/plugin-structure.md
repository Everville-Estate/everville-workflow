# Plugin structure reference

## Default layout

```text
plugin-name/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── skill-name/
│       ├── SKILL.md
│       ├── references/
│       ├── scripts/
│       └── assets/
├── commands/
│   └── legacy-command.md
├── agents/
│   └── reviewer.md
├── hooks/
│   └── hooks.json
├── .mcp.json
└── CHANGELOG.md
```

Only `name` is required in `plugin.json`. Normal metadata includes `version`, `description`, `author`, `homepage`, `repository`, `license`, and `keywords`. Custom component path fields must be relative to the plugin root and begin with `./`.

Do not put components inside `.claude-plugin/`. Do not use a root `CLAUDE.md` as plugin runtime instructions; enabling a plugin does not load it.

## Skills and commands

A skill lives at `skills/<command-name>/SKILL.md`. The directory controls its plugin-scoped command name. Frontmatter may include `description`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `context`, `agent`, `paths`, and scoped `hooks`.

Use `disable-model-invocation: true` for side-effectful or timing-sensitive workflows such as publish, deploy, commit, send, destructive cleanup, remote mutation, or PR creation. A command file under `commands/` is the legacy flat skill format and should follow the same invocation-safety rule.

Skill bodies remain in conversation context after invocation. Keep the main body concise and place detailed material in `references/` for on-demand reading.

## Hooks

Default path: `hooks/hooks.json`. Event names are case-sensitive. Common events include:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `PostToolUseFailure`
- `Stop`
- `SubagentStop`
- `SessionEnd`
- `PreCompact` / `PostCompact`

Use `${CLAUDE_PLUGIN_ROOT}` for bundled files, `${CLAUDE_PLUGIN_DATA}` for persistent state, and `${CLAUDE_PROJECT_DIR}` for the active project. Prefer exec-form hook commands where supported so paths are passed without shell tokenization.

`PreToolUse` can block a matched call before it runs. `PostToolUse` cannot undo a completed call. `SessionStart` adds context but cannot block session startup.

## State and dependencies

Marketplace installs are copied into a versioned cache. Treat `${CLAUDE_PLUGIN_ROOT}` as read-only and ephemeral. Store durable plugin-owned state or installed runtime dependencies under `${CLAUDE_PLUGIN_DATA}`. Document executable/package prerequisites and fail clearly when they are unavailable.

## Validation boundary

`claude plugin validate <path> --strict` validates manifest schema and makes warnings fatal. It does not execute hooks, parse application semantics, install packages, exercise network calls, or prove side-effect safety. Add component-specific tests for those claims.
