---
name: everville-reduce-entropy
description: Use when an Everville change may add wrappers, helpers, abstractions, dependencies, duplicated paths, or obsolete code, or when the user asks to simplify. Minimize accidental complexity and long-term ownership cost while preserving required behavior, safety, correctness, tests, types, observability, operability, and legitimate additive features. Treat line count as a diagnostic, never an automatic rejection gate.
---

# Everville Reduce Entropy

Optimize the **final ownership burden**, not the size of the patch and not raw lines alone.

The target is the smallest coherent system that fully satisfies required behavior and operational constraints. Deletion is valuable when it removes accidental complexity; addition is justified when it is necessary for correctness, safety, evidence, or a requested capability.

## Load a relevant mindset only when useful

For a non-obvious design trade-off, inspect the frontmatter in `references/` and read the one most relevant file in full. State its principle before applying it. Do not load every reference, and do not delay a simple duplicate-removal decision for philosophical reading.

Useful routes:

- Existing data can replace behavior-heavy abstraction → `references/data-over-abstractions.md`
- A design becomes simpler by separating responsibilities → `references/design-is-taking-apart.md`
- Choosing between familiar convenience and structural simplicity → `references/simplicity-vs-easy.md`
- Deciding whether a capability is expensive to retrofit later → `references/expensive-to-add-later.md`
- Adding another mindset → `references/adding-reference-mindsets.md`

## Decision order

### 1. Fix required constraints

List what the result must preserve or add:

- User-requested behavior and compatibility.
- Correctness, security, privacy, and data integrity.
- Tests and type guarantees that make those properties observable.
- Logging, metrics, failure handling, rollback, and operability required by the risk.
- Framework/repository conventions and explicit compliance requirements.

These are constraints, not entropy to delete. A smaller result that violates one is not simpler; it is incomplete.

### 2. Search for existing coverage

Before adding a helper, wrapper, module, flag, or dependency, inspect nearby patterns and answer:

- Does an existing primitive already own this behavior?
- Can one existing path be extended without creating two sources of truth?
- Is the proposed abstraction backed by multiple real uses, or only imagined flexibility?
- What becomes obsolete if the proposal lands?

Prefer reuse or consolidation when ownership stays clear. Do not force unrelated concepts through one helper merely to reduce count.

### 3. Compare ownership cost

Compare credible options across:

| Dimension | Question |
|---|---|
| Concepts | How many distinct rules must a maintainer understand? |
| Sources of truth | Can behavior drift between files, layers, or flags? |
| Dependencies | Does this add lifecycle, security, or upgrade burden? |
| Change surface | How many places must change for the next likely requirement? |
| Evidence | Are tests/types/observability sufficient to trust the simpler shape? |
| Removal | Which old code, configuration, compatibility path, or dependency can now disappear? |

Use line/file counts as clues to investigate, not as the verdict. Ten explicit lines can be safer and cheaper than a clever two-line abstraction; a necessary feature may legitimately add code.

### 4. Choose and clean up

Choose the option with the lowest total ownership cost that satisfies all constraints. Remove newly obsolete code in the same change when safe. If compatibility or staged migration prevents removal, name the retained path, owner, and removal condition instead of calling the work complete entropy reduction.

## Red flags

- **“Future flexibility” without a named near-term use** — likely speculative surface area.
- **Wrapper that only renames another API** — adds navigation without policy or safety value.
- **Two ways to perform the same operation** — creates drift unless migration is explicit.
- **Deduplication across unrelated concepts** — fewer lines, tighter coupling.
- **Deleting validation/tests/types/logging to improve counts** — hides risk rather than reducing complexity.
- **Fighting framework conventions** — local cleverness becomes institutional maintenance cost.
- **Rejecting every net-additive change** — confuses product capability and necessary safeguards with accidental complexity.

## Output

State the decision compactly:

```text
Required constraints: ...
Existing coverage inspected: ...
Chosen shape: ...
Ownership cost reduced: ...
Necessary additions retained: ...
Obsolete code removed or deferred with condition: ...
```

Bias toward deletion **after** requirements and evidence are protected. The win is a system that is easier to own, not merely a smaller diff.
