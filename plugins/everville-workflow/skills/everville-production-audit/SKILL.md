---
name: everville-production-audit
description: Use before an Everville deployment for a local-evidence release-readiness audit of RLS/authz, migration safety, idempotency, env validation, secrets, CI evidence, and critical-path coverage. Invoke at the verify-to-finish boundary of unified-workflow or when asked whether a release is ready to ship. This reports a deterministic local readiness verdict; it does not verify production or deploy.
---

# Everville Local Release-Readiness Audit

A correct diff can still make an unsafe release. Review establishes whether a change is correct; this audit checks the locally inspectable release surface before deployment. It cannot prove that production is healthy or that a deployment succeeded.

## Operating rules

- **Local evidence only.** Read migrations, schema, route handlers, env schema, test results, CI status, and deploy configuration. Never hit production, run a remote scanner, or deploy.
- **Name the evidence.** Cite every file and command used. A check that could not run is missing, never passed.
- **Use the verdict rules exactly.** Do not invent points, weights, or a confidence score.
- **Report only.** Do not fix, migrate, or deploy while using this skill.

## Checks

| Surface | Verify | Typical evidence |
|---|---|---|
| **RLS / authz** | Every new or altered table has RLS and appropriate policy; policies do not recursively select their own table; service credentials cannot reach clients | `supabase/migrations/*`, schema, route handlers, `NEXT_PUBLIC_*` usage |
| **Migration safety** | No destructive operation on populated data lacks a safe backfill/transition; rollback or an explicit forward-only recovery path exists | migration diff and release notes |
| **Idempotency** | Webhooks and jobs deduplicate retries so they cannot double-charge, double-insert, or double-send | webhook, queue, cron, and edge-function handlers |
| **Env fail-fast** | Required variables are validated at startup; public env changes require a fresh build | env schema, `next.config.*`, build configuration |
| **Boundary validation** | User input and external responses are validated; detached `next after()` work does not assume request auth | routes, server actions, `after()` callbacks |
| **Secrets and logs** | Secrets are absent from browser code, action return values, committed env files, and logs | source searches and client boundaries |
| **CI and critical path** | CI is confirmed green for the current head; the critical path has automated or recorded manual-test evidence | `gh pr checks`, SHA evidence, tests, release notes |

Run reproducible checks where applicable:

```bash
rg -n "SERVICE_ROLE|service_role" app components -g '!**/route.ts' -g '!**/*.server.ts'
gh pr checks --watch=false
```

Tier 1 (aviation, financial, or investor-facing) evaluates every row. Tier 2 evaluates every row affected by the change. Mark an unaffected row `N/A` with a reason; never skip it silently.

## Deterministic verdict

Apply these rules in order:

1. **BLOCK** if any applicable blocker is found or its required evidence is missing: RLS/authz on a changed table, idempotency for a changed webhook/job, safe migration/recovery for a destructive migration, or protection against secret exposure.
2. **SHIP WITH RISK** if there is no blocker but any applicable risk remains or its evidence is missing: current-head CI, critical-path test/manual evidence, required-env fail-fast validation, boundary validation, or another unresolved release risk. Name an owner for every accepted risk.
3. **SHIP** only when every applicable check is verified and no blocker or unresolved risk remains.

These are hard verdict caps: one blocker caps the verdict at **BLOCK**; otherwise one unresolved risk caps it at **SHIP WITH RISK**. Findings cannot be offset by unrelated strengths.

The most common false pass is treating green CI as release readiness. CI covers only tested behavior; inspect migration recovery, idempotency, authz, and secrets directly.

## Required output

```markdown
## Local Release-Readiness Audit — <app/PR>   Tier: <1|2>
**Verdict: SHIP | SHIP WITH RISK | BLOCK**
**Scope:** local evidence only; production state not verified

### Evidence checked
- <surface>: <file or command> -> <finding and severity>

### Evidence missing
- <surface>: could not verify <X> because <reason> -> <verdict effect>

### Required before ship
- <blocker and specific fix, or risk, owner, and acceptance decision>
```

Use `Blocker`, `Should-fix`, and `Nice-to-have` labels consistently with the workflow review step. Omit `Required before ship` only for `SHIP`.

## Anti-patterns

- Declaring production healthy from local evidence.
- Passing a check that was not performed.
- Auditing only the diff instead of the release surface.
- Re-scoring a blocker because unrelated checks passed.
- Fixing or deploying instead of returning the audit.
