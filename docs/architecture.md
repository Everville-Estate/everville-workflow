# Everville Workflow — Architecture Design

- **Date**: 2026-04-23
- **Author**: niko (with Claude)
- **Status**: Draft for review
- **Owners**: @nikoasta, @balicopter (Andrey), @maslennikov-ig (Igor — IT admin)
- **Repo target**: `Everville-Estate/everville-workflow` (private)
- **Local clone path**: `~/Developer/work/everville-workflow` (per `~/Documents/CLAUDE.md` — code lives under `~/Developer/`, never `~/Documents/`)

---

## 1. Context & Goals

After reading [Igor Maslennikov's "3000 hours in Claude Code" article](https://pikabu.ru/story/3000_chasov_v_claude_code_upakoval_ves_opyit_v_tri_plagina_13825013) and his [Template Bridge plugin](https://github.com/maslennikov-ig/template-bridge), we want to formalise our team's Claude Code workflow into a shared, versioned, multi-user plugin set.

**Goals:**

- Enforce a consistent 11-step development ritual across all Everville projects (epic → close)
- Make E2E testing a first-class verification gate on user-facing work
- Make Context7 the canonical source for library facts (kill stale-memory bugs)
- Track tasks across sessions via Beads (per-repo, git-native)
- Bridge closed Beads epics into long-term auto-memory
- Enable Andrey, Igor, and future team members to install one bundle and adopt the same discipline
- Stay non-forking — install Superpowers + Beads + Template Bridge as upstream deps
- Survive context compaction and session restart with no manual re-priming

**Non-goals:**

- Replace Linear / external trackers (Beads is for AI-driven work, not company project management)
- Build a new agent framework (we use existing Superpowers + Templates)
- Auto-sync personal memory or env vars across users (per-user, never shared)
- Force the workflow on trivial edits (typo fixes, formatting, version bumps — explicit whitelist)

---

## 2. Decisions Summary

| # | Decision | Choice |
|---|----------|--------|
| Q1 | Beads scope | All-in: every active repo gets `.beads/` |
| Q2 | Hook strategy | Global with detection: `[ -d .beads ] && bd prime` |
| Q3 | E2E integration | Both: short rule in CLAUDE.md + dedicated skill |
| Q4 | Memory ↔ Beads bridge | One-way: `bd close` → append to project memory |
| Q5 | Skill rationalization | Audit + archive cold (90-day usage report) |
| Q6 | Per-project CLAUDE.md | Generator skill `project-bootstrap` |
| Q7 | Workflow escape hatches | Explicit trivial whitelist (no AI-judgment loophole) |
| Q8 | Subagent automation | Per-project config in `.beads/config.json` |
| Q9 | Distribution | Private repo in `Everville-Estate` org, multi-plugin marketplace |
| Q10 | Context7 layer | First-class: pinned per-project, pre-warmed by bootstrap, verification gate |

---

## 3. Architecture Overview

### Layered stack

```
┌───────────────────────────────────────────────────────────────────────┐
│                            YOUR TASK                                   │
├──────────┬──────────────────┬────────────┬─────────────┬──────────────┤
│  Beads   │   Superpowers    │  Context7  │  Templates  │  Everville   │
│  WHAT    │   HOW            │  FACTS     │  WHO        │  STACK RULES │
│          │                  │            │             │              │
│ epic     │ brainstorming    │ resolve-id │ template-   │ project      │
│ ready    │ writing-plans    │ query-docs │ catalog     │ bootstrap    │
│ blocks   │ TDD              │ pinned-libs│ 413+ agents │ memory       │
│ close    │ debugging        │ stale-warn │ on-demand   │ tier policy  │
│          │ verification     │ pre-warm   │             │ telegram     │
└──────────┴──────────────────┴────────────┴─────────────┴──────────────┘
   │              │                │             │              │
   └─ beads       └─ superpowers   └─ context7   └─ template-   └─ everville-*
      plugin         plugin           MCP           bridge          plugins
                                                    plugin       (this repo)
```

### The 11-Step Ritual

```
1. EPIC          bd create -t epic "Goal"
2. BRAINSTORM    superpowers:brainstorming
3. PLAN          superpowers:writing-plans   ← tag user-facing sub-tasks "needs E2E"
3.5 CONTEXT7     resolve-library-id + query-docs for each library touched
4. SUB-TASKS     bd create + bd dep add (parent-child / blocks / discovered-from)
5. ISOLATE       superpowers:using-git-worktrees (non-trivial work)
6. IMPLEMENT     bd ready → claim → TDD (RED → verify-fail → GREEN → verify-pass → REFACTOR)
7. E2E           [if user-facing] everville-e2e-discipline:write-spec → run → commit
8. REVIEW        superpowers:requesting-code-review (+ project-configured agents)
9. VERIFY        superpowers:verification-before-completion (unit + e2e + visual + deploy-check)
10. FINISH       superpowers:finishing-a-development-branch
11. CLOSE        bd close <epic-id> --reason "..." → triggers memory-bridge hook
```

**Trivial whitelist (skip ritual)**: typo/comment-only, formatting-only (prettier/eslint --fix), dependency version bumps without API change, doc-only edits in `*.md` / `docs/**`, README badge updates, `.gitignore` / `.vercelignore` additions. Anything else = full 11 steps.

### Project Tiers

Each project is assigned a tier at bootstrap (modifiable in `.beads/config.json`):

| Tier | Definition | Defaults |
|------|------------|----------|
| **1 — Critical** | Production user-facing or aviation/financial; bugs cause real-world harm or revenue loss | Telegram on, full E2E required, auto-dispatch security-auditor + deploy-checker on every verify, visual regression mandatory |
| **2 — Active** | Production but lower-stakes (marketing sites, internal tools); bugs cause friction not harm | Telegram off, E2E recommended, auto-dispatch code-reviewer only, visual regression for marketing surfaces only |
| **3 — Experimental** | Pre-production / spike / MVP / archived-but-alive | Telegram off, E2E optional, no auto-dispatch, manual review |

Tier 1 (current Everville landscape): balicopter, everville-team-portal, eva-agent, portal.everville.estate, bali.villas.
Tier 2: roya.gallery, roya.business, mix.florist, showcase, eva.mba.
Tier 3: pecatu-dev, mancave-inventory, motorsport-track-day-research, archived projects.

---

## 4. Repository Structure

```
everville-workflow/                         ← marketplace root
├── .claude-plugin/
│   └── marketplace.json                    ← lists 4 plugins
├── plugins/
│   ├── everville-workflow/                 ← discipline layer
│   │   ├── .claude-plugin/plugin.json
│   │   ├── CLAUDE.md
│   │   ├── skills/
│   │   │   ├── unified-workflow/SKILL.md
│   │   │   └── trivial-whitelist/SKILL.md
│   │   └── commands/
│   │       └── workflow-status.md
│   │
│   ├── everville-e2e-discipline/           ← user-facing safety net
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   └── e2e-discipline/SKILL.md
│   │   └── agents/
│   │       └── e2e-spec-writer.md
│   │
│   ├── everville-bootstrap/                ← project init + cross-cutting glue
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   ├── project-bootstrap/SKILL.md
│   │   │   └── memory-bridge/SKILL.md
│   │   ├── commands/
│   │   │   ├── bootstrap-project.md
│   │   │   ├── audit-skills.md
│   │   │   ├── audit-context7.md
│   │   │   └── browse-templates.md
│   │   ├── hooks/
│   │   │   ├── beads-detect.sh
│   │   │   ├── memory-bridge.sh
│   │   │   └── telegram-epic-close.sh
│   │   ├── templates/
│   │   │   ├── project-claude-md.template
│   │   │   ├── project-settings.template.json
│   │   │   └── beads-config.template.json
│   │   └── settings.example.json
│   │
│   └── everville-stack/                    ← meta-plugin (bundle installer)
│       ├── .claude-plugin/plugin.json
│       └── README.md
│
├── docs/
│   ├── architecture.md                     ← this design (copy)
│   ├── workflow.md                         ← the 11-step ritual + E2E
│   ├── beads-rollout.md                    ← per-project init guide
│   └── runbook.md                          ← Andrey/Igor onboarding
│
├── CODEOWNERS                              ← @nikoasta @balicopter @maslennikov-ig
├── .github/workflows/
│   └── validate-plugins.yml
└── README.md
```

**Upstream deps (not forked, installed alongside)**: `superpowers`, `beads`, `template-bridge`. Our plugins reference their skills by name (`superpowers:brainstorming`, `template-bridge:unified-workflow`, etc.).

**Install for any team member**:

```bash
claude plugin marketplace add Everville-Estate/everville-workflow
claude plugin install everville-stack@everville-workflow   # full bundle
# or à la carte:
claude plugin install everville-workflow@everville-workflow
claude plugin install everville-e2e-discipline@everville-workflow
claude plugin install everville-bootstrap@everville-workflow
```

---

## 5. Plugin Internals

### 5.1 `everville-workflow` — discipline layer

**Skill: `unified-workflow`**

Extends Template Bridge's flow with E2E gate (step 7) and Context7 prefetch (step 3.5). See "11-Step Ritual" in section 3.

**Skill: `trivial-whitelist`**

Returns `{trivial: bool, reason: string}` when AI consults it on a candidate change. Hard list; no fuzzy AI judgment. Whitelisted change-types listed in section 3.

**Command: `/workflow-status`**

Prints current state for re-orientation after compaction:
- Active epic + status
- `bd ready` output (Ready Front)
- Current branch + worktree
- Last commit
- Pinned Context7 libs freshness

---

### 5.2 `everville-e2e-discipline` — user-facing safety net

**Skill: `e2e-discipline`**

Activates when sub-task tagged "needs E2E". Playbook:
- New project → invoke existing `e2e-setup` skill first
- Existing project → write spec following project's Playwright conventions
- Visual regression required for: `app/(marketing)/`, dashboards, customer-facing flows
- Skip: API-only changes, internal admin tools without UI changes
- Always run on preview deploy URL (deploy-checker integration), not just localhost

**Agent: `e2e-spec-writer`**

Wraps the existing `playwright-tester` agent with niko-stack defaults:
- Supabase cookie-based SSR auth (per `e2e-setup`)
- Screenshot baselines committed to repo
- Storage state reuse for authenticated tests
- Telemetry: writes pass/fail count to `.beads/e2e-history.jsonl`

---

### 5.3 `everville-bootstrap` — project init + cross-cutting glue

**Skill: `project-bootstrap`**

Given a repo path, generates project-level config from detected reality + memory cross-reference. See section 7 for full flow.

**RULE**: detect from lockfile/config, never inherit framework versions from global rules.

**Skill: `memory-bridge`**

Triggered by `bd close` event. On epic closure:
1. Parse last event from `.beads/events.jsonl`
2. Resolve project name from `$PWD` (basename + git remote)
3. Match to `~/.claude/projects/-Users-niko-air/memory/project_<name>.md`
4. Append: `- 2026-04-23 closed epic "<title>" — <reason>`
5. Update MEMORY.md index timestamp on the entry

**Edge cases**:
- No matching memory file → log to `~/.claude/memory-bridge-orphans.log`
- Same-name repo collision → disambiguate by git remote URL hash
- Sub-epic closed → append to parent's project, not separately

**Commands**:

| Command | Purpose |
|---------|---------|
| `/bootstrap-project` | Init or refresh project config in current repo |
| `/audit-skills` | 90-day skill usage report; suggests archive moves |
| `/audit-context7` | Per-project Context7 pin freshness; flags stale pins (>30d) |
| `/browse-templates` | Pass-through to `npx claude-code-templates@latest` |

**Hooks**:

| Hook | Event | Effect |
|------|-------|--------|
| `beads-detect.sh` | SessionStart, PreCompact | Silent `bd prime` if `.beads/` exists |
| `memory-bridge.sh` | PostToolUse (Bash, matches `bd close`) | Append epic summary to project memory |
| `telegram-epic-close.sh` | PostToolUse (Bash, matches `bd close`) | Notify via existing FREDDIE_BOT_TOKEN (opt-in per project) |

**Templates**: `project-claude-md.template`, `project-settings.template.json`, `beads-config.template.json` — variables filled by `project-bootstrap` skill.

---

### 5.4 `everville-stack` — bundle convenience plugin

Empty plugin (no skills/commands/hooks), uses the `dependencies` field in `plugin.json` to pull the other three plugins as a one-command install. Per Claude Code plugin manifest schema, `dependencies` accepts string names or `{name, version}` objects, so `everville-stack` can declare `["everville-workflow", "everville-e2e-discipline", "everville-bootstrap"]`.

**Phase 0 decision**: defer this plugin. Ship one working plugin first (everville-workflow), add others as their content lands. `everville-stack` bundle ships in Phase 2 once all three target plugins exist.

---

## 6. Cross-cutting Concerns

### 6.1 Global hooks added (`~/.claude/settings.json`)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "[ -d \"$PWD/.beads\" ] && command -v bd >/dev/null && bd prime 2>/dev/null || true", "timeout": 5 },
          { "type": "command", "command": "[ -d \"$PWD/.beads\" ] && echo 'WORKFLOW: invoke everville-workflow:unified-workflow before any non-trivial task' || true", "timeout": 2 }
        ]
      }
    ],
    "PreCompact": [
      {
        "matcher": "",
        "hooks": [
          { "type": "command", "command": "[ -d \"$PWD/.beads\" ] && bd prime 2>/dev/null || true", "timeout": 5 }
        ]
      }
    ]
  }
}
```

Both hooks are **silent no-ops** in non-Beads dirs → zero impact on projects that haven't been bootstrapped. Coexists with the existing 8 hooks (different events).

### 6.2 Memory bridge mechanism

```
User: "bd close epic-42 --reason 'Dashboard live'"
    │
    ▼
