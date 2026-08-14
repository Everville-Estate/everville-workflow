---
name: trivial-whitelist
description: Use before any Everville repository change to route it deterministically to BYPASS, LIGHT, or FULL. BYPASS is a hard whitelist for non-behavioral edits; LIGHT handles ordinary non-trivial code, UI, config, dependency, and agent-instruction changes; FULL handles critical or structural work such as auth, migrations/RLS, payments/webhooks, destructive data operations, cross-cutting refactors, and critical surfaces. Returns one verdict with the matching rule.
---

# Trivial Whitelist — Track Router

Consult this skill before changing an Everville repository. This skill is the single authoritative source for BYPASS/LIGHT/FULL classification; downstream workflow skills consume its verdict and must not repeat these trigger rules. Return exactly one verdict and cite the matching rule:

- **BYPASS** — direct edit plus proportionate verification; do not invoke unified-workflow.
- **LIGHT** — invoke unified-workflow and use its four-phase track.
- **FULL** — invoke unified-workflow and use its 11-step track.

Apply the first matching section below. Do not collapse every non-trivial change into FULL.

## 1. FULL triggers

Return **FULL** when any condition holds:

- Critical surface: aviation, financial, investor-facing, or explicitly Tier 1.
- Database schema, migration, RLS, destructive/backfill data operation.
- Auth, session, permissions, secrets, payments, webhooks, or durable jobs.
- Cross-cutting refactor or runtime behavior spanning multiple subsystems.
- Agent hooks or guardrails whose failure/bypass affects many repositories or sessions.
- The user explicitly requests the FULL track.

## 2. BYPASS whitelist

If no FULL trigger applies, return **BYPASS** only for these isolated changes:

1. Typo or comment-only correction with no executable/instruction behavior change.
2. Formatting-only output from an established formatter, committed without logic changes.
3. Patch/minor dependency bump whose changelog or release notes confirm no relevant API/behavior change.
4. Explanatory docs/README edits that do not change a decision, contract, runbook, generated interface, or agent instruction.
5. README badge/URL/coverage-number maintenance.
6. Additive ignore patterns in `.gitignore`, `.vercelignore`, or `.dockerignore`; removals are not BYPASS.
7. Lockfile regeneration committed alone after the originating dependency operation is already approved.

BYPASS still requires evidence appropriate to the edit: inspect the diff and run a cheap relevant check when one exists. It means “no workflow track,” not “no verification.”

## 3. LIGHT default

Return **LIGHT** for everything else non-trivial, including:

- Ordinary business logic, API routes/server actions, algorithms, and data transformations without a FULL trigger.
- UI components, styling, copy, or interaction changes.
- Runtime config such as `next.config.*`, `vercel.json`, or `.env.example` without secrets/permission changes.
- `CLAUDE.md`, `AGENTS.md`, `SKILL.md`, agent definitions, or slash commands that change agent behavior but are not cross-cutting hooks/guardrails.
- ADR/decision-content edits.
- Major dependency bumps, or patch/minor bumps whose compatibility cannot be verified, unless discovered impact upgrades them to FULL.
- Mixed formatting plus any behavior line.

If LIGHT work later exposes a FULL trigger, upgrade in place under unified-workflow.
Rerun this router to record that upgraded verdict; unified-workflow does not reclassify it independently.

## Examples

```text
README spelling only                              -> BYPASS (rule 1)
Verified patch bump with no relevant API change  -> BYPASS (rule 3)
Hero headline or button styling                  -> LIGHT
Small non-auth server action                     -> LIGHT
SKILL.md trigger wording                         -> LIGHT
PreToolUse enforcement hook                      -> FULL
RLS policy or payment webhook                    -> FULL
```

## Project extensions

A project may add BYPASS cases through an explicit `trivial_whitelist_extra` section in its root instructions. Extensions may add narrow generated or mechanical paths, but cannot downgrade a FULL trigger. Cite the exact extension when using it.

Ask the user only when the verdict depends on unavailable information that cannot be obtained safely, such as whether a dependency release changes an API used by the project. Otherwise inspect the repository and choose deterministically.
