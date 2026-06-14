---
name: everville-plugin-forge
description: Create and manage Claude Code plugins in the everville-workflow marketplace. Use when scaffolding a new plugin, adding components (commands, skills, agents, hooks) to an existing plugin, bumping plugin versions, scouting whether a skill already exists before creating one, or auditing/linting plugin.json / marketplace.json / SKILL.md frontmatter before release.
---

<!--
  Adapted from softaworks/agent-toolkit (plugin-forge) — MIT licensed.
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: renamed to everville-plugin-forge; replaced Python
  scaffolding scripts (create_plugin.py / bump_version.py) with native
  `claude plugin` CLI commands + short bash recipes; wired to the specific
  everville-workflow marketplace layout.
-->

# Everville Plugin Forge

Build and maintain plugins inside the `Everville-Estate/everville-workflow` marketplace. Covers the manifest schemas, the directory layout, and the workflows for adding, updating, testing, and releasing plugins.

## When to Use

- Creating a new plugin under `plugins/<name>/`
- Adding or modifying components (commands, skills, agents, hooks, MCP servers)
- Bumping `version` in both `plugin.json` and `marketplace.json` before release
- Auditing manifests before `claude plugin validate`
- Vendoring an external MIT-licensed skill (add attribution header + `LICENSES/<source>-MIT.txt`)

## Marketplace Layout

```
everville-workflow/
├── .claude-plugin/
│   └── marketplace.json              # registers every plugin
├── LICENSES/                          # third-party attributions
│   └── softaworks-MIT.txt
└── plugins/
    └── <plugin-name>/
        ├── .claude-plugin/plugin.json
        ├── CLAUDE.md                  # plugin-level rules (loaded on enable)
        ├── skills/<name>/SKILL.md
        ├── skills/<name>/references/
        ├── agents/<name>.md
        ├── commands/<name>.md
        └── hooks/hooks.json
```

## Workflows

### 0. Scout before you create

The cheapest skill is the one you don't write. Before scaffolding anything, check whether the need is already met:

```bash
# Local marketplace + installed skills
grep -rl -i "<the capability>" plugins/*/skills ~/.claude/skills 2>/dev/null
```

Also check the team's other surfaces (the `everville-core` KB, sibling marketplaces) and, for a genuinely new capability, public skill sources. If a match exists, extend or compose with it instead of duplicating — run `everville-skill-stocktake` if you suspect the new idea overlaps something already shipped. Only scaffold when nothing covers the need.

**Vetting an external match before adopting it:** read its SKILL.md in full for surprises — shell commands it runs, network calls, credential access. Copy it to a branch and diff against what you'd have written before trusting it. Never wire an unread external skill into the workflow.

### 1. Scaffold a new plugin

```bash
NAME=my-plugin
mkdir -p plugins/$NAME/.claude-plugin plugins/$NAME/skills plugins/$NAME/commands plugins/$NAME/agents

cat > plugins/$NAME/.claude-plugin/plugin.json <<JSON
{
  "name": "$NAME",
  "version": "0.1.0",
  "description": "...",
  "author": {
    "name": "Everville Estate PTE LTD",
    "email": "niko@everville.estate",
    "url": "https://github.com/Everville-Estate"
  },
  "homepage": "https://github.com/Everville-Estate/everville-workflow",
  "repository": "https://github.com/Everville-Estate/everville-workflow",
  "license": "MIT",
  "keywords": ["everville"]
}
JSON
```

Then register it in `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-plugin",
  "source": "./plugins/my-plugin",
  "description": "...",
  "version": "0.1.0",
  "author": { "name": "Everville Estate PTE LTD" }
}
```

### 2. Validate before pushing

```bash
claude plugin validate plugins/<name>           # plugin manifest
claude plugin validate .                         # marketplace manifest
```

Both must pass before commit. Warnings on SKILL.md frontmatter usually mean the YAML block isn't the very first thing in the file — never put HTML comments or blank lines above `---`.

`claude plugin validate` checks manifest structure but does not parse every SKILL.md's YAML. Run this mechanical lint too — it catches a malformed frontmatter block (bad indentation, missing `name`/`description`, a stray tab) that the model wouldn't spot by eye:

```bash
python3 - <<'PY'
import glob, yaml, sys
bad = 0
for f in glob.glob('plugins/**/SKILL.md', recursive=True):
    src = open(f).read()
    if not src.startswith('---'):
        print(f"FAIL {f}: frontmatter must be the first thing in the file"); bad += 1; continue
    try:
        fm = yaml.safe_load(src.split('---', 2)[1])
    except yaml.YAMLError as e:
        print(f"FAIL {f}: invalid YAML — {e}"); bad += 1; continue
    for key in ('name', 'description'):
        if not fm.get(key):
            print(f"FAIL {f}: missing '{key}'"); bad += 1
print('OK' if not bad else f'{bad} problem(s)'); sys.exit(1 if bad else 0)
PY
```

### 3. Bump version

Version lives in **two** places and both must match:

1. `plugins/<name>/.claude-plugin/plugin.json` → `version`
2. `.claude-plugin/marketplace.json` → the matching `plugins[]` entry's `version`

Semver:
- **major** — breaking change (skill renamed, argument-hint changed, hook signature changed)
- **minor** — added component, new functionality, adapted upstream source
- **patch** — doc fix, description tweak, inline typo

### 4. Refresh local cache

Claude Code caches by version. After pushing a new version:

```bash
claude plugin marketplace update everville-workflow
claude plugin update <plugin-name>@everville-workflow
```

Verify the cache has the new version:

```bash
ls ~/.claude/plugins/cache/everville-workflow/<plugin-name>/
```

### 5. Vendor an external skill

When adapting an MIT-licensed skill from another marketplace:

1. Copy source to `plugins/<plugin>/skills/<renamed>/SKILL.md`
2. Add a **new** frontmatter block with the Everville name + description (do NOT keep the upstream `name`)
3. Add an HTML comment *below* the frontmatter attributing the source
4. Copy the upstream `LICENSE` to `LICENSES/<source>-MIT.txt` (once per source, shared across all adopted items)
5. Run `claude plugin validate plugins/<plugin>` — frontmatter must still be parsed correctly

## Component Formats

| Component | Location | Format |
|-----------|----------|--------|
| Commands | `commands/<name>.md` | YAML frontmatter (`description`, `argument-hint`) + markdown body |
| Skills | `skills/<name>/SKILL.md` | YAML frontmatter (`name`, `description`) + markdown body; optional `references/` directory |
| Agents | `agents/<name>.md` | YAML frontmatter (`name`, `description`, `tools`, `model`) + markdown body |
| Hooks | `hooks/hooks.json` | Object keyed by event name (`session_start`, `before_tool_use`, etc.) |
| MCP Servers | `.mcp.json` at plugin root | Standard MCP server config |

## Command Naming

Commands can namespace via subdirectory:

- `commands/foo.md` → `/foo`
- `commands/build/sync.md` → `/build:sync`

## Git Hygiene

Use the standard Claude Code commit trailer:

```
<conventional commit message>

Co-Authored-By: Claude <noreply@anthropic.com>
```

(The model in use sets its own co-author name under `noreply@anthropic.com`. The old Happy-engineering trailer block is retired.)

## Reference Docs

| Reference | Content |
|-----------|---------|
| `references/plugin-structure.md` | Directory layout, manifest schema, component formats |
| `references/marketplace-schema.md` | Marketplace format, plugin entries, distribution |
| `references/workflows.md` | Step-by-step patterns for adding, updating, testing, publishing |
