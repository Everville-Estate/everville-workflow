# Handoff template

Use repository-relative paths. Complete every bracketed placeholder before validation.

````markdown
# Handoff: <TASK_TITLE>

**Created:** <TIMESTAMP_WITH_TIMEZONE>
**Repository:** <OWNER_REPOSITORY>
**Branch:** <GIT_BRANCH>
**Head:** <FULL_HEAD_SHA>
**Continues from:** <PREDECESSOR_OR_NONE>

## Current state

<CURRENT_STATE>

## Verification at checkpoint

- `<COMMAND>` — <OBSERVED_RESULT>

## Recent commits

```text
<RECENT_COMMITS>
```

## Working tree

```text
<WORKING_TREE_STATUS>
```

## Work completed

- [x] <COMPLETED_OUTCOME>

## Immediate next steps

1. <FIRST_ACTION>
2. <SECOND_ACTION>

## Decisions and rationale

| Decision | Rationale | Alternatives rejected |
| --- | --- | --- |
| <DECISION> | <RATIONALE> | <ALTERNATIVES> |

## Critical files

- `<REPOSITORY_RELATIVE_PATH:LINE>` — <RELEVANCE>

## Blockers and external waits

- <BLOCKER_OR_WAIT>

## Environment requirements

- `<VARIABLE_NAME>` — <REQUIREMENT_AND_PURPOSE>
- <SERVICE_OR_PROCESS> — <SAFE_VERIFICATION>

## Assumptions and gotchas

- <ASSUMPTION_AND_RECHECK>
- <NON_OBVIOUS_RISK>

## Pending and deferred

- [ ] <PENDING_WORK>
- Deferred: <ITEM> — <REASON>

## Sharing status

Local only; not staged, committed, pushed, uploaded, or sent.
````

If the user later authorizes sharing, update the final status only after the exact action succeeds. Do not include a local absolute path, environment value, authenticated URL, copied cookie, token, customer data, or secret-bearing log.
