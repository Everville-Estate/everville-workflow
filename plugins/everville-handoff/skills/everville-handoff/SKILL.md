---
name: everville-handoff
description: "Create comprehensive handoff documents for seamless agent session transfers. Triggered when: (1) user requests handoff/memory/context save, (2) context is filling up and work should be checkpointed before a boundary, (3) major task milestone completed, (4) work session ending, (5) user says 'save state', 'create handoff', 'I need to pause', (6) resuming with 'load handoff', 'resume from', 'continue where we left off'. A handoff preserves context across a boundary — checkpoint before context runs low, but don't let it become a reason to stop productive work early. Everville-specific: stores handoffs under .claude/handoffs/ in the repo being worked on so future agents in any Everville project can resume."
---

<!--
  Adapted from softaworks/agent-toolkit (session-handoff) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: renamed to everville-handoff; replaced Python
  scaffolding/validation scripts (create_handoff.py, validate_handoff.py,
  list_handoffs.py, check_staleness.py) with native bash + git + gh recipes;
  description calls out the long-running agent-orchestration use case that
  surfaces across balicopter, portal, and eva work.
-->

# Everville Handoff

Creates handoff documents that let a fresh agent continue work with zero ambiguity — across machines, across agents (Claude Code ↔ Hermes ↔ Codex), across a context boundary, or across a deliberate pause. Use it to checkpoint before context runs low; just don't let it become a reason to wrap up while there's productive work left.

**Scope note:** same-session and same-machine continuation is now covered natively by Claude Code (context summarization + the per-machine auto-memory directory). This skill earns its keep at the boundaries the native mechanisms can't cross: a different machine, a different agent (Hermes/Codex), or a repo-committed checkpoint another teammate will pick up. For a plain "continue tomorrow on this machine" case, native resume is enough — don't create a handoff file out of habit.

## Mode Selection

- **Creating a handoff** — user wants to save state or pause work. Follow **CREATE**.
- **Resuming from a handoff** — user wants to continue previous work or mentions an existing handoff. Follow **RESUME**.
- **Proactive checkpoint** — when context is genuinely getting full, or after substantial work (major milestone, complex debugging resolved, architectural decisions made), create the handoff and report its path in your summary. Offer rather than interrupt: checkpoint at a natural boundary, don't halt active work mid-task to ask.

## CREATE Workflow

### Step 1: Generate the scaffold

```bash
SLUG=${1:-work}
STAMP=$(date +%Y-%m-%d-%H%M%S)
DIR=.claude/handoffs
mkdir -p "$DIR"
FILE="$DIR/${STAMP}-${SLUG}.md"

BRANCH=$(git branch --show-current)
COMMITS=$(git log -5 --oneline)
MODIFIED=$(git status --short)
CWD=$(pwd)

cat > "$FILE" <<EOF
# Handoff: ${SLUG}

**Created:** $(date -Iseconds)
**Project:** $CWD
**Branch:** $BRANCH

## Recent commits
\`\`\`
$COMMITS
\`\`\`

## Modified files
\`\`\`
$MODIFIED
\`\`\`

## Current State Summary
[TODO: what's happening right now, in 2-4 sentences]

## Important Context
[TODO: critical info the next agent MUST know — environment, blockers, half-applied changes, external waits]

## Immediate Next Steps
1. [TODO: first concrete action]
2. [TODO: second]
3. [TODO: third]

## Decisions Made
- [TODO: decision + rationale, not just outcome]

## Critical Files
- path/to/file.ts — [why it matters]

## Key Patterns Discovered
- [TODO: conventions to follow]

## Potential Gotchas
- [TODO: known issues to avoid]

## Pending Work
- [ ] [TODO]

## Continues from
[TODO: previous handoff filename if this is a chain, otherwise "(new)"]
EOF
echo "Handoff scaffold: $FILE"
```

### Step 2: Fill in every `[TODO: ...]`

Prioritize these four sections first:

1. **Current State Summary** — what's happening right now
2. **Important Context** — critical info the next agent MUST know
3. **Immediate Next Steps** — clear, actionable first action
4. **Decisions Made** — choices with rationale (not just outcomes)

See `references/handoff-template.md` for expanded guidance per section.

### Step 3: Validate

