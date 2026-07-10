# Skill Design Patterns and Failure Modes

Read this file when choosing a pattern, diagnosing progressive disclosure, or reviewing a main skill body over 500 lines.

## Common patterns

| Pattern | Best for | Main-body shape | Common failure |
|---|---|---|---|
| Mindset | Creative/taste judgment | Short principles, decision prompts, sharp anti-patterns | Generic inspiration with no domain taste |
| Navigation | Several distinct task families | Small router with explicit conditional references | Orphan references or loading everything |
| Philosophy | Craft where purpose shapes output | Principles followed by an expression workflow | Abstract prose with no actionable decisions |
| Process | Multi-phase, stateful work | Ordered phases, gates, fallbacks, outputs | Checkbox ceremony unrelated to risk |
| Tool | Fragile technical/file operations | Decision tree, exact commands/scripts, validation | Vague advice where one wrong step corrupts output |

Approximate length is not a pattern. Choose based on the decisions and failure consequences.

## Progressive-disclosure test

For each resource, answer:

1. What observable condition requires it?
2. Does the main body tell the agent to read it completely at that decision point?
3. Which adjacent resources should not be loaded for this path?
4. Would missing the resource cause incorrect action, or is it optional background?
5. Does the referenced content duplicate the main body?

A good route looks like:

```markdown
When editing OOXML directly, read `references/ooxml.md` completely before mutation.
Do not load `references/new-document.md`; it applies only to greenfield generation.
```

A file list titled “References” with no decision point is not a loading route.

## Failure modes

### Tutorial

- Symptom: defines common concepts or teaches basic language/library operations.
- Consequence: consumes context without changing expert decisions.
- Correction: keep only non-obvious decisions, constraints, and failure recovery.

### Dump

- Symptom: one very long body mixes routing, philosophy, examples, and every variant.
- Consequence: every invocation pays for irrelevant branches.
- Correction: keep routing/core decisions in the body; move coherent conditional detail into explicitly routed references.

### Orphan references

- Symptom: resources exist but no workflow branch tells the agent when to read them.
- Consequence: critical knowledge is never loaded, or all files are loaded defensively.
- Correction: add condition-specific must-load and do-not-load instructions.

### Checkbox procedure

- Symptom: many generic steps (“open, edit, save”) without consequential ordering.
- Consequence: ceremony masks the absence of domain judgment.
- Correction: preserve only steps whose order, tool, evidence, or failure mode is non-obvious.

### Vague warning

- Symptom: “be careful,” “handle edge cases,” or “use best practices.”
- Consequence: does not change behavior.
- Correction: name the concrete wrong action, consequence, detection, and safer alternative.

### Invisible skill

- Symptom: strong body but a vague description.
- Consequence: routing never loads the body for applicable requests.
- Correction: put what/when/trigger vocabulary and important exclusions in the description.

### Wrong location

- Symptom: triggering information exists only after activation.
- Consequence: it cannot help activation.
- Correction: move routing criteria to metadata; leave execution detail in the body.

### Over-engineered package

- Symptom: auxiliary docs, changelogs, and install guides that do not support runtime behavior.
- Consequence: maintenance surface without agent value.
- Correction: retain only skill instructions and resources required to perform the task.

### Freedom mismatch

- Symptom: exact scripts constrain creative work, or fragile production/data work has only principles.
- Consequence: generic output in the first case, unsafe improvisation in the second.
- Correction: calibrate constraints to consequence of error.

### Runtime theater

- Symptom: forceful words or a paper score are presented as proof the skill is followed.
- Consequence: false operational confidence.
- Correction: separate design review, invocation measurement, deterministic script/hook tests, and full execution evidence.
