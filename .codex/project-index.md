# Project Index - Everville Workflow

Stable navigation map. Current resumable task state lives in `.codex/handoff.md`; Git and pull requests retain completed history.

## Runtime Shape

- Public Claude Code plugin marketplace with three separately versioned plugins.
- No application server or production data plane; runtime behavior executes inside Claude Code through skills, agents, and hooks.
- Python is standard-library-only for shipped executable code.

## Primary Entrypoints

- `README.md` - current installation and operating model.
- `.claude-plugin/marketplace.json` - plugin inventory and distribution versions.
- `plugins/*/.claude-plugin/plugin.json` - plugin metadata.
- `plugins/everville-workflow/hooks/hooks.json` - automatic runtime events.
- `scripts/validate_repository.py` - deterministic repository validation.
- `scripts/validate_marketplace_install.sh` - isolated consumer installation and cached-package validation.

## Core Subsystems

- `plugins/everville-workflow/skills/` - change-execution workflow, release, CI, entropy, and lesson guidance.
- `plugins/everville-workflow/skills/everville-spec-hardening/` - proportional REVIEW/HARDEN/DELIVER guidance for existing multi-component or high-risk specifications.
- `plugins/everville-workflow/hooks/` - repository-scoped workflow attention gate.
- `plugins/everville-workflow/agents/` - read-only pattern and CI observers.
- `plugins/everville-meta/` - opt-in marketplace authoring, instruction refactoring, skill-quality, inventory, and compliance-diagnostic tooling.
- `plugins/everville-handoff/` - cross-boundary checkpoint guidance.
- `tests/` - deterministic hook, harness, manifest, and documentation contract tests.
- `docs/` - current design notes; historical proposals live under `docs/archive/`.

## Integrations And Sources Of Truth

- Claude Code component schemas and hook behavior: first-party `code.claude.com` documentation.
- GitHub repository state: `Everville-Estate/everville-workflow`.
- `superpowers` is an external workflow dependency and must be installed or declared unavailable.
- Plugin manifests and marketplace versions must agree; the marketplace is authoritative for distributed inventory.

## Verification

- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `python3 scripts/validate_repository.py`
- `claude plugin validate . --strict`
- `claude plugin validate plugins/everville-workflow --strict`
- `claude plugin validate plugins/everville-meta --strict`
- `claude plugin validate plugins/everville-handoff --strict`
- `scripts/validate_marketplace_install.sh`
- `python3 plugins/everville-meta/skills/everville-skill-comply/scripts/skill_comply.py tests/fixtures/everville-spec-hardening.json --plugin-dir plugins/everville-workflow --workdir . --dry-run`

## Conventions And Boundaries

- Keep executable helpers dependency-free unless the dependency is declared, pinned, and justified.
- Scope automatic behavior to verified Everville repositories.
- Guidance may shape behavior; deterministic policy belongs in tests, CI, permissions, and repository protection.
- Never present SessionStart context or a skill description as an enforcement boundary.
- Do not store task history, blockers, or delivery logs in this index.
