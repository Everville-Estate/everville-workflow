---
name: everville-agent-md-refactor
description: Refactor large or contradictory CLAUDE.md and AGENTS.md instruction sets in Everville repositories using real Claude Code loading mechanisms. Use @imports for universally required modules and path-scoped .claude/rules for conditional guidance while preserving safety-critical instructions.
license: MIT
---

<!--
  Adapted from softaworks/agent-toolkit (agent-md-refactor) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: renamed and corrected for Claude Code @imports,
  .claude/rules path scoping, AGENTS.md compatibility, and context cost.
-->

# Everville Agent MD Refactor

Refactor project instructions without changing their meaning or silently removing their runtime effect.

## Loading facts

- Claude Code loads project instructions from `CLAUDE.md` or `.claude/CLAUDE.md`.
- Claude Code does not load `AGENTS.md` by name. If it is the shared source, create a `CLAUDE.md` containing `@AGENTS.md` (plus any Claude-specific rules), or use a supported symlink.
- An ordinary Markdown link such as `[Testing](.claude/testing.md)` is navigation for humans, not an instruction import.
- `@path/to/file` in `CLAUDE.md` imports that file. Imports load at session start, including nested imports, so splitting into imports improves organization but does **not** reduce token cost.
- Markdown files under `.claude/rules/` are discovered as rules. A rule without `paths` frontmatter loads unconditionally. A rule with `paths` loads when Claude reads a matching file.
- Procedures that apply only on demand should become skills, not always-loaded instruction files.

## Safety invariant

Never delete, weaken, or conditionally hide an instruction concerning secrets, authentication, authorization, production writes, destructive commands, regulated data, source-of-truth boundaries, required verification, or explicit human approval merely to shorten the root file. Preserve it in an always-loaded project instruction unless its scope is truly limited and the path rule covers every affected file.

Record every moved, merged, and deleted instruction so reviewers can prove coverage.

## Process

### 1. Inventory and resolve contradictions

Read all relevant sources before editing:

```bash
find .. -name CLAUDE.md -o -name CLAUDE.local.md -o -name AGENTS.md
find .claude/rules -type f -name '*.md' 2>/dev/null
```

Build an inventory with columns for source, instruction, current scope, proposed destination, and disposition. Identify contradictions and ask the user to resolve only choices that materially change behavior. Do not pick one silently.

### 2. Classify by loading need

| Need | Destination | Context behavior |
| --- | --- | --- |
| Applies to every task | Root `CLAUDE.md` or unscoped `.claude/rules/*.md` | Always loaded |
| Universal module kept separate for ownership/readability | `@.claude/instructions/<topic>.md` import from root | Always loaded; no token saving |
| Applies only to known files/directories | `.claude/rules/<topic>.md` with `paths` | Loads on matching file reads |
| Repeatable multi-step procedure | `.claude/skills/<name>/SKILL.md` | Body loads when invoked |
| Personal, machine-specific preference | `CLAUDE.local.md` | Local project context; normally gitignored |
| Vague, redundant, or demonstrably obsolete | Delete with rationale | No load |

Keep the root concise, but do not use a line-count target as a reason to lose necessary context.

### 3. Choose imports or path rules deliberately

Use an import when every session needs the complete module:

```markdown
# Project name

Production application for ...

## Commands

- Build: `pnpm build`
- Test: `pnpm test`

## Required policy

@.claude/instructions/security.md
@.claude/instructions/release.md
```

Use path-scoped rules when guidance applies only to part of the tree:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "supabase/**/*.{sql,ts}"
---

# API and database rules

- Validate untrusted input at the boundary.
- Verify authorization independently of authentication.
- Include rollback and RLS evidence for schema changes.
```

Path patterns must cover tests, migrations, generated entry points, and alternate extensions where the rule still matters. If safe coverage cannot be expressed confidently, keep the rule unconditional.

### 4. Handle AGENTS.md repositories

When `AGENTS.md` is canonical for multiple tools, preserve that authority and add a small Claude bridge:

```markdown
# Claude Code instructions

@AGENTS.md

## Claude-specific notes

- [Only instructions that genuinely apply to Claude Code]
```

Do not duplicate the full text in both files; duplicated rules drift. If the project intentionally makes `CLAUDE.md` canonical, document that decision and update other tooling separately rather than assuming it reads Claude's file.

### 5. Delete only with evidence

Candidates for deletion include unverifiable advice ("write clean code"), facts already guaranteed by tooling, exact duplicates, and references to removed systems. "Do not commit secrets" is **not** automatically redundant: security and approval rules are safety-critical and should remain concrete.

Produce a deletion table:

| Original source | Instruction | Reason | Evidence |
| --- | --- | --- | --- |
| `CLAUDE.md` | ... | duplicate / obsolete / vague | replacement path, tool config, or commit |

## Verification

After editing:

1. Use `/memory` in Claude Code to confirm the root instructions and unconditional rules are loaded.
2. Confirm every `@import` target exists; imports are relative to the file containing them and recurse only to Claude Code's supported depth.
3. Open/read one matching and one non-matching file for each path rule, then use `/memory` or the `InstructionsLoaded` hook view/debug output to confirm expected loading.
4. Compare the instruction inventory against the new files. Every original instruction must be preserved, intentionally merged, or explicitly deleted.
5. Search for stale ordinary-link templates and duplicated text:

```bash
rg -n '\]\(\.claude/.*\.md\)' CLAUDE.md .claude 2>/dev/null
rg -n '^@' CLAUDE.md .claude/CLAUDE.md 2>/dev/null
```

6. Run the repository's normal validation and inspect `git diff --check`.

## Output

Report:

- files created, moved, and deleted;
- which content remains always loaded;
- which rules are path-scoped and their patterns;
- estimated context effect (imports do not save tokens; path rules and skills can);
- contradictions resolved by the user;
- the preservation/deletion inventory and verification evidence.
