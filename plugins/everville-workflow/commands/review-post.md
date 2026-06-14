---
description: Post review findings onto the current branch's GitHub PR as one atomic review — severity-tagged inline comments plus an APPROVE/REQUEST_CHANGES/COMMENT verdict, de-duped against existing comments.
argument-hint: "[pr-number]"
---

# /review-post

Land the findings from the REVIEW step (step 8 of `unified-workflow`) onto the GitHub PR as a single formal review. Run after a verifier/reviewer pass has produced severity-tagged findings (🔴 Blocker / 🟠 Should-fix / 🟡 Nice-to-have / 🔵 Nit).

## Severity → verdict

- Any 🔴 Blocker or 🟠 Should-fix present → `REQUEST_CHANGES`
- Only 🟡 Nice-to-have / 🔵 Nit → `COMMENT`
- Zero findings → `APPROVE`

## Process

### 1. Resolve the PR

```bash
PR=${1:-$(gh pr view --json number -q .number)}
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
HEAD_SHA=$(gh pr view "$PR" --json headRefOid -q .headRefOid)
```

If no PR is open for the branch, stop and tell the user to open one (or run `/explain-pr-changes` first).

### 2. De-dup against existing comments

Fetch what's already on the PR so a re-run doesn't repost the same notes:

```bash
gh api "repos/$REPO/pulls/$PR/comments" --paginate -q '.[] | "\(.path):\(.line)\t\(.body)"' > /tmp/existing-review-comments.txt
```

Drop any finding whose (path, line, gist) already appears. Prefix every comment you post with `🤖 ` so bot comments stay distinguishable from human ones.

### 3. Post one atomic review

Build a single request with all inline comments plus the verdict — one call, not N:

```bash
gh api "repos/$REPO/pulls/$PR/reviews" -X POST --input - <<'JSON'
{
  "commit_id": "$HEAD_SHA",
  "event": "REQUEST_CHANGES",
  "body": "<one paragraph: count per severity, the verdict, and why>",
  "comments": [
    { "path": "app/foo.ts", "line": 42, "body": "🤖 🔴 **Blocker** — <finding + concrete fix>" }
  ]
}
JSON
```

- `line` is the line in the file's new version (RIGHT side). For a multi-line span use `start_line` + `line`.
- A comment on a line outside the diff is rejected — keep inline comments on changed lines and put anything else in the review `body`.

### 4. Report

Tell the user the verdict, the count per severity, and the PR review URL. Don't re-paste every comment.

## Guardrails

- This posts a review **as the authenticated `gh` user**. On your own branch, `REQUEST_CHANGES` is fine; don't auto-request-changes on someone else's PR without the user's go.
- Never put secrets or full file contents in a comment.
