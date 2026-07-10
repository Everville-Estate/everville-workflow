# Changelog

This file records marketplace-level releases. Individual component history may be summarized here when multiple plugins change together.

## everville-workflow 0.12.0 / everville-meta 0.3.0 / everville-handoff 0.4.0 - 2026-07-10

### Changed

- Scope automatic workflow guidance to verified Everville repositories and make the hook's advisory boundary explicit.
- Add deterministic tests for hook and compliance-harness behavior.
- Replace stale onboarding and architecture documents with current platform guidance.
- Add repository validation, CI, CODEOWNERS, and a review-focused pull request template.
- Add an isolated three-plugin installation gate that validates the cached consumer packages.
- Recalibrate workflow, entropy, skill-quality, handoff, and plugin-authoring guidance.
- Move instruction-refactoring and skill-quality/diagnostic tools into `everville-meta` so ordinary workflow installations carry a smaller always-on discovery surface.

### Security

- Remove unbounded path-substring exemptions, repository-marker collisions, repeated denial on marker-write failure, undeclared runtime dependencies, and retained temporary compliance traces.
