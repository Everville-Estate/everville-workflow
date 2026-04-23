---
name: trivial-whitelist
description: Use before starting any change to decide whether the unified-workflow 11-step ritual is required. Returns a clear verdict — trivial (skip ritual) or non-trivial (full ritual). Hard list; no fuzzy judgment.
---

# Trivial Whitelist — Ritual Bypass Rules

Consult this skill before any change. If the change matches an item on the whitelist below, skip the `unified-workflow` ritual and make the edit directly. Otherwise, follow the full 11 steps.

## Whitelisted change types (skip ritual)

1. **Typo / comment-only fixes** — no executable code change.
2. **Formatting-only** — output of `prettier --write`, `eslint --fix`, `gofmt`, `rustfmt`, etc. No logic change.
3. **Dependency version bumps without API change** — patch/minor bumps where changelog confirms no breaking API. Major bumps always require the ritual.
4. **Doc-only edits** — any file under `docs/**` or ending in `.md`, except `CLAUDE.md` which governs AI behavior (treat as code).
5. **README badge updates** — status badges, shields.io URLs, coverage percent.
6. **`.gitignore` / `.vercelignore` / `.dockerignore` additions** — new ignore patterns. Removals require the ritual.
7. **Lockfile regeneration** — `npm install` / `yarn` / `pnpm` / `uv lock` outputs, committed alone.

## Not trivial (always run full ritual)

Anything involving:
- Business logic, algorithms, data transformations
- Database schema / migrations / RLS policies
- API routes / server actions / edge functions
- UI components (even "small" tweaks — user-visible = ritual)
- Auth flows / session handling / cookies
- Config files that affect runtime (`next.config.js`, `vercel.json`, `.env.example`, etc.)
- `CLAUDE.md` at any level
- Hooks in `.claude/settings.json`
- Anything the user explicitly flagged as critical (e.g., balicopter aviation code)

## Usage pattern

```
User: "fix typo in README"
AI: [consults trivial-whitelist] → item #4 (doc-only) → direct edit, no ritual

User: "bump next from 16.2.1 to 16.2.2"
AI: [consults trivial-whitelist] → item #3, check changelog → patch bump, no API change → direct edit, no ritual

User: "tweak the hero headline on the homepage"
AI: [consults trivial-whitelist] → not on list (UI change) → full ritual: epic, brainstorm, plan, ...
```

## Edge cases — ask the user

If any of these apply, stop and ask — do not auto-decide:
- Change is mostly formatting but includes one logic line
- Doc edit in `CLAUDE.md` or `knowledge/decisions/`
- Dependency bump crosses major version
- Project-specific `trivial_whitelist_extra` list applies (set in `./CLAUDE.md`)

## Per-project extensions

Projects can add to (never remove from) this whitelist via `trivial_whitelist_extra` in `./CLAUDE.md`:

```markdown
## Trivial whitelist extensions
- airtable.tables/*.json schema sync (auto-generated from Airtable)
- supabase/functions/_shared/types.ts (generated)
```

Extensions land during `/bootstrap-project` (when `everville-bootstrap` is installed).