```bash
FILE=".claude/handoffs/<stamp>-<slug>.md"
# 1. No [TODO placeholders remain
grep -n "\[TODO:" "$FILE" && echo "FAIL: placeholders remain" || echo "OK"

# 2. No obvious secrets
grep -Ein "api[_-]?key|password|token|secret|bearer|sk_(live|test)_|AKIA[0-9A-Z]{16}" "$FILE" && echo "FAIL: possible secret" || echo "OK"

# 3. All referenced files exist
grep -oE '(\./|plugins/|app/|components/|db/|supabase/)[a-zA-Z0-9_./-]+' "$FILE" | sort -u | while read p; do
  [ -e "$p" ] || echo "MISSING: $p"
done
```

Fail closed: do not finalize a handoff with placeholders, detected secrets, or missing files.

### Step 4: Confirm

Report to the user:
- Handoff file path
- Any validator warnings
- Summary of captured context (3 sentences max)
- First action the next session should take

## RESUME Workflow

### Step 1: List available handoffs

```bash
ls -t .claude/handoffs/*.md 2>/dev/null
```

Most recent first. Title and date are in the filename: `YYYY-MM-DD-HHMMSS-<slug>.md`.

### Step 2: Check staleness

```bash
FILE="$1"
CREATED=$(grep -m1 '^\*\*Created:\*\*' "$FILE" | sed 's/.*Created:\*\* //')
# python3 handles the ISO-8601 colon offset (+08:00) portably; BSD `date -j -f "%z"` does not, and GNU `date -d` doesn't exist on macOS
CREATED_EPOCH=$(python3 -c "import datetime,sys; print(int(datetime.datetime.fromisoformat(sys.argv[1]).timestamp()))" "$CREATED")
NOW=$(date +%s)
AGE_HOURS=$(( (NOW - CREATED_EPOCH) / 3600 ))

COMMITS_SINCE=$(git log --since="$CREATED" --oneline | wc -l | tr -d ' ')
FILES_CHANGED=$(git log --since="$CREATED" --name-only --pretty=format: | sort -u | grep -v '^$' | wc -l | tr -d ' ')

echo "Age: ${AGE_HOURS}h | Commits since: $COMMITS_SINCE | Files changed: $FILES_CHANGED"

if   [ $AGE_HOURS -lt 2 ] && [ $COMMITS_SINCE -lt 3 ]; then echo "FRESH — safe to resume"
elif [ $AGE_HOURS -lt 24 ] || [ $COMMITS_SINCE -lt 10 ]; then echo "SLIGHTLY_STALE — review diff, then resume"
elif [ $AGE_HOURS -lt 168 ]; then echo "STALE — verify context carefully"
else echo "VERY_STALE — consider creating a fresh handoff"
fi
```

### Step 3: Read the handoff completely

Before taking any action. If the handoff has a "Continues from" link, read the predecessor too — you need the full chain.

### Step 4: Verify context

Walk the checklist in `references/resume-checklist.md`:

1. Project directory and git branch match
2. Blockers have been resolved
3. Assumptions still hold
4. Modified files don't conflict with current HEAD
5. Environment state matches

### Step 5: Begin work

Start with **Immediate Next Steps** item #1. Reference "Critical Files", "Key Patterns Discovered", and "Potential Gotchas" as you work.

### Step 6: Update or chain

Long session? Create a new handoff linked to this one:

```bash
SLUG=continuation-1
STAMP=$(date +%Y-%m-%d-%H%M%S)
PREV=.claude/handoffs/<previous>.md
NEW=.claude/handoffs/${STAMP}-${SLUG}.md
# ... same scaffold as Step 1 above, with:
# Continues from
# $PREV
```

## Handoff Chaining

```
2026-04-23-093000-auth.md        (initial)
    ↓  Continues from
2026-04-23-143000-auth-part-2.md
    ↓  Continues from
2026-04-24-090000-auth-part-3.md
```

When resuming from a chain: read the most recent handoff, reference predecessors as needed.

## Storage

`.claude/handoffs/` at the root of the repo being worked on (not in `~/.claude`). This keeps context with the code and is portable across Everville repos.

Naming: `YYYY-MM-DD-HHMMSS-<slug>.md`

## References

- `references/handoff-template.md` — full template structure with guidance per section
- `references/resume-checklist.md` — verification checklist for resuming agents
