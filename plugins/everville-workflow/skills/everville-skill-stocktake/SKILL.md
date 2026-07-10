---
name: everville-skill-stocktake
description: Use to audit the everville-workflow marketplace (or a project's installed skills) for rot, overlap, and drift — when skills have accumulated, two skills seem to do the same thing, a skill references retired infrastructure, or the user asks "which skills should we keep / merge / retire". Emits a Keep/Improve/Update/Retire/Merge verdict per skill, each with a decision-enabling reason. Pairs with everville-skill-judge (scores one skill) and everville-reduce-entropy (deletion bias). Read-only audit — never deletes without explicit confirmation.
---

# Everville Skill Stocktake

`everville-skill-judge` scores **one new skill at intake**. This audits the **whole standing set** for what intake can't see: two skills that have drifted into doing the same job, a skill that references infrastructure we retired, a skill nobody's invoked since it was written. A marketplace rots silently — nothing flags overlap until you trip over it.

## Two modes

- **Quick scan** — only skills changed since a ref (`git diff --name-only <ref> -- '**/SKILL.md'`). Default after a release.
- **Full stocktake** — every skill in the marketplace (or `~/.claude/skills` + plugin skills for a project). Run periodically, not every session.

## Method

1. **Enumerate** the skills in scope and group by plugin. For a full run, list them first so the work is resumable.
2. **Choose the review engine.** When subagents are available and authorized, dispatch an independent verifier per skill (or small batch) in parallel. Each verifier runs `everville-skill-judge` and returns the score plus dimension evidence. When subagents are unavailable, use the local fallback below; lack of subagents must not block the audit.
3. **Detect overlap across the set** — this is the part a single-skill judge can't do. Cluster by what the skill *acts on* (PRs, skills, prose, migrations, agents). Two skills in the same cluster with overlapping triggers are a Merge candidate; flag the pair, don't judge them in isolation.
4. **Assign one verdict per skill** (below), each with a decision-enabling reason.
5. **Report, then stop.** This skill never edits or deletes. Retire/Merge actions happen only after the user signs off; run `everville-reduce-entropy` to execute the deletion bias once they do.

## Verdicts

| Verdict | Means |
|---|---|
| **Keep** | Earning its place; no action |
| **Improve** | Stays, but has a named D-score gap to fix (cite the dimension) |
| **Update** | Content references retired infra, a renamed command, or a stale stack assumption |
| **Retire** | No longer needed; nothing depends on it; remove |
| **Merge → X** | Overlaps skill X; fold the unique part into X and retire this one |

Where the boundaries fall: a low judge score *alone* is **Improve**, not Retire — a weak skill that's still the only thing covering its need gets fixed, not removed. **Retire** requires that nothing depends on it *and* its need is gone or covered elsewhere. **Merge** requires a same-cluster sibling with overlapping triggers to fold into. **Update** is for a skill that's fine in design but cites retired infra or a renamed command. When two apply, prefer the less destructive (Improve/Update over Retire/Merge) unless the overlap is exact.

## The reason rule (the whole point)

A verdict is worthless without a reason that lets someone act without re-investigating. **Banned reasons:** "superseded", "overlaps", "low quality", "redundant" — these name a conclusion, not a cause.

Every reason must state **(1) the specific defect** and **(2) what covers the same need instead**:

- ❌ "Retire — superseded."
- ✅ "Retire — its only trigger ('generate PR body') is fully handled by `/explain-pr-changes`, which also grades the existing body; nothing references this skill."
- ❌ "Merge — overlaps some-prose-skill."
- ✅ "Merge → some-prose-skill — both fire on 'write copy'; this one's only unique content is the email-subject-line checklist, which should move into some-prose-skill's quick-checklist."

## Output

```
## Skill Stocktake — <marketplace/project>   Mode: <quick|full>   Skills: N
Review engine: <independent subagents | local fallback>

| Skill | Score | Verdict | Reason (defect + replacement) |
|-------|-------|---------|-------------------------------|
| ...   | NN/130| Merge→X | ...                           |

### Overlap clusters
- <cluster>: skillA, skillB — <which to merge into which, and why>

### Proposed actions (require confirmation before any delete)
- Retire: ...
- Merge: ...
```

## Local fallback (no subagents)

Process deterministic, small batches locally:

1. Snapshot the full skill inventory and assign stable alphabetical batches of at most five.
2. For each skill, read it and its required references cold, run `everville-skill-judge`, and write the score/evidence row before opening the next skill.
3. After all individual rows exist, make a separate cross-set pass for trigger overlap, retired infrastructure, and dependency relationships.
4. Label the report `Review engine: local fallback`. Do not describe the result as independent or fresh-context review.
5. If context is becoming unreliable, stop at a batch boundary and return the completed inventory/rows plus the exact next batch. A resumable partial audit is better than invented scores.

The same evidence and reason rules apply. The fallback changes review independence, not the verdict standard.

## Anti-patterns

- **Judging overlap one skill at a time.** Overlap is a property of pairs; the single-skill judge will pass both. Cluster first.
- **Lazy reasons.** "Superseded" sends the next person back to square one. Name the defect and the replacement, every time.
- **Deleting in the same breath as deciding.** Stocktake proposes; the user disposes. No `rm`, no PR-to-delete, until they say go.
- **Running a full stocktake every session.** It's a periodic audit, not a per-task gate. Quick-scan after a release; full run occasionally.
- **Claiming local fallback is independent.** It is a continuity mechanism when subagents are unavailable; label it honestly.
