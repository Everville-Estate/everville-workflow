# Everville Skill Judge — Scoring Rubric

Read this file completely before assigning scores. The maximum is 130 points: 120 core plus 10 Everville Fit.

## D1. Knowledge Delta — 20

Does the skill add judgment or procedures the model is unlikely to apply reliably without it?

| Score | Evidence |
|---|---|
| 0–5 | Mostly basic definitions, generic tutorials, persona framing, or common best practices |
| 6–10 | Some useful domain content diluted by substantial redundancy |
| 11–15 | Mostly expert decisions, trade-offs, or failure modes with limited repetition |
| 16–20 | Dense, specific knowledge delta; nearly every section changes a real decision |

Check decision trees, non-obvious trade-offs, domain edge cases, and reasons behind constraints. Deduct for background the model already knows.

## D2. Mindset and Domain Procedures — 15

Does it transfer both how an expert thinks and any non-obvious order of operations?

| Score | Evidence |
|---|---|
| 0–3 | Generic mechanical steps only |
| 4–7 | Useful procedures but weak decision principles, or vice versa |
| 8–11 | Good balance of thinking framework and domain procedure |
| 12–15 | Expert reasoning plus precise, consequential sequencing and fallbacks |

Valuable procedure: fragile format or system sequence where ordering matters. Redundant procedure: “open, edit, save, test.”

## D3. Failure and Anti-Pattern Quality — 15

Does it state concrete wrong turns, why they fail, and what to do instead?

| Score | Evidence |
|---|---|
| 0–3 | No failure guidance |
| 4–7 | Vague cautions without consequence or alternative |
| 8–11 | Specific anti-patterns with reasons for common failures |
| 12–15 | Experience-backed landmines, boundaries, and recovery paths |

Exact word “NEVER” is not required. Specificity, consequence, and corrective action are.

## D4. Specification and Description — 15

Does the skill satisfy the current runtime contract and route correctly?

| Score | Evidence |
|---|---|
| 0–5 | Invalid/missing metadata or incompatible package shape |
| 6–10 | Valid basics but vague description, stale commands, or unsupported fields |
| 11–13 | Current format; description explains what and when with useful trigger terms |
| 14–15 | Validated current contract, precise positive/negative routing, no stale runtime claims |

Verify current requirements with first-party docs or the runtime validator when possible. The description should say what the skill does, when it applies, and vocabulary likely to appear in applicable requests. Trigger guidance hidden only in the body cannot help pre-load routing.

## D5. Progressive Disclosure — 15

Does the skill load the right amount of context at the right time?

| Score | Evidence |
|---|---|
| 0–5 | Oversized dump, or critical knowledge stranded in unreferenced files |
| 6–10 | References exist but routes are vague/over-broad |
| 11–13 | Main body is focused; conditional references have explicit loading triggers |
| 14–15 | Clear must-load and do-not-load branches, focused resources, no orphan content |

Main bodies under 500 lines are a guardrail, not a guarantee. A concise body can still be unusable; a justified larger body still pays a context cost. Simple skills may be best self-contained.

## D6. Freedom Calibration — 15

Does specificity match task fragility?

| Score | Evidence |
|---|---|
| 0–5 | Rigid ceremony for creative work or vague advice for fragile operations |
| 6–10 | Several mismatched constraints or missing safety boundaries |
| 11–13 | Mostly appropriate freedom with clear high-risk constraints |
| 14–15 | Constraint level tracks consequence across all paths and fallbacks |

Creative/taste tasks usually need principles and range. File formats, security, data mutation, and production operations need exact checks and narrow freedom.

## D7. Design Pattern — 10

Does structure fit the job rather than imitate a fashionable template?

| Score | Evidence |
|---|---|
| 0–3 | Chaotic structure or no usable task flow |
| 4–6 | Recognizable pattern with significant mismatch |
| 7–8 | Appropriate pattern with minor friction |
| 9–10 | Structure makes routing, decisions, and execution unusually clear |

Use the patterns reference when scoring below 7 or when pattern choice is uncertain.

## D8. Practical Usability — 15

Can an agent successfully act, recover, and verify?

| Score | Evidence |
|---|---|
| 0–5 | Contradictory, incomplete, unsafe, or examples do not work |
| 6–10 | Common path works but important decisions/fallbacks are missing |
| 11–13 | Clear normal path, useful examples, edge cases, and verification |
| 14–15 | Complete decision paths, tested helpers, explicit errors/fallbacks, auditable output |

Check tool availability, dependency declaration, executable examples, path portability, error handling, and observable completion criteria.

## D9. Everville Fit — 10 (hard gate)

Award two points for each:

1. **Project alignment** — guidance matches the target repository’s current stack and conventions, or is deliberately stack-agnostic.
2. **Dependency discipline** — no silent install, unapproved binary/service, credential request, or undeclared runtime dependency.
3. **No persona costume** — adds knowledge rather than “expert/10x” framing or decorative preambles.
4. **Composes with existing workflow** — does not duplicate or contradict installed planning, TDD, review, security, or orchestration capabilities without a named reason.
5. **Respects Everville controls** — preserves secret handling, source-of-truth, review, deployment, and global instruction boundaries relevant to its actions.

| Score | Meaning |
|---|---|
| 0–3 | Wrong marketplace or unsafe fit; reject/adapt regardless of total |
| 4–6 | Fixable fit blockers |
| 7–8 | Minor integration friction |
| 9–10 | Native, compatible fit |

## Grade scale

| Grade | Score | Meaning |
|---|---:|---|
| A | 117–130 | Excellent design; accept unless a named blocker remains |
| B | 104–116 | Good; accept after minor named fixes |
| C | 91–103 | Adequate; fix blockers before acceptance |
| D | 78–90 | Significant rework required |
| F | 0–77 | Fundamental redesign required |

Hard gate: D9 below 4 is Reject/Adapt regardless of total.