Beads emits event to .beads/events.jsonl
    │
    ▼
PostToolUse hook (matcher: Bash) — detects `bd close` pattern
    │
    ▼
memory-bridge.sh:
  1. Parse last event from .beads/events.jsonl
  2. Resolve project name from $PWD (basename + git remote check)
  3. Match to ~/.claude/projects/-Users-niko-air/memory/project_<name>.md
  4. Append epic summary line
  5. Update MEMORY.md index timestamp
```

Implementation: bash, <50 lines.

### 6.3 Telegram integration (opt-in per project)

Per-project `.claude/settings.json` adds a PostToolUse hook that detects `bd close.*epic` and curls FREDDIE_BOT_TOKEN. Defaults: yes for tier-1 (balicopter, everville-team-portal, eva-agent, portal.everville.estate, bali.villas), no otherwise.

### 6.4 Secrets / env handling

- Plugin code = no secrets
- `~/.claude/settings.json` references env vars by name (`${FREDDIE_BOT_TOKEN}`, `${NIKO_CHAT_ID}`)
- Each user maintains their own `~/.claude/.env` (not committed, not shared)
- Each user maintains their own `~/.claude/CLAUDE.md` and memory dir
- Plugin distributes only: rules, skills, commands, hooks, templates

---

## 7. Bootstrap Flow + Config Schemas

### 7.1 `/bootstrap-project` flow

```
$ cd ~/Developer/work/balicopter
$ /bootstrap-project
    │
    ▼
