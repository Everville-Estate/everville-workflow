---
name: everville-handoff
description: Create or resume validated repository-local handoffs for explicit cross-machine, cross-agent, or durable checkpoint requests. Stores portable identity as sanitized Git owner/repository plus commit, never environment values, and never commits or shares the file automatically.
---

<!--
  Adapted from softaworks/agent-toolkit (session-handoff) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: portable repository identity, aggregated fail-closed
  validation, commit-ancestry staleness, and explicit sharing boundaries.
-->

# Everville Handoff

Use a handoff when work must cross a machine, agent, teammate, or durable repository boundary. Claude Code's native resume and auto-memory are normally enough for same-machine continuation, so do not create repository files merely because a turn is ending.

## Safety and sharing boundary

- Store handoffs under `.claude/handoffs/` in the repository.
- Record the sanitized `owner/repository`, branch, and commit. An absolute checkout path is not repository identity and should not appear in a portable handoff.
- Record environment variable names and whether setup is required, never values.
- Do not include credentials, session cookies, private URLs containing credentials, customer data, or copied secret-bearing logs.
- Creation is local only. Do not stage, commit, push, upload, or send a handoff unless the user explicitly authorizes that exact sharing action after reviewing the file.
- Before committing a handoff, confirm repository policy allows it and consider whether the content belongs in a private issue or approved vault instead. Never push it automatically.

## CREATE

### 1. Capture portable metadata

Run from the repository root:

```bash
VALIDATOR="${CLAUDE_PLUGIN_ROOT}/skills/everville-handoff/scripts/handoff_validator.py"
SLUG=$(python3 "$VALIDATOR" slug "${1:-work}") || exit 1
STAMP=$(date +%Y-%m-%d-%H%M%S)
DIR=.claude/handoffs
mkdir -p "$DIR"
FILE="$DIR/${STAMP}-${SLUG}.md"
REMOTE=$(git remote get-url origin)
REPOSITORY=$(python3 - "$REMOTE" <<'PY'
import re, sys, urllib.parse
s = sys.argv[1].strip()
if re.match(r'^[^/@]+@[^:]+:', s):
    host, path = s.split(':', 1)
    s = host.split('@', 1)[1] + '/' + path
else:
    parsed = urllib.parse.urlsplit(s)
    if parsed.scheme:
        s = (parsed.hostname or '') + parsed.path
s = s.split('?', 1)[0].split('#', 1)[0].strip('/').removesuffix('.git')
parts = [p for p in s.split('/') if p]
if len(parts) < 2:
    raise SystemExit('cannot derive owner/repository from origin')
print('/'.join(parts[-2:]))
PY
)
BRANCH=$(git branch --show-current)
HEAD_SHA=$(git rev-parse HEAD)
COMMITS=$(git log -5 --oneline)
MODIFIED=$(git status --short)
```

The normalization intentionally drops URL userinfo, query strings, and host-specific checkout syntax so embedded credentials cannot enter the handoff.

### 2. Create and complete the document

Create `$FILE` from `references/handoff-template.md`. Fill every placeholder. At minimum include:

- created time in ISO 8601 with timezone;
- repository (`owner/repository`), branch, and full head SHA;
- current outcome/status in 2–4 sentences;
- exact next action;
- completed and pending work;
- decisions with rationale;
- critical repository-relative files in backticks;
- blockers and external waits without sensitive payloads;
- required environment variable **names** only;
- predecessor filename if this continues a handoff chain.

Do not paste `env`, `.env`, credential-store output, authenticated URLs, or full logs. Summarize errors and link to an approved artifact instead.

### 3. Validate once, fail closed

Run the bundled validator with the real handoff path. It requires the safe filename, title, metadata, every template section, and non-placeholder content; it also aggregates path, reference, and common secret-pattern findings. It exits non-zero if any issue exists:

```bash
python3 "$VALIDATOR" validate "$FILE" --repo-root .
```

Review every reported item. Do not finalize, share, or claim success until the validator exits 0. Pattern checks reduce risk but cannot prove a document contains no sensitive information; perform a human-readable diff review too.

### 4. Report local completion

Report the repository-relative path, validator result, head SHA, and first next action. State explicitly that the handoff is uncommitted/unshared unless the user separately authorized sharing.

## RESUME

### 1. Select and read

```bash
ls -t .claude/handoffs/*.md 2>/dev/null
```

Read the selected handoff completely before acting. Read the direct predecessor when a missing decision or assumption depends on it; do not recursively load an entire chain without need.

### 2. Verify repository identity and staleness

Extract the `Repository`, `Branch`, `Head`, and `Created` fields. Normalize the current origin using the CREATE recipe and require the same `owner/repository`. A mismatch is a hard stop.

Use Git ancestry as the primary staleness signal:

```bash
HANDOFF_HEAD=<full-sha-from-handoff>

if ! git cat-file -e "${HANDOFF_HEAD}^{commit}" 2>/dev/null; then
  echo "UNKNOWN — handoff commit is unavailable; fetch/reconcile before resuming"
elif [ "$(git rev-parse HEAD)" = "$HANDOFF_HEAD" ]; then
  echo "EXACT — repository is at the handoff commit"
elif git merge-base --is-ancestor "$HANDOFF_HEAD" HEAD; then
  COMMITS_SINCE=$(git rev-list --count "$HANDOFF_HEAD..HEAD")
  FILES_CHANGED=$(git diff --name-only "$HANDOFF_HEAD..HEAD" | sed '/^$/d' | wc -l | tr -d ' ')
  echo "ADVANCED — ${COMMITS_SINCE} commits and ${FILES_CHANGED} files changed; reconcile before work"
else
  echo "DIVERGED — handoff head is not an ancestor of current HEAD; stop and investigate"
fi
```

Wall-clock age is supplemental, not the primary verdict. Parse ISO 8601 safely and reject invalid or future timestamps rather than trusting `git log --since`:

```bash
python3 - "$CREATED" <<'PY'
from datetime import datetime, timezone
import sys
raw = sys.argv[1].strip().replace('Z', '+00:00')
created = datetime.fromisoformat(raw)
if created.tzinfo is None:
    raise SystemExit('Created timestamp must include timezone')
hours = (datetime.now(timezone.utc) - created.astimezone(timezone.utc)).total_seconds() / 3600
if hours < -0.05:
    raise SystemExit('Created timestamp is in the future')
print(f'Age: {max(hours, 0):.1f}h')
PY
```

### 3. Reconcile before implementation

Follow `references/resume-checklist.md`. Verify current dirty state, changed critical files, blockers, required services, dependency versions, and environment-variable presence. Check presence without printing values.

If the commit diverged, the repository identity differs, critical files disappeared, or a safety assumption no longer holds, stop and re-establish context rather than following stale next steps.

### 4. Continue or supersede

Begin with the first still-valid immediate next step. If a later durable boundary is needed, create a new handoff with the current head and name the predecessor. Do not edit an old handoff to pretend it represents newer state.

## References

- `references/handoff-template.md` — portable document template
- `references/resume-checklist.md` — reconciliation and secret-safe environment checks
