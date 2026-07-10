---
name: loop-on-ci
description: Explicit side-effecting procedure for a user who invokes /everville-workflow:loop-on-ci to diagnose failing PR or branch checks, make bounded local fixes, and—only when separately authorized for the exact branch—push and re-watch. A watch-only request remains read-only. Covers Everville-specific CI traps such as E2E serialization, stale same-name check runs, kb:map drift, and merge races.
disable-model-invocation: true
---

<!--
  Adapted from cursor/plugins cursor-team-kit (fix-ci + loop-on-ci, merged — their
  triggers overlap: "fix failing CI" is a subset of "loop until green") — MIT licensed,
  see LICENSES/cursor-MIT.txt. Everville modifications: gh-native workflow kept;
  added the team-burn guardrails below (E2E serialization, latest-run-per-name,
  Review Gate re-arm, kb:map drift, headRefOid merge race, main-comparison triage).
-->

# Loop on CI

Watch a branch/PR's checks and iterate on failures until green. `gh pr checks` is the source of truth — it includes ALL PR-attached checks (Vercel, Checkly, Meticulous), while `gh run list` only covers GitHub Actions.

## Authorization boundary

This skill is explicitly invoked because it may create commits and publish fixes. A request to **watch**, inspect, or explain CI authorizes read-only access only. A request to **fix CI** authorizes bounded local edits and verification, but does not by itself authorize `git push`, PR edits, reruns that consume scarce resources, or merge. Before the first remote mutation, require explicit authorization for the exact repository and branch. Never merge from this skill.

## Workflow

1. Resolve the PR: `gh pr view --json number,url,headRefName`.
2. Inspect before waiting: `gh pr checks --json name,bucket,state,workflow,link,startedAt,completedAt`. Failures already present → diagnose those first; pending → watch.
3. Watch in the **background**, not a blocking foreground call — `gh pr checks --watch --fail-fast` as a background task (or dispatch the `ci-watcher` agent) and keep working; never sit idle polling. No state change in ~30 min → treat as stalled and report, don't wait forever.
4. For a failed GitHub Actions check: extract the `<run-id>` from the check's `link` field (`…/actions/runs/<run-id>/job/…`), then `gh run view <run-id> --log-failed` and extract the **first actionable error**, not the last line of noise. For a failed external check (Vercel/Checkly/Meticulous) there are no gh logs — open the `link`, report the failing state and hand the user the URL if the dashboard needs auth.
5. Apply the smallest safe fix for **one failure cause** and run the relevant local check. If publishing that exact branch is authorized, push and go to 2. Otherwise report the verified local fix and the pending push; do not mutate the remote. The check set can change after an authorized push — always re-read it. **After 3 fix cycles on the same check without progress, stop and report** — thrashing hides the real cause; escalate with the evidence collected.

## Triage order for a red check

1. **Same failure on main?** `gh run list --branch main --workflow <wf> --limit 3`. If main is red the same way, the failure predates the PR — do not absorb unrelated fixes into it. Report the evidence; integrate a main-side fix only when that branch update is separately authorized.
2. **Stale run of the same name?** Two check runs with one name coexist after re-triggers (e.g. a gate that failed pre-review and passed post-review). Mergeability uses the **latest** run — compare `startedAt` timestamps before treating a `fail` line as current.
3. **Known flake signature?** Retry once and report the flake evidence; don't "fix" a flake with code.
4. Only then treat it as a real regression introduced by the PR.

## Everville-specific traps (each of these has burned the team)

- **E2E suites share one test project** — never let two E2E-bearing runs overlap, including main's push CI after a merge. One suite at a time; on member-churn signatures, rerun the suite solo.
- **New root-level files invalidate the Agent KB** — if "Agent KB drift check" fails after adding any file, run `pnpm kb:map` and commit `docs/agent-kb/generated/` in the same PR.
- **Review Gate evidence expires on push** — review evidence is pinned to the head SHA; after any push, re-run the reviewer (`/code-review --comment` or re-post the review) or the gate stays red.
- **Merge race** — before a separately authorized merge performed outside this skill, verify `gh pr view --json headRefOid` equals your local `git rev-parse HEAD`; a watcher that went green for an older SHA proves nothing about the current head. Re-arm the watch after any authorized push.
- **Playwright artifacts** — failure screenshots land in `test-results/`; when a report upload looks empty, check both the reporter path and `test-results/`.

## Guardrails

- One failure cause per fix; minimal low-risk change before any refactor.
- Never `--no-verify` to force progress.
- A fix that edits the failing test's assertions is a finding to report, not a fix to push silently.

## Output

Report: current CI status, the primary failing job + root error, fixes applied in order, whether remote publication was authorized/performed, and the PR URL when available.