1. DETECT (lockfile/config — never trust global defaults)
   ├─ package.json     → Next.js 16.2.2, React 19, TS 5.x
   ├─ supabase/        → tcrrmyodvyqbpccjqnfo, schemas
   ├─ vercel.json      → project ID
   ├─ drizzle.config   → schema location
   ├─ .vercel/project  → linked project
   └─ git remote       → Everville-Estate/balicopter
    │
    ▼
2. RESOLVE MEMORY
   └─ project_balicopter.md found → extract: 88 PRs, aviation-grade, Airtable mirror
    │
    ▼
3. PRE-WARM CONTEXT7
   └─ For each prod dep: resolve-library-id; persist to .beads/context7-libs.json
    │
    ▼
4. PROPOSE config (diff shown)
   ├─ tier: 1
   ├─ telegram: yes
   ├─ e2e_required: yes
   ├─ auto_dispatch: { review: [code-reviewer, security-auditor],
   │                    verify: [deploy-checker, playwright-tester] }
   ├─ trivial_whitelist_extra: ["airtable.tables/*.json schema sync"]
   └─ deploy_method: "vercel-api"
    │
    ▼
5. WRITE FILES (with confirm)
   ├─ ./CLAUDE.md
   ├─ ./.claude/settings.json
   ├─ ./.beads/config.json
   ├─ ./.beads/context7-libs.json
   └─ ./.beads/.gitignore
    │
    ▼
