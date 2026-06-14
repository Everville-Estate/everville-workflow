---
name: everville-production-audit
description: Use before deploying an Everville app to production — a local-evidence ship/block readiness audit of the release surface (Supabase RLS, migration rollback, webhook/job idempotency, env fail-fast, authz boundaries), not diff correctness. Invoke at the verify→finish boundary of unified-workflow, when the user says "is this ready to ship / deploy / go live", or before any prod Vercel promotion of a tier-1 (balicopter/financial) or investor-facing surface. Emits a scored verdict with mandatory Evidence-checked / Evidence-missing sections.
---

# Everville Production Audit

A diff can be correct and the release still unsafe. Code review answers "is this change right?"; this answers "is the **release surface** ready?" — the things that only bite in production: a migration with no way back, a webhook that double-charges on retry, an env var that fails open, a new table with no RLS. This skill is the gate between VERIFY and FINISH.

## Operating rules

- **Local evidence only.** Read migrations, schema, route handlers, env schema, CI status, deploy config. Never run a remote scanner, never hit production, never deploy. The deliverable is a verdict, not an action.
- **Name your evidence.** Every conclusion cites the file/command it came from. A check you couldn't run is "missing," not "passed." Unverifiable ≠ safe.
- **Block on absence, not just on failure.** "No rollback path found" blocks the same as "rollback is broken." Silence about a release-surface concern is a finding.

## The audit — gather evidence for each, on our stack

| Surface | What to verify | Where to look |
|---|---|---|
| **RLS / authz** | Every new or altered table has RLS enabled + a policy; no policy sub-selects its own table (use SECURITY DEFINER); service-role key never reaches the client bundle | `supabase/migrations/*`, Drizzle schema, route handlers, `NEXT_PUBLIC_*` usage |
| **Migration reversibility** | Forward migration is safe (no destructive `DROP`/`ALTER … NOT NULL` on populated columns without backfill) and has a stated rollback or is provably forward-only | `supabase/migrations/*`, the PR's migration diff |
| **Idempotency** | Webhooks and background jobs dedupe on a key — a retry or double-delivery doesn't double-charge, double-insert, or double-send | webhook routes, edge functions, queue/cron handlers |
| **Env fail-fast** | Required env vars are validated at boot and throw if missing — not silently `undefined`; `NEXT_PUBLIC_*` changes are paired with a fresh build, not just a redeploy | env schema/zod, `next.config`, build settings |
| **Boundary validation** | User input and external API responses validated at the boundary; internal guarantees trusted. Watch the Everville footgun: a `next after()` callback runs as anon with no request auth, so RLS-gated writes inside it silently no-op | route handlers, server actions, `after()` calls |
| **Secrets & logs** | No service-role key or secret reaching the client — including via a server action whose return value lands in a client component; nothing secret in committed `.env` or logs | the checks below, `.env*`, client components |
| **CI & critical path** | CI is actually green (not "looks green"); the critical user path has a test or a written manual-test note | the checks below, test files, the spec |

Two checks worth running rather than eyeballing — they make the evidence reproducible:

```bash
# Service-role key referenced anywhere that ships to the browser (must be empty)
rg -n "SERVICE_ROLE|service_role" app components -g '!**/route.ts' -g '!**/*.server.ts'
# Real CI state for this branch's PR (don't trust the green checkmark in the UI alone)
gh pr checks --watch=false
```

Tier-1 (balicopter aviation, anything financial/investor-facing) audits **all** rows. Tier-2 audits the rows the change touches. Skip nothing silently — if a row is N/A, say why.

## Scoring — caps are the point

Start at 100, deduct for findings, then apply **hard caps** (a cap overrides the deducted score — you cannot buy back a structural gap with polish elsewhere):

- **Cap at 69 (BLOCK)** if any of: a new/altered table ships without RLS or authz; a webhook/job is non-idempotent; a migration is destructive with no rollback or backfill; a secret can reach the client or logs.
- **Cap at 84 (SHIP WITH RISK)** if any of: CI is not confirmed green; the critical path has no test or manual-test evidence; required env vars aren't validated at boot.
- **Bands:** 85–100 SHIP · 70–84 SHIP WITH RISK (named, owner-assigned) · ≤69 BLOCK.

The single most common false pass: **treating green CI as production readiness.** CI proves the code the tests cover works; it says nothing about rollback, idempotency, or authz. Audit those directly.

## Required output

```
## Production Audit — <app/PR>   Tier: <1|2>
**Verdict: SHIP | SHIP WITH RISK | BLOCK**   Score: NN/100  (cap: <none|69|84> — <why>)

### Evidence checked
- <surface>: <what you read> → <finding + severity 🔴/🟠/🟡>

### Evidence missing
- <surface>: could not verify <X> because <reason> — treated as a finding

### Required before ship  (only if BLOCK / SHIP WITH RISK)
- 🔴 <blocker + the specific fix>
- 🟠 <risk to accept explicitly, with an owner>
```

Reuse the REVIEW step's severity labels (🔴 Blocker / 🟠 Should-fix / 🟡 Nice-to-have) so triage stays consistent across the workflow.

## Anti-patterns

- **"CI is green, ship it."** CI ≠ release readiness. See above.
- **Scoring on polish.** A well-tested feature with no RLS on its table is a BLOCK, not an 80. Caps exist so cosmetics can't outvote structure.
- **Passing what you couldn't check.** If you didn't find the rollback path, the verdict is "missing," not "fine."
- **Auditing the diff instead of the surface.** That's the REVIEW step's job; this one inspects what production will actually run. If you trip over a diff-correctness bug here, hand it back to REVIEW rather than re-litigating it — don't double-own correctness.
- **Acting on the finding.** This skill reports. It does not fix, migrate, or deploy — that's the user's call after reading the verdict.
