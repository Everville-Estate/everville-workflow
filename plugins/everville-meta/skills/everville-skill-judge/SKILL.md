---
name: everville-skill-judge
description: Evaluate a new, modified, vendored, or existing Agent Skill before marketplace acceptance. Use for SKILL.md audits, skill quality reviews, trigger/description problems, progressive-disclosure checks, or intake decisions. Scores nine evidence-based dimensions (120 core points plus 10 Everville Fit points), applies an Everville-fit hard gate, and returns concrete improvements without claiming runtime compliance.
---

<!--
  Adapted from softaworks/agent-toolkit (skill-judge) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: marketplace-fit dimension, evidence protocol,
  current-spec check, and progressive-disclosure references.
-->

# Everville Skill Judge

Evaluate skill **design on paper**. This does not prove that a model invokes or follows the skill at runtime; use `everville-skill-comply` for invocation experiments and deterministic tests for scripts/hooks.

## Required loading route

Before scoring any skill, **read [`references/scoring-rubric.md`](references/scoring-rubric.md) completely**. It is the authoritative 130-point rubric and grade scale.

Then load only what the case needs:

- Read [`references/patterns-and-failures.md`](references/patterns-and-failures.md) completely when selecting a design pattern, diagnosing a score below 11 on D5, below 7 on D7, or when the target is over 500 lines.
- Read [`references/report-template.md`](references/report-template.md) completely before producing a full marketplace intake report or when the user requests the standard report format.
- Do **not** load pattern examples for a concise re-score when the structure is already established.

## Core model

A skill earns context by supplying a useful **knowledge delta**:

- **Expert knowledge** — non-obvious decisions, trade-offs, failure modes, domain procedures, and constraints learned through practice.
- **Activation knowledge** — brief reminders of known behavior that are easy to overlook.
- **Redundant knowledge** — generic tutorials, common operations, persona costume, and repeated background that the model already has.

The objective is not maximum length or polish. It is a routable, usable compression of domain judgment with the right freedom for the consequence of error.

## Evaluation protocol

### 1. Establish scope and current contract

Identify the target `SKILL.md`, its references/scripts/assets, intended runtime, marketplace/project, and whether the review is intake, update, or audit.

For format or runtime claims, verify against current first-party Agent Skills/Claude Code documentation or the runtime’s validator. Do not award compliance points from memory when the contract may have changed. Report unavailable validation explicitly.

### 2. Read the complete target

Read the entire `SKILL.md`. Follow every loading instruction needed to understand the behavior, then inspect referenced executable scripts or templates that affect usability/safety. Record:

- body and reference line counts;
- description/trigger surface;
- required tools/dependencies;
- explicit loading routes and fallbacks;
- conflicts with project/global instructions.

### 3. Classify the knowledge

Mark sections as Expert, Activation, or Redundant and estimate an `E:A:R` ratio. Treat the ratio as diagnostic rather than false precision. Cite representative evidence for each category.

### 4. Score all nine dimensions

Apply the loaded rubric. For each dimension:

1. Cite file/line evidence or state that evidence is missing.
2. Assign a score inside the documented band.
3. Give a one-sentence reason.
4. Name a concrete improvement whenever the score is below maximum.

Do not let attractive formatting compensate for weak triggers, stale commands, unverifiable examples, or missing edge cases. Do not assume every procedure is valuable; separate domain-specific sequencing from generic file operations.

### 5. Test decision paths

Mentally execute at least:

- one normal trigger;
- one adjacent request that should not trigger;
- one failure/fallback path;
- each reference-loading branch;
- any destructive, secret-bearing, or external mutation path.

Run safe validators or script tests when available. A non-running example is a usability defect, not merely a style issue.

### 6. Calculate grade and gate

Sum D1–D9 out of 130 and apply the rubric’s percentage-based grade. If D9 Everville Fit is below 4, verdict is **Reject/Adapt** regardless of total. Otherwise:

- A/B can be accepted subject to named blockers.
- C requires blocker fixes before acceptance.
- D/F requires significant redesign.

A high paper score is not a runtime compliance claim.

### 7. Report actionable findings

Lead with score, grade, fit gate, and verdict. Every critical issue must name the concrete defect, its consequence, and the smallest credible correction. Prioritize at most three improvements before optional detail.

## Reviewer anti-patterns

- Giving points because content looks professional or is long.
- Ignoring token cost, duplicate content, or an oversized main body.
- Treating a body-only “when to use” section as a substitute for a routable description.
- Rewarding references that have no explicit loading path.
- Accepting vague warnings without a concrete failure and reason.
- Calling a skill compliant because its instructions sound forceful.
- Treating an unavailable tool/dependency as if it worked.
- Using a stale fixed stack assumption instead of the target project’s current contract.
- Evaluating this judge against itself as proof of quality; use an independent review if this skill changes.

## Concise output

For a quick audit, return:

```text
Score / grade / Everville-fit gate
Evidence-backed dimension table (D1–D9)
Critical issues
Top three improvements
Runtime claim boundary
```

For a full intake report, load and use the report template.