6. INIT BEADS
   $ bd init --project balicopter --type webapp
    │
    ▼
7. NEXT STEPS printed
```

### 7.2 Per-project `CLAUDE.md` template (rendered example)

```markdown
# Balicopter — Project Context

## Stack (auto-detected 2026-04-23)
Next.js 16.2.2 (App Router, proxy.ts middleware), React 19, TS 5.x, Supabase
(bc + airtable schemas in tcrrmyodvyqbpccjqnfo), Drizzle, Tailwind v4,
Vercel (prj_xxx), Airtable mirror (appyDv59zhdxNELHW)

## Tier: 1 (Aviation — maximum care, verify everything)

## Auto-Dispatch
- Code review: code-reviewer + security-auditor
- Verification: deploy-checker + playwright-tester
- E2E required: yes (dashboards, schedule, bookings, public booking page)

## Project-Specific Rules
- Never deploy without spidertracks/cognito sanity check
- Airtable schema changes require parallel ./airtable.tables/ JSON update
- Never push without `npm run typecheck && npm run e2e:smoke`

## Key Files
- supabase/migrations/    — append-only
- airtable.tables/        — Airtable schema mirror (17 tables)
- src/app/(dashboard)/    — admin dashboards (E2E required)
- src/app/(public)/       — booking page (E2E + visual regression)

