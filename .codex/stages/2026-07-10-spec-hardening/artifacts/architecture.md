---
schema_version: orchestration-artifact/v1
artifact_type: delegated-stream
task_id: 019f4ad4-1f14-7041-81e1-eb91c641b137/spec-architecture
stage_id: 2026-07-10-spec-hardening
agent_type: worker
subagent_model: inherit_orchestrator
reasoning_effort: inherit_orchestrator
model_reasoning_rationale: Cross-skill overlap and workflow fit required an independent package design.
repo: everville-workflow
branch: feat/spec-hardening-0.13.0
base_branch: fix/workflow-remediation-0.12.0
base_commit: 58bcf0c53d7d4b449919c213c742631b70a30eb5
worktree: /Users/niko.dev/Developer/work/everville-workflow-spec-hardening
write_zone:
  - read-only package and workflow architecture
success_criteria:
  - Select one-vs-many skill architecture.
  - Define positive and negative triggers, references, authority boundaries, and release placement.
selected_docs:
  - current repository architecture and runtime contracts
selected_skills:
  - skill-creator
  - everville-skill-judge rubric
selected_agents:
  - worker
catalog_candidates:
  - none
parallel_group: architecture
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
  - trigger and overlap matrix: passed
  - paper architecture review: passed
changed_files:
  - none
explicit_defers:
  - none
---

# Summary

Selected one `everville-spec-hardening` skill with three conditional references: decision coverage, boundary review, and delivery. Review and reconciliation remain one responsibility, avoiding duplicate ownership.

# Scope / Routing

Automatic routing is limited to existing multi-component/high-risk specifications and FULL DESIGN/PLAN work; explicit use still requires an existing spec. Brainstorming, routine BYPASS/LIGHT work, code review, debugging, prose cleanup, and concrete single-component plans stay outside the deep workflow.

# Verification

The design targets workflow version 0.13.0 and keeps meta/handoff unchanged. It requires no scripts, agents, secondary ledger, new dependency, or archive attribution.

# Delivery / Cleanup

The orchestrator implemented the accepted package shape and authority model manually in the integration worktree.

# Risks / Follow-ups / Explicit Defers

No architecture debt was deferred.
