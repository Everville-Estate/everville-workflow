---
schema_version: orchestration-artifact/v1
artifact_type: delegated-stream
task_id: 019f4ad4-1f14-7041-81e1-eb91c641b137/spec-test-strategy
stage_id: 2026-07-10-spec-hardening
agent_type: worker
subagent_model: inherit_orchestrator
reasoning_effort: inherit_orchestrator
model_reasoning_rationale: Independent verification design was needed before integration.
repo: everville-workflow
branch: feat/spec-hardening-0.13.0
base_branch: fix/workflow-remediation-0.12.0
base_commit: 58bcf0c53d7d4b449919c213c742631b70a30eb5
worktree: /Users/niko.dev/Developer/work/everville-workflow-spec-hardening
write_zone:
  - read-only validation design
success_criteria:
  - Define deterministic policy, packaging, compliance, security, install, and forward-test gates.
selected_docs:
  - repository validator, CI, install gate, comply harness, and skill-judge rubric
selected_skills:
  - skill-security-auditor
  - everville-skill-comply
selected_agents:
  - worker
catalog_candidates:
  - none
parallel_group: validation
depends_on_streams:
  - none
parallel_decision: parallel
status: accepted
delivery_method: manual integration
accepted_by_orchestrator: yes
cleanup_status: cleaned
cleanup_notes: Read-only stream created no branch, worktree, or files.
risk_level: medium
verification:
  - exact test and failure matrix: passed
  - fresh-agent prompt design: passed
changed_files:
  - none
explicit_defers:
  - paid runtime compliance experiment requires separate approval of the printed maximum spend
---

# Summary

Defined a zero-spend deterministic matrix for exact package shape, routing, modes/verdicts, authority, no private reasoning, no duplicate ledger, clean-room fingerprints, synchronized versions, safe link resolution, and no-spend scenario execution.

# Scope / Routing

The design also requires strict current-runtime validation, security scanning, isolated cached installation, fresh-agent positive/negative behavior, and independent paper review.

# Verification

The orchestrator implemented the selected matrix in repository tests, CI, the repository validator, the marketplace installation gate, and a four-scenario dry-run fixture.

# Delivery / Cleanup

Accepted through manual integration. No child cleanup was needed.

# Risks / Follow-ups / Explicit Defers

The compliance dry-run validates configuration and command construction only. It does not prove automatic runtime invocation; a paid experiment remains separately authorized.
