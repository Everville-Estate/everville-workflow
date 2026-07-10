---
schema_version: orchestration-artifact/v1
artifact_type: delegated-stream
task_id: 019f4ad4-1f14-7041-81e1-eb91c641b137/docs-contracts
stage_id: 2026-07-10-workflow-remediation
agent_type: worker
subagent_model: inherit_orchestrator
reasoning_effort: inherit_orchestrator
model_reasoning_rationale: Platform-contract and onboarding corrections formed an independent documentation-sensitive stream.
repo: everville-workflow
branch: fix/remediation-docs
base_branch: main
base_commit: 65dcee6be9bc5fe6dcef14bd4504d365dc122a81
worktree: /Users/niko.dev/Developer/work/everville-workflow-docs-contracts
write_zone:
  - README.md
  - docs
  - plugins/everville-meta/skills/everville-plugin-forge
  - plugins/everville-meta/skills/everville-agent-md-refactor
  - plugins/everville-handoff
  - plugins/everville-workflow/commands/explain-pr-changes.md
success_criteria:
  - Make onboarding accurately describe all plugins and install scopes.
  - Align plugin, memory, rules, hooks, and skill guidance with current Claude Code contracts.
  - Make handoffs portable, aggregated, and safe for secrets.
  - Ensure PR explanation is read-only generation.
selected_docs:
  - https://code.claude.com/docs/en/hooks
  - https://code.claude.com/docs/en/plugins-reference
  - https://code.claude.com/docs/en/skills
  - https://code.claude.com/docs/en/memory
selected_skills:
  - orchestrator-stage
selected_agents:
  - worker
catalog_candidates:
  - none
parallel_group: docs-contracts
depends_on_streams:
  - none
parallel_decision: parallel
status: accepted
delivery_method: cherry-pick
accepted_by_orchestrator: yes
cleanup_status: blocked
cleanup_notes: Worktree removed; local branch retained because cherry-picked content is not Git-merged and force deletion was not authorized.
risk_level: medium
verification:
  - claude plugin validate . --strict: passed
  - claude plugin validate plugins/everville-meta --strict: passed
  - claude plugin validate plugins/everville-handoff --strict: passed
  - embedded handoff Python compile and fixtures: passed
  - git diff --check: passed
changed_files:
  - README.md
  - docs/architecture.md
  - docs/archive/architecture-2026-04-proposal.md
  - docs/instruction-refactor.md
  - plugins/everville-meta/skills/everville-plugin-forge
  - plugins/everville-handoff
  - plugins/everville-workflow/commands/explain-pr-changes.md
  - plugins/everville-workflow/CHANGELOG.md
explicit_defers:
  - none
---

# Summary

Corrected three-plugin onboarding, replaced stale architecture with a current account, archived the old proposal, aligned instruction and plugin guidance to current Claude Code contracts, and made handoff and PR-explanation behavior portable and safe.

# Scope / Routing

The stream was bounded to documentation, platform-contract guidance, handoff behavior, and the PR explanation command. The orchestrator later updated versions and package placement.

# Verification

The stream passed strict marketplace and plugin validation, frontmatter parsing, compiled embedded Python, valid and invalid handoff fixtures, stale-claim searches, and whitespace checks. The orchestrator repeated repository-wide validation after integration.

# Delivery / Cleanup

Accepted via cherry-pick as integration commit `d6d9216`. The isolated worktree was removed; the source branch remains because forced branch deletion was not authorized.

# Risks / Follow-ups / Explicit Defers

No implementation debt was deferred within the assigned scope.
