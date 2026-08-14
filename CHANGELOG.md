# Changelog

This file records marketplace-level releases. Individual component history may be summarized here when multiple plugins change together.

## everville-workflow 0.14.0 / everville-meta 0.4.0 - 2026-08-14

### Changed

- Remove the per-tool mutation gate and duplicate classification, stage-ledger, and orchestration machinery.
- Keep one live, repository-scoped SessionStart identity check and require isolated worktrees or sequential writers.
- Replace readiness scores with deterministic evidence verdicts and move PR explanation into an explicit-only skill.
- Give compliance outcomes distinct nonzero exits for non-compliance, infrastructure failure, and inconclusive evidence.
- Reduce broad lesson catalogs and make any global memory persistence explicit-request-only.

### Deployment

- Require project scope for the workflow, local scope for the meta plugin, and retain user scope only for the explicit handoff plugin.
- Record the audited canonical, stale-clone, external, and identity-ambiguous repository boundaries in `docs/deployment-scope.md`.

## everville-workflow 0.13.0 - 2026-07-10

### Added

- Add an independently written specification-hardening skill for approved multi-component or high-risk designs, with focused decision-coverage, boundary-review, and delivery references.
- Add deterministic positive/negative routing contracts, archive-fingerprint exclusions, no-spend compliance scenarios, and cached-package verification for the new skill.

### Security

- Treat the unlicensed reference archive as unknown-rights material: no copied text, attribution claim, bundled source, mandatory agent behavior, or reasoning-transcript persistence is included.

## everville-workflow 0.12.0 / everville-meta 0.3.0 / everville-handoff 0.4.0 - 2026-07-10

### Changed

- Scope automatic workflow guidance to verified Everville repositories and make the hook's advisory boundary explicit.
- Add deterministic tests for hook and compliance-harness behavior.
- Replace stale onboarding and architecture documents with current platform guidance.
- Add repository validation, CI, CODEOWNERS, and a review-focused pull request template.
- Add an isolated three-plugin installation gate that validates the cached consumer packages.
- Pin current Node 24 GitHub Actions releases by commit SHA so CI has no deprecated-runtime warning or floating action dependency.
- Recalibrate workflow, entropy, skill-quality, handoff, and plugin-authoring guidance.
- Move instruction-refactoring and skill-quality/diagnostic tools into `everville-meta` so ordinary workflow installations carry a smaller always-on discovery surface.

### Security

- Remove unbounded path-substring exemptions, repository-marker collisions, repeated denial on marker-write failure, undeclared runtime dependencies, and retained temporary compliance traces.
