# Boundary Review

Use this reference for interfaces where components exchange data, state, authority, or control.

## Map each boundary

Create a compact provider/consumer map. For every exchange, compare:

- identifiers, types, units, optionality, defaults, and version rules;
- ownership of validation and canonical state;
- authentication, authorization, tenancy, and data classification;
- delivery semantics, ordering, deduplication, and idempotency;
- timeout, backoff, retry limits, and terminal failure;
- observability: correlation identifiers, logs, metrics, alerts, and audit records;
- compatibility during rollout, migration, rollback, and mixed-version operation.

Treat names that look alike as unverified until their semantics match. Treat a shared schema as incomplete if lifecycle or ownership differs between its producers and consumers.

## Follow operational sequences

Review the system while it is changing, not only as a static component list. Trace representative sequences across boundaries:

- two actors update related state at nearly the same time;
- one component succeeds after another times out;
- a message or callback is delivered more than once;
- work resumes after a crash or deploy;
- a rollback meets data written by the newer version;
- an operator repairs or replays a failed operation;
- a permission changes while work is in flight.

For each sequence, identify the durable point of no return, the recovery owner, and the evidence an operator uses to distinguish pending, completed, and failed work.

## Classify mismatches

- **Blocking:** the specification can cause unsafe, contradictory, unrecoverable, or non-implementable behavior.
- **Important:** implementation can proceed only with a fragile assumption, missing critical-path test, or unclear operational ownership.
- **Optional:** a bounded improvement that does not undermine correct implementation.

Each finding should cite both sides of the boundary when available. If one side is absent, say which contract is missing rather than manufacturing it.

## Reconcile once

Keep discovery and resolution linked by finding ID. A proposed amendment should name its dependent consumers, tests, operational procedures, and migration considerations. Recheck those ripples after the amendment, then close or retain the finding with an explicit disposition.