## Context7 — Pinned Library Docs (refresh by 2026-05-23)
- Next.js 16.2.2  → /vercel/next.js/v16.2.2
- React 19        → /facebook/react/v19
- Supabase SSR    → /supabase/supabase
- Drizzle ORM     → /drizzle-team/drizzle-orm
- Tailwind v4     → /tailwindlabs/tailwindcss/v4
- Zod 4           → /colinhacks/zod/v4
- Playwright      → /microsoft/playwright

RULE: query Context7 BEFORE writing any code that uses these libraries.
Never trust training-data memory for API surface.

## Reference
- Memory: project_balicopter.md, project_balicopter_airtable.md
- Refs: reference_vercel_deploy.md, reference_spidertracks_api.md
```

### 7.3 `.beads/config.json` schema

```json
{
  "project": "balicopter",
  "tier": 1,
  "type": "webapp",
  "telegram_notifications": true,
  "e2e_required": true,
  "auto_dispatch": {
    "review": ["code-reviewer", "security-auditor"],
    "verify": ["deploy-checker", "playwright-tester"]
  },
  "milestones": [],
  "epic_close_hooks": ["memory-bridge", "telegram"]
}
```

### 7.4 `.beads/context7-libs.json` schema

```json
{
  "resolved_at": "2026-04-23",
  "stale_after_days": 30,
  "libs": {
    "next":             "/vercel/next.js/v16.2.2",
    "react":            "/facebook/react/v19",
    "@supabase/ssr":    "/supabase/supabase",
    "drizzle-orm":      "/drizzle-team/drizzle-orm",
    "tailwindcss":      "/tailwindlabs/tailwindcss/v4",
    "zod":              "/colinhacks/zod/v4",
    "@playwright/test": "/microsoft/playwright"
  }
}
```

---

## 8. Context7 Layer Details

### 8.1 Workflow integration

Step 3.5 (post-plan, pre-implementation):
- For each library named in the plan, call `resolve-library-id` then `query-docs`
- Cache results in current session context
- For pinned libs (already in `.beads/context7-libs.json`), skip resolve step — go straight to `query-docs`

### 8.2 Verification gate

`unified-workflow:verification-before-completion` extension:

For PRs that touch framework/library code → check `git log` of feature branch for at least one Context7 query event recorded in `.beads/events.jsonl`. If absent → block "done" claim with: *"No Context7 query in this branch. Did you implement from memory?"*

### 8.3 Why this matters

Existing memory has 5+ feedback entries that are essentially "training-data was wrong about library X" (`feedback_eslint10_blocked.md`, `feedback_nextjs16_proxy_intercepts_api.md`, `feedback_postgrest_fk_ambiguity.md`, etc.). Context7 layer is the systemic fix — those entries become unnecessary because Claude never relies on memory for library facts.

---

## 9. Rollout Plan

### Phase 0 — Foundation (1 session, ~2h)

- Create `Everville-Estate/everville-workflow` repo
- Bootstrap `marketplace.json` + 4 `plugin.json` files
- Write all skills, commands, hooks, templates
- CODEOWNERS: @nikoasta, @balicopter, @maslennikov-ig
- `.github/workflows/validate-plugins.yml` (lint plugin schemas, shellcheck hooks)
- Push, install on niko's laptop, smoke-test

### Phase 1 — Niko self-pilot (3-7 days)

- Install superpowers + beads + template-bridge + everville-stack
- Update global `~/.claude/CLAUDE.md` (Next.js 14+ → Next.js 16+, append workflow rule)
- Merge SessionStart + PreCompact hooks
- Run `/audit-skills` → archive cold marketplaces
- Run `/bootstrap-project` on **balicopter** (tier 1 pilot)
- Execute one real epic end-to-end through 11-step ritual
- File friction as Beads tasks against everville-workflow repo
- Iterate on plugin

### Phase 2 — Tier-1 rollout (1 week)

- `/bootstrap-project` on:
  - everville-team-portal
  - eva-agent
  - portal.everville.estate
  - bali.villas
- Update each project's memory entry with bootstrap output
- Verify hooks don't conflict with existing project hooks

### Phase 3 — Andrey & Igor onboarding (after Phase 2 stable)

- Igor (IT admin): grant org-level perms on everville-workflow repo
- Andrey (`balicopter` handle): runbook walkthrough at `docs/runbook.md`
- Each installs marketplace + everville-stack
- Each writes their own `~/.claude/CLAUDE.md` (per-user)
- Each runs `/bootstrap-project` on their active repos
- TG channel for plugin issues

### Phase 4 — Tier-2 rollout (when capacity allows)

- Remaining active projects (roya.gallery, roya.business, mix.florist, showcase, pecatu-dev, etc.) at lower tier
- Archived projects: skip

---

## 10. Testing Strategy

### Plugin CI (`.github/workflows/validate-plugins.yml`)

| Layer | What | How |
|-------|------|-----|
| Schema | All `plugin.json` + `marketplace.json` valid | `ajv-cli` against Anthropic schema |
| Markdown | All SKILL.md have valid frontmatter | yaml-lint + custom checker |
| Hooks | All `.sh` files pass shellcheck | `shellcheck hooks/*.sh` |
| Commands | All command markdown loadable | dry-run install in CI |
| Templates | `project-claude-md.template` renders cleanly | render against fixtures |

### Manual workflow tests (during Phase 1)

| Test | Pass criteria |
|------|---------------|
| Fresh session in Beads project | `bd prime` runs silently, workflow reminder echoes |
| Fresh session in non-Beads project | No errors, no echo |
| Compact mid-session | Beads context re-injected after compact |
| `bd close epic-N` | Memory bridge appends to correct `project_*.md` |
| `/bootstrap-project` on existing project | Diffs shown, no destructive overwrite |
| `/bootstrap-project` re-run | Detects existing config, asks before changing |
| Trivial change (typo in README) | Whitelist skips full ritual |
| Non-trivial change (new feature) | Full 11-step enforced |
| Context7 query happens before library code | Logged in `.beads/events.jsonl` |
| Telegram fires on epic close (tier-1) | Notification arrives |
| Auto-dispatch fires correct agents per tier | Agents run at right step |

### Rollback plan

1. `claude plugin disable everville-stack@everville-workflow`
2. Remove SessionStart/PreCompact hook entries from `~/.claude/settings.json`
3. Beads stays installed; `.beads/` per project preserves task history
4. Memory entries stay (append-only)

---

## 11. Success Criteria & Risks

### Success criteria (judge after 4 weeks of Phase 1+2)

- ≥ 80% of non-trivial commits in piloted repos went through the 11-step ritual
- Memory project entries gained ≥ 1 epic-close summary per active project
- Zero hook-conflict incidents reported
- Andrey successfully onboarded at end of Phase 3 with < 30 min handholding
- ≥ 1 instance where Context7 query caught a stale-memory bug pre-implementation
- `/audit-skills` resulted in ≥ 20 skills archived

### Risks

| Risk | Mitigation |
|------|------------|
| Beads becomes new YAGNI bloat (per `feedback_overengineering.md`) | Trivial whitelist hard-prevents ritual on small work |
| Hooks slow down session start (8 already) | All new hooks have `[ -d .beads ]` short-circuit, <50ms total |
| Memory bridge appends garbage to memory files | Dry-run flag for first month; review log; tighten match logic |
| Andrey's setup diverges (different OS, Claude version) | Plugin is markdown + bash; broadly portable. Runbook calls out compat |
| Igor's Template Bridge gets a breaking update | We don't fork — we install alongside; pin version if it breaks |
| Context7 MCP downtime blocks workflow | Step 3.5 has fallback: warn but allow proceed; verification flags it post-hoc |
| Telegram spam on rapid epic closures | Rate-limit hook to 1 notification / 5 min per project |

---

## 12. Open Questions / Follow-ups

- [ ] Confirm `bd init` is idempotent (tested with one project before Phase 2)
- [ ] Decide: do per-project hooks need their own audit log, or piggyback on global `bash-audit.log`?
- [ ] `validate-plugins.yml`: do we want plugin-install smoke test in CI (requires Claude binary in CI)?
- [ ] Memory bridge: append to what file when project name doesn't match any `project_*.md`? (current plan: orphan log; alternative: auto-create skeleton entry)
- [ ] Should `/audit-context7` actually re-resolve stale pins, or just report? (current plan: report, ask before re-resolve)
- [ ] Define "user-facing" precisely for E2E tagging — heuristic vs. explicit annotation?

---

## 13. References

- Article: [3000 hours in Claude Code (Igor Maslennikov, 2026-03-27)](https://pikabu.ru/story/3000_chasov_v_claude_code_upakoval_ves_opyit_v_tri_plagina_13825013)
- Plugin: [maslennikov-ig/template-bridge](https://github.com/maslennikov-ig/template-bridge)
- Plugin: [obra/superpowers](https://github.com/obra/superpowers)
- Plugin: [steveyegge/beads](https://github.com/steveyegge/beads)
- Templates: [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates)
- Existing memory index: `~/.claude/projects/-Users-niko-air/memory/MEMORY.md`
