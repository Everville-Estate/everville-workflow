# everville-workflow — Plugin Rules

When this plugin is enabled, Claude Code must consult the `unified-workflow` skill at the start of any non-trivial task. Use the `trivial-whitelist` skill to decide whether a change is trivial.

## Skills in this plugin

- `unified-workflow` — 11-step development ritual (see `skills/unified-workflow/SKILL.md`)
- `trivial-whitelist` — hard list of ritual-skip change types (see `skills/trivial-whitelist/SKILL.md`)

## Install prerequisites

This plugin's `unified-workflow` skill references several `superpowers:*` skills. Users must install `superpowers` separately:

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

## Plugin versioning

- 0.1.0 — Initial release: unified-workflow + trivial-whitelist skills (Phase 0)
- 0.2.0 — Planned: `/workflow-status` command (Plan 2)

## Maintainers

@nikoasta, @balicopter, @maslennikov-ig
