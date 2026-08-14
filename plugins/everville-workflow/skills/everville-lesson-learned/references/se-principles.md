---
description: Compact vocabulary for naming a principle that is directly evidenced by a code change.
---

# Engineering Principle Vocabulary

Use this only to name an observed pattern. Do not enumerate principles that the diff does not demonstrate.

| Principle | Evidence in a change |
|---|---|
| Single responsibility | One module stops owning unrelated reasons to change |
| Separation of concerns | UI, domain logic, data access, or configuration gain a clear boundary |
| High cohesion | Related behavior moves together near its consumers |
| Loose coupling | A dependency is narrowed behind an explicit contract |
| Encapsulation | Internal state or implementation details leave the public API |
| KISS | Indirection or machinery is removed without losing required behavior |
| YAGNI | Speculative behavior or configuration is deleted or deliberately deferred |
| Rule of three | Repetition is kept local until a stable pattern is demonstrated |
| DRY | Repeated knowledge, not merely similar syntax, gains one representation |
| Least surprise | Naming, return values, side effects, or errors match caller expectations |
| Fail fast | Invalid input or configuration is rejected at the earliest reliable boundary |
| Defensive programming | A demonstrated edge case receives explicit handling |
| Measured optimization | Performance work follows evidence rather than intuition |

Prefer a precise domain lesson over a famous label when the label adds no clarity.
