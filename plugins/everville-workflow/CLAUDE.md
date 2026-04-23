# everville-workflow — Plugin Rules

When this plugin is enabled, Claude Code must consult the `unified-workflow` skill at the start of any non-trivial task. Use the `trivial-whitelist` skill to decide whether a change is trivial.

## Skills in this plugin

- `unified-workflow` — 11-step development ritual (see `skills/unified-workflow/SKILL.md`)
- `trivial-whitelist` — hard list of ritual-skip change types (see `skills/trivial-whitelist/SKILL.md`)
- `everville-skill-judge` — 130-point rubric for accepting new skills (adapted from softaworks, adds D9 Everville Fit)
- `everville-reduce-entropy` — bias toward deletion; invoked during ISOLATE step
- `everville-agent-md-refactor` — split bloated repo CLAUDE.md files via progressive disclosure
- `everville-lesson-learned` — extract SE lessons from diffs; optional auto-memory feedback persistence

## Agents in this plugin

- `codebase-pattern-finder` — read-only Sonnet agent for BRAINSTORM step; surfaces existing Next.js/Supabase/Drizzle/shadcn patterns before new design

## Commands in this plugin

- `/explain-pr-changes` — generate PR body from diff; creates or updates PR
- `/review-self` — self-review diff as mental model before requesting code review

## Install prerequisites

This plugin's `unified-workflow` skill references several `superpowers:*` skills. Users must install `superpowers` separately:

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

## Plugin versioning

- 0.1.0 — Initial release: unified-workflow + trivial-whitelist skills (Phase 0)
- 0.1.1 — Doc fix: remove invalid `github:` prefix from marketplace add commands
- 0.2.0 — Adopted 7 items from softaworks/agent-toolkit (MIT): everville-skill-judge (with 9th dimension "Everville Fit"), everville-reduce-entropy, everville-agent-md-refactor, everville-lesson-learned, codebase-pattern-finder agent, /explain-pr-changes, /review-self. Attribution in `LICENSES/softaworks-MIT.txt`.

## Maintainers

@nikoasta, @balicopter, @maslennikov-ig
