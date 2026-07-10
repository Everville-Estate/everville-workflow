# Full Skill Evaluation Report Template

Read this file before a marketplace intake report or whenever the user requests the standard full format.

```markdown
# Skill Evaluation: <name>

## Verdict

- Score: X/130 (Y%)
- Grade: A/B/C/D/F
- Pattern: Mindset/Navigation/Philosophy/Process/Tool/Other
- Knowledge ratio: E:A:R = X:Y:Z (diagnostic estimate)
- Everville Fit: X/10 — Pass/Reject-Adapt
- Runtime boundary: design review only; invocation/execution not measured
- Verdict: <one evidence-based sentence>

## Evidence inspected

- Main skill: <path, lines>
- Required references/scripts/assets: <paths>
- Current spec/validator: <source or unavailable>
- Safe checks run: <commands/results or none>

## Dimension scores

| Dimension | Score | Max | Evidence and reason |
|---|---:|---:|---|
| D1 Knowledge Delta | X | 20 | <file:line evidence> |
| D2 Mindset and Procedures | X | 15 | ... |
| D3 Failure/Anti-pattern Quality | X | 15 | ... |
| D4 Specification and Description | X | 15 | ... |
| D5 Progressive Disclosure | X | 15 | ... |
| D6 Freedom Calibration | X | 15 | ... |
| D7 Design Pattern | X | 10 | ... |
| D8 Practical Usability | X | 15 | ... |
| D9 Everville Fit | X | 10 | ... |

## Critical issues

1. <defect> — <consequence> — <smallest credible correction>

## Top three improvements

1. <highest-leverage correction>
2. <second correction>
3. <third correction>

## Detailed notes

For each dimension below 80%, explain:

- missing/problematic evidence;
- concrete example;
- correction and expected effect.

## Decision-path checks

- Applicable trigger: <result>
- Adjacent non-trigger: <result>
- Failure/fallback: <result>
- Reference-loading path: <result>
- Sensitive/external mutation path: <result or not applicable>

## Acceptance conditions

- <specific blocker and proof needed>
```

Do not fill absent evidence with assumptions. Use “not verified” and adjust D4/D8 accordingly.
