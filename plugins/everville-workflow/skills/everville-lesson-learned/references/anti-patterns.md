---
description: Compact signals for concrete engineering risks visible in a code change.
---

# Anti-Pattern Signals

Use a label only when the diff supplies direct evidence.

| Pattern | Evidence to look for |
|---|---|
| Mixed responsibility | One module changes for unrelated UI, data, and domain concerns |
| Shotgun change | One behavior requires the same coordinated edit across many files |
| Premature abstraction | A generic interface or factory has one real case and no stated constraint |
| Knowledge duplication | The same rule or invariant is independently encoded in several places |
| Hidden policy | An unexplained literal controls retries, limits, permissions, or state |
| Long operation | A function combines several named stages or deeply nested branches |
| Misleading comment | Commentary restates stale behavior instead of recording intent or constraints |

Describe the consequence and the changed evidence, not the label alone. Treat a large file count or line count as a prompt to inspect, not proof of a defect.
