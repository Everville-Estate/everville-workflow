---
name: everville-lesson-learned
description: Analyze a specific code change and extract one or two evidence-grounded, reusable engineering lessons. Use when asked for the lesson, engineering takeaway, or reflection on a bug fix or implementation. Persist globally only when the user explicitly requests it.
---

<!--
  Adapted from softaworks/agent-toolkit (lesson-learned), MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: renamed and narrowed to evidence-grounded lessons;
  global-memory writes require an explicit user request.
-->

# Everville Lesson Learned

Extract the most useful lesson demonstrated by an actual change. Do not force a lesson from trivial work or turn the response into a generic engineering lecture.

## Analyze

1. Determine the requested scope. If none is given, use the feature branch versus its base; on the base branch, use the last five commits.
2. Read the commit messages and diff. For a diff over 500 lines, inspect its stat first, then the most relevant changed files. Do not expand into unchanged code unless it is necessary to understand the change.
3. Identify the single dominant pattern. Use `references/se-principles.md` only as a compact naming aid; use `references/anti-patterns.md` when the change shows a concrete risk.
4. Support every claim with a commit, file, or changed behavior. Report uncertainty when intent is not evidenced.

## Output

```markdown
## Lesson: <specific principle or pattern>

**Evidence:** <the concrete change, with files/commits>
**Lesson:** <one or two sentences>
**Why it matters:** <practical consequence>
**Next time:** <one actionable rule>
```

Add at most one secondary lesson. If the change is routine, say that no durable lesson is supported.

## Global memory is explicit-only

Do not offer, suggest, or perform global persistence by default. Persist only when the user explicitly asks to save the lesson to global memory. Then:

- follow the active host's memory-writing instructions and existing format; do not guess a path or create a parallel memory system;
- save only a short portable rule plus the concrete repo/PR/commit provenance;
- check for an existing equivalent entry and update it instead of duplicating it;
- exclude repo-specific trivia and unverified interpretations.

## Avoid

- catalogs of loosely related principles;
- advice disconnected from the diff;
- more than two lessons;
- negative-only or motivational filler;
- memory writes based on implied consent.
