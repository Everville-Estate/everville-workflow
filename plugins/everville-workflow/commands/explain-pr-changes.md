---
description: Generate review-ready PR title/body Markdown from the current branch diff without creating a branch, opening or editing a PR, pushing, or changing GitHub state.
argument-hint: "[issue-number-to-close]"
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash(git status *) Bash(git branch *) Bash(git rev-parse *) Bash(git log *) Bash(git diff *) Bash(gh pr view *)
---

<!--
  Adapted from softaworks/agent-toolkit (explain-pr-changes) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: generation-only trust boundary, explicit invocation,
  Why/What/How preservation, dependency-ordered changesets, and Gotchas.
-->

# /explain-pr-changes

Generate a proposed PR title and body from the current branch's existing diff. This command is read-only.

## Hard boundary

This invocation authorizes analysis and Markdown generation only. It does **not** authorize any of the following:

- creating or switching branches;
- committing, pushing, or fetching;
- creating a pull request;
- editing a PR body or title;
- posting comments/reviews;
- merging, closing, or otherwise changing GitHub state.

Never run `gh pr create`, `gh pr edit`, `gh api` with a mutating method, `git push`, or branch-creation commands from this skill. After showing the proposal, the user may separately request publication. Treat that as a new external-write action: confirm the exact target PR and preserve any human-authored content before mutation.

## Inputs

1. Confirm this is a Git worktree and record the current branch and HEAD.
2. If the current branch is `main`, has no commits/diff against `origin/main`, or `origin/main` is unavailable, report the condition and stop. Do not create a branch or fetch automatically.
3. Inspect `git diff --stat origin/main...HEAD`, `git diff origin/main...HEAD`, and relevant commit messages.
4. If `gh` is installed and authenticated, `gh pr view --json number,title,body,url,baseRefName,headRefName` may be used read-only to understand an existing PR. If it is unavailable, continue from local Git evidence and state that existing PR content was not checked.
5. If the local `origin/main` reference may be stale, say so in the generated report; do not silently mutate refs.

## Preserve useful existing content

When an existing PR body is available, grade it on:

- **Why** — the problem, risk, or goal;
- **What** — the actual changes;
- **How** — approach and non-obvious decisions.

Retain accurate human-authored context and make the smallest additions needed. Regenerate from scratch only when no usable body exists. Never overwrite an existing body as part of this command.

## Analyze

Understand the intent and group files into dependency-ordered changesets: foundations first, implementation next, integration/UI after that, then tests and configuration. For each group identify:

- affected files;
- behavior and contract changes;
- exported function signature, schema, global data, migration, or public API effects;
- dependencies and what the group enables;
- verification added or run;
- reviewer gotchas.

Triage each changeset:

- `NEEDS_REVIEW`: any logic, behavior, data, configuration semantics, or public contract changes.
- `APPROVED`: only non-behavioral typo, formatting, comment, or equivalent mechanical edits.

When uncertain, use `NEEDS_REVIEW`.

## Diagrams

Include a small Mermaid diagram only when it materially clarifies changed data flow, call hierarchy, state transitions, or relationships among three or more components. Do not diagram the entire system.

## Output

Return one proposed title followed by one Markdown body in a fenced block. Do not write a file unless the user separately asks for a local artifact. Do not add conversational text inside the body.

````markdown
# PR Summary: [proposed title]

## High-level summary

[Why, what, and how in at most 150 words.]

## Architectural impact

[Optional focused Mermaid diagram and one-sentence explanation. Omit when unnecessary.]

## Detailed changesets

### Changeset 1: [meaningful title]

**Files affected**

- `path/to/file`

**Changes**

- [specific behavior or implementation change]
- Public/API/data impact: [none, or exact impact]

**Depends on:** [nothing or prior changeset]

**Enables:** [later change or outcome]
**Triage:** `NEEDS_REVIEW` or `APPROVED`

## Verification

- `[command]` — [observed result, or "not run"]

## Gotchas and non-obvious details

[Omit when none.]

Close #[issue-number]
````

Include the `Close #...` line only when `$ARGUMENTS` contains a valid issue number. Never infer an issue number from unrelated text.

After the fenced proposal, state:

- whether an existing body was checked and which Why/What/How gaps were filled;
- the diff baseline and HEAD used;
- that no branch, Git remote, PR, title, body, comment, or merge state was changed;
- that publishing requires a separate explicit request naming the target PR.
