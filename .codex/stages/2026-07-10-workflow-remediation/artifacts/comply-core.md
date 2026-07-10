---
schema_version: orchestration-artifact/v1
artifact_type: delegated-stream
task_id: 019f4ad4-1f14-7041-81e1-eb91c641b137/comply-core
stage_id: 2026-07-10-workflow-remediation
agent_type: worker
subagent_model: inherit_orchestrator
reasoning_effort: inherit_orchestrator
model_reasoning_rationale: Cross-module compliance semantics and evidence quality needed a bounded specialist stream.
repo: everville-workflow
branch: fix/remediation-comply
base_branch: main
base_commit: 65dcee6be9bc5fe6dcef14bd4504d365dc122a81
worktree: /Users/niko.dev/Developer/work/everville-workflow-comply-core
write_zone:
  - plugins/everville-workflow/skills/everville-skill-comply
  - plugins/everville-workflow/skills/everville-skill-judge
  - plugins/everville-workflow/skills/everville-skill-stocktake
  - plugins/everville-workflow/skills/unified-workflow
  - plugins/everville-workflow/skills/trivial-whitelist
  - plugins/everville-workflow/skills/everville-reduce-entropy
  - tests/test_skill_comply.py
success_criteria:
  - Make compliance results reproducible and confidence-aware.
  - Reconcile workflow tiers, review ordering, and optional-tool fallbacks.
  - Remove harmful line-count incentives while preserving safety controls.
selected_docs:
  - https://code.claude.com/docs/en/plugins-reference
  - https://code.claude.com/docs/en/skills
selected_skills:
  - orchestrator-stage
selected_agents:
  - worker
catalog_candidates:
  - none
parallel_group: comply-core
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
  - python3 -m unittest tests.test_skill_comply -v: passed
  - unified-workflow dry-run: passed
  - trivial-whitelist dry-run: passed
  - claude plugin validate plugins/everville-workflow --strict: passed
  - git diff --check: passed
changed_files:
  - plugins/everville-meta/skills/everville-skill-comply
  - plugins/everville-meta/skills/everville-skill-judge
  - plugins/everville-meta/skills/everville-skill-stocktake
  - plugins/everville-workflow/skills/unified-workflow/SKILL.md
  - plugins/everville-workflow/skills/trivial-whitelist/SKILL.md
  - plugins/everville-workflow/skills/everville-reduce-entropy/SKILL.md
  - tests/test_skill_comply.py
explicit_defers:
  - none
---

# Summary

Rebuilt the compliance harness around JSON scenarios, explicit candidate loading, timeouts, trace cleanup, classified infrastructure errors, and evidence-calibrated claims. Reconciled the workflow tiers and moved maintenance skills into the opt-in meta plugin during integration.

# Scope / Routing

The agent implemented the harness and core-skill corrections in its assigned paths. The orchestrator performed the packaging move to `everville-meta` and updated all references after acceptance.

# Verification

The stream passed 14 focused unit tests and both three-run scenario dry-runs. The orchestrator repeated those checks after the plugin move and validated every plugin strictly.

# Delivery / Cleanup

Accepted via cherry-pick as integration commit `db910e2`. The isolated worktree was removed; the source branch remains under the safe-cleanup rule.

# Risks / Follow-ups / Explicit Defers

No paid live `claude -p` compliance run was performed; configuration and command construction were verified without spend. This is a measurement choice, not untracked implementation debt.
