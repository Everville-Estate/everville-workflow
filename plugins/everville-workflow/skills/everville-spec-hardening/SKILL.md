---
name: everville-spec-hardening
description: Use when an existing approved or implementation-bound Everville specification spans multiple components, shared data or types, lifecycle or authorization boundaries, critical operations, concurrency, or recovery, or when the user explicitly asks to deeply interrogate, reconcile, or synthesize such a specification. Supports FULL DESIGN/PLAN work by finding decision gaps and boundary conflicts, then producing traceable amendments and verification obligations. Do not use for initial brainstorming, routine BYPASS/LIGHT work, code review or debugging, prose cleanup, or a concrete single-component plan.
---

# Everville Spec Hardening

Harden an existing specification before implementation or release planning. Keep the work proportional, evidence-linked, and inside the authority already granted for the task.

## Applicability gate

Use this skill only when at least one condition is true:

- The user explicitly requests specification interrogation, reconciliation, synthesis, or this skill for an existing specification.
- An existing implementation-bound specification crosses components and shares schemas, identifiers, events, permissions, lifecycle rules, or operational state.
- A Tier-1 or otherwise high-risk design depends on concurrency, retries, recovery, migration, or irreversible decisions that are not yet implementation-ready.
- The FULL workflow reaches DESIGN or PLAN with one of those specification risks.

Do not invoke it merely because a document is called a spec. Explicitly naming the skill does not remove the prerequisite for an existing specification; if the user is creating the design from scratch, route to brainstorming or the normal design process first. Route implementation and code-diff defects to the normal workflow and code review. A bounded, concrete single-component plan does not need this skill unless the user explicitly asks for a review of its existing specification.

If the gate does not pass, state the better-fitting path and continue there without adding ceremony.

## Modes and authority

Choose exactly one mode from the request; default to **REVIEW** when write authority is absent:

- **REVIEW** — assess and report. Never edit local inputs or create external state.
- **HARDEN** — make the requested local specification amendments. Preserve history and do not publish them remotely.
- **DELIVER** — produce the requested implementation-ready output while preserving the historical input unless the user explicitly names it as the canonical file to replace.

None of these modes authorizes push, PR creation or editing, merge, publication, release, deployment, or contacting people. Those external mutations require separate explicit authority.

Use the project's existing plan, issue/Beads epic, ADR, decision log, or handoff as task truth. Do not create a parallel status ledger. Subagents are optional: deploy them only when the user or active governing instructions authorize agents. Without that authority, use a single-agent path. When agents are authorized, parallelize only independent read-only work or disjoint write zones.

Persist evidence, findings, decisions, assumptions, and concise rationale. Never request or persist full, private, internal, or hidden reasoning, chain-of-thought, or agent transcripts.

## Workflow

### 1. Establish the review frame

Identify:

- the canonical specification and its intended decision point;
- components and actors inside scope;
- existing contracts, constraints, and repository evidence;
- facts that are fixed, assumptions that are provisional, and choices that still need an owner.

If a necessary source is missing, continue with an explicitly bounded assessment when useful. Ask the user only when a genuine domain tradeoff, missing authority, or unavailable fact would materially change the outcome.

### 2. Test decision coverage

Read [`references/decision-coverage.md`](references/decision-coverage.md) only when required behavior, policy, contracts, state transitions, or exception handling may be underspecified. Convert ambiguity into concrete scenarios and decision questions. Do not invent domain policy to make the document look complete.

### 3. Review shared boundaries

Read [`references/boundary-review.md`](references/boundary-review.md) only when components exchange data, authority, state, or control, or when a proposed resolution needs cross-system ripple analysis. Check both steady-state compatibility and transitions under simultaneous work, partial failure, retry, recovery, and rollout.

Record each material issue with:

- a stable ID;
- affected surfaces;
- source evidence or the missing evidence;
- the condition that exposes the issue;
- user/system impact;
- a recommended resolution or an explicit decision question;
- priority: **blocking**, **important**, or **optional**;
- disposition: **open**, **resolved**, or **deferred with owner**.

Findings and reconciliation are one responsibility. Do not produce one review that another process must rediscover before it can resolve the same conflicts.

### 4. Reconcile with minimum ripple

For a clear defect, propose the smallest coherent amendment and list every dependent contract that must be rechecked. For a real tradeoff, present concise options, consequences, and the decision owner; do not choose silently or require approval for mechanical consistency repairs.

After each accepted resolution, rerun only the affected boundary and decision checks. Perform a final global terminology and invariant scan once all blocking items are settled.

### 5. Deliver implementation-ready conclusions

Read [`references/delivery.md`](references/delivery.md) only when producing or updating an output specification. Report conclusions and traceable rationale, not a transcript of analysis.

The default deliverable contains:

1. Scope and source baseline.
2. Confirmed decisions and invariants.
3. Amendments, keyed to finding IDs and source locations.
4. Open decisions with owner and implementation impact.
5. Cross-component verification obligations.
6. Deferred items with an owner and revisit condition.

In REVIEW mode, return the assessment without editing files. In HARDEN mode, patch only the authorized local specification or its established amendment surface. In DELIVER mode, create the requested output without overwriting history unless explicitly authorized. Do not create implementation code unless separately requested.

## Verdict and completion gate

End with exactly one verdict:

- **READY** — no blocking finding remains, required evidence is present, and the specification is implementation-ready.
- **READY WITH EXPLICIT DEFERS** — no blocking finding remains; every defer names an owner and revisit condition, and none prevents safe implementation.
- **NOT READY** — a structural conflict, missing authority, or missing critical evidence still blocks implementation.

Before a ready verdict, confirm that shared terms, identifiers, schemas, ownership, permissions, lifecycle transitions, failure/recovery behavior, and observability agree across affected components. Every amendment must trace to evidence and dependent checks. Never translate missing evidence into a pass.
