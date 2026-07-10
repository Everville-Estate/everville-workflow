---
schema_version: orchestration-artifact/v1
artifact_type: delegated-stream
task_id: 019f4ad4-1f14-7041-81e1-eb91c641b137/gate-runtime
stage_id: 2026-07-10-workflow-remediation
agent_type: worker
subagent_model: inherit_orchestrator
reasoning_effort: inherit_orchestrator
model_reasoning_rationale: High-risk hook behavior needed a bounded implementation stream and deterministic tests.
repo: everville-workflow
branch: fix/remediation-gate
base_branch: main
base_commit: 65dcee6be9bc5fe6dcef14bd4504d365dc122a81
worktree: /Users/niko.dev/Developer/work/everville-workflow-gate-runtime
write_zone:
  - plugins/everville-workflow/hooks
  - tests/test_gate_check.py
success_criteria:
  - Gate only verified GitHub Everville-Estate repositories.
  - Scope markers by session, worktree root, and canonical remote.
  - Cover linked worktrees, exemptions, fail-open behavior, and mutating Bash with tests.
selected_docs:
  - https://code.claude.com/docs/en/hooks
selected_skills:
  - orchestrator-stage
selected_agents:
  - worker
catalog_candidates:
  - none
parallel_group: gate-runtime
depends_on_streams:
  - none
parallel_decision: parallel
status: accepted
delivery_method: cherry-pick
accepted_by_orchestrator: yes
cleanup_status: blocked
cleanup_notes: Worktree removed; local branch retained because cherry-picked content is not Git-merged and force deletion was not authorized.
risk_level: high
verification:
  - python3 -m unittest tests.test_gate_check -v: passed
  - claude plugin validate plugins/everville-workflow --strict: passed
  - git diff --check: passed
changed_files:
  - plugins/everville-workflow/hooks/hooks.json
  - plugins/everville-workflow/hooks/gate-check.py
  - tests/test_gate_check.py
explicit_defers:
  - none
---

# Summary

Scoped the advisory first-mutation gate to authenticated Everville GitHub repositories, corrected marker identity and worktree behavior, expanded Bash coverage, and added a deterministic 15-test matrix.

# Scope / Routing

The stream stayed inside hook runtime files and their tests. It inherited the orchestrator model and reasoning policy; no additional catalog asset was needed.

# Verification

The stream passed its focused 15-test suite, strict workflow-plugin validation, and whitespace checks. The orchestrator reran these checks after integration.

# Delivery / Cleanup

Accepted via cherry-pick as integration commit `43bb435`. The isolated worktree was removed. The source branch remains because safe cleanup does not force-delete a cherry-picked branch without authorization.

# Risks / Follow-ups / Explicit Defers

Shell classification is deliberately conservative and remains an advisory speed bump, not a sandbox. No implementation debt was deferred.
