# Current state

Everville Workflow 0.14.0 and Meta 0.4.0 are being prepared on `feat/workflow-cleanup-0.14.0` from `origin/main` at `18ec08b0bd152740368d4d33b0ee40089679479e`.

The upgrade removes the unused local stage-orchestration subsystem and the per-tool mutation hook, keeps one live repository-scoped SessionStart identity check, centralizes BYPASS/LIGHT/FULL routing, requires isolated worktrees or sequential writers instead of a fragile shared-lock protocol, replaces production-readiness scores with deterministic local-evidence verdicts, distinguishes compliance failure modes by exit status, moves PR explanation to an explicit-only skill, and trims generic lesson material.

A 2026-08-14 workstation audit found that `everville-workflow` was active in zero repositories: its only recorded installation was disabled at user scope. `everville-meta` was also disabled at user scope. `everville-handoff` alone was enabled globally. The intended post-release boundary is workflow at project scope in 22 verified canonical Everville repositories, meta local to this maintainer repository, and explicit-only handoff at user scope. Nine stale duplicate clones, thirteen non-Everville repositories, and six identity-ambiguous adjacent repositories are excluded pending separate reconciliation. See `docs/deployment-scope.md`.

## Resume point

The final source candidate passes 53 unit tests, repository validation, strict marketplace/all-plugin validation, isolated three-plugin installation, Python compilation, compliance dry-run, diff hygiene, live canonical and formerly aliased `private-coach` SessionStart checks, and strict security scans for all 14 skills. A live Sonnet probe loaded the candidate plugin and completed a routing scenario. Independent exact-diff review has no remaining findings.

Commit, push, and open the protected pull request. Do not persistently install the feature checkout or enable the old 0.13.0 release. After the pull request is approved and merged, update the marketplace and roll 0.14.0 out only to the verified project-scope targets, then verify the installed cache and actual hook surface.

## External gate

Repository protection requires an approving review and current-head CI. Do not bypass that protection or present an unmerged feature branch as a released installation.
