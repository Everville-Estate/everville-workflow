# Delivery

Use this reference only when producing or updating an implementation-ready output. Preserve the source specification as history unless the authorized task explicitly identifies it as the canonical file to update.

## Recommended structure

```markdown
# Specification hardening: <scope>

## Baseline
- Canonical sources reviewed
- In-scope components and actors
- Known evidence limits

## Confirmed decisions and invariants
- <decision or invariant, with source>

## Amendments
### SH-001 — <short title> [blocking|important|optional]
- Affected surfaces:
- Evidence:
- Condition and impact:
- Resolution or decision required:
- Dependent checks:
- Disposition: open|resolved|deferred
- Owner or approver, when needed:

## Open decisions
| ID | Decision owner | Options and consequences | Needed by |
| --- | --- | --- | --- |

## Verification obligations
- <contract, scenario, or operational proof>

## Deferred
- <item, owner, and revisit condition>
```

Omit empty sections. Link to repository paths, headings, requirement IDs, schemas, or contract definitions instead of pasting large source passages.

## Amendment rules

- State the new conclusion and the evidence that requires it.
- Prefer the smallest change that restores consistency across all affected surfaces.
- Distinguish required behavior from an illustrative implementation.
- Retain unresolved choices as visible decisions; do not hide them in prose.
- Record concise rationale sufficient for review. Do not store private reasoning or full agent conversations.
- If the user authorized editing, use the repository's established document and review workflow. Otherwise present the amendment set without writing files.

## Compact example

```markdown
### SH-001 — Event identity is not stable [blocking]
- Affected surfaces: order API, event consumer, replay tool
- Evidence: the producer defines identity as `(tenant_id, order_id)` while the consumer deduplicates on `order_id`
- Condition and impact: two tenants reuse an order ID; one valid event is discarded
- Resolution: carry `tenant_id` and deduplicate on the canonical composite identity
- Dependent checks: event schema/version, consumer store, replay query, mixed-version rollout
- Disposition: resolved after all consumers adopt the composite key
```

The example illustrates finding shape, not a default architecture. Derive actual amendments from the reviewed sources.

## Handoff quality

A builder should be able to derive tasks and tests from the amendments without repeating the review. A reviewer should be able to trace every material change back to evidence, see who owns each remaining choice, and identify which checks must be rerun after a decision changes.
