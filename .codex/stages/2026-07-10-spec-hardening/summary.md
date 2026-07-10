# Stage Summary - 2026-07-10 specification hardening

Objective: transform the useful architecture-review concepts in `Archive 2.zip` into an independently expressed, proportional Everville skill with proven safety, routing, usability, and packaging, while keeping PR `#16` untouched and unmerged.

## Parallel Decomposition Matrix

| Stream | Goal | Agent | Write zone | Dependencies | Verification | Model/reasoning | Decision | Reason |
|---|---|---|---|---|---|---|---|---|
| provenance | Establish original source, authorship, and license or a clean-room boundary | docs_researcher | read-only | archive and public sources | exact-phrase/source/license cross-check | inherit; provenance risk | parallel | Independent internet research with no shared writes |
| architecture | Design proportional package, triggers, references, and workflow boundaries | worker | read-only | archive concepts and current repo | positive/negative routing cases and paper rubric | inherit; cross-module design | parallel | Independent design surface |
| validation | Design deterministic, dry-run, security, install, and forward-test coverage | worker | read-only | current harnesses and candidate intent | exact case/assertion matrix | inherit; verification design | parallel | Independent evidence surface |
| implementation | Build the selected clean-room skill, tests, docs, versions, and stage evidence | orchestrator | skill package, manifests, docs, tests, stage files | provenance, architecture, validation | full local matrix | inherit; integration ownership | sequential | Shared packaging contract depends on all three research streams |
| forward-test | Exercise the candidate as a user-facing skill without leaking intended answers | fresh worker agents | isolated temporary/worktree outputs only | accepted candidate | objective prompt/output checks | inherit; fresh context | sequential | Candidate must exist first |
| integrated-review | Review the complete diff and evidence before publication | independent worker | read-only | final candidate SHA | blocker/should-fix gate | inherit; high-risk review | sequential | Stable integrated diff required |

Documentation: Agent Reach GitHub/search evidence for provenance; current repository and Claude Code `2.1.195` validators for runtime contracts.

Asset routing: `orchestrator-stage`, `task-router`, `skill-creator`, `skill-security-auditor`, Agent Reach, repo-local `everville-skill-judge`/`everville-skill-comply`, GitHub publish workflow, and `orchestration-closeout`; no catalog promotion.

Beads is unavailable. The active Codex goal, this stage summary, `.codex/handoff.md`, and delegated artifacts are task truth.

## Explicit defers

- Original authorship and license remain unknown; literal reuse requires a compatible license or written permission.
- Paid runtime compliance is not authorized. The accepted no-spend dry-run covers 12 planned executions with a maximum possible spend of $12.00 if later approved.

## Candidate outcome

- One independently written `everville-spec-hardening` skill with three conditional references; no custom agent, script, asset, or duplicate ledger.
- Workflow version 0.13.0; meta 0.3.0 and handoff 0.4.0 remain unchanged.
- 54 deterministic tests, including negative policy fixtures and proof that dry-run cannot execute model scenarios.
- Repository validation, current strict Claude Code validation, isolated cached installation, security scanning, process verification, and diff hygiene pass.
- Fresh-context positive and adjacent-negative behavior pass.
- Independent skill-judge result: 121/130 (A), Everville Fit 10/10, zero blocker; both should-fix findings corrected before stable commit.
