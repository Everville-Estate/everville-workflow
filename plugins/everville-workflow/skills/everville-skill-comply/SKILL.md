---
name: everville-skill-comply
description: Measure whether a candidate Claude Code skill is invoked under supportive, neutral, and competing prompts. Use after changing a high-stakes skill, when runtime routing may ignore a skill, or when asked whether a skill is actually consulted. Runs bounded `claude -p` plan-mode scenarios against an explicit candidate plugin directory and reports invocation compliance, low-confidence results, inconclusive budget caps, and infrastructure failures separately. This diagnostic does not test hook enforcement or prove full workflow execution.
---

# Everville Skill Comply

Use this harness to test one narrow question: **does Claude invoke the candidate skill when the prompt applies?** It complements paper review by exercising skill discovery and routing under three prompt conditions:

- **Supportive** — explicitly asks for the workflow.
- **Neutral** — ordinary request with no workflow cue.
- **Competing** — plausible pressure to skip or over-apply the workflow.

The harness uses only the Python standard library. It runs `claude -p` in plan mode, loads the candidate with `--plugin-dir`, parses stream JSON, and evaluates declared markers.

## Scope and limits

This is an **invocation diagnostic**, not an enforcement test.

- It can observe `Skill` invocations, tool names, assistant text, and terminal process metadata.
- It does not execute edits, prove that workflow steps completed, or exercise `PreToolUse` hooks.
- Test hooks separately with deterministic unit/integration tests that send representative hook input and assert exit codes and JSON output.
- Do not describe this report as proof that a gate cannot be bypassed.

## Run it

From the marketplace checkout:

```bash
python3 plugins/everville-workflow/skills/everville-skill-comply/scripts/skill_comply.py \
  plugins/everville-workflow/skills/everville-skill-comply/scenarios/unified-workflow.json \
  --plugin-dir plugins/everville-workflow \
  --workdir /path/to/target-everville-repo \
  --dry-run
```

Remove `--dry-run` only after reviewing the printed candidate path, target repo, run count, timeout, and worst-case spend. The defaults are portable:

- `--plugin-dir` defaults to the plugin root containing this script, so a source checkout tests its source and an installed copy tests that exact installed copy.
- `--workdir` defaults to the current directory; pass it explicitly when the current directory is not the target project.
- Bundled scenarios default to three runs. Use at least three conclusive runs per measured level before making a strong claim.

Useful controls:

```bash
# Override stochastic sample size, per-run budget, and process timeout
python3 .../skill_comply.py scenarios.json --runs 5 --budget 1.5 --timeout 240

# Write a machine-readable report. Traces are deleted by default.
python3 .../skill_comply.py scenarios.json --json report.json

# Retain raw temporary traces only for deliberate debugging
python3 .../skill_comply.py scenarios.json --retain-traces
```

Never run the harness merely to validate JSON; `--dry-run` performs schema/path validation without real model spend.

## Scenario format

Scenario files are JSON so no third-party parser is required:

```json
{
  "schema_version": 1,
  "skill": "unified-workflow",
  "budget_usd": 1.5,
  "runs": 3,
  "timeout_seconds": 180,
  "scenarios": [
    {
      "id": "feature-neutral",
      "level": "neutral",
      "prompt": "Add a tested booking server action.",
      "expect": [{"skill": "unified-workflow"}],
      "expect_absent": []
    }
  ]
}
```

Validation rejects unknown fields, duplicate or malformed IDs, invalid levels, empty prompts, invalid markers or text regexes, non-positive runs/budgets/timeouts, missing workdirs, and plugin roots without a `.claude-plugin/plugin.json` manifest (legacy root manifests are also accepted).

Marker kinds:

- `{"skill": "substring"}` — substring in a `Skill` tool input; primary routing signal.
- `{"tool": "ToolName"}` — exact tool name.
- `{"text": "regex"}` — case-insensitive assistant-text regex; use sparingly because prose is less stable.

## Read the report honestly

- **Compliant / non-compliant** are marker verdicts from a conclusive process.
- **Inconclusive** means the budget cap prevented a decision; it is excluded from compliance rates.
- **Infrastructure error** means timeout, launch failure, non-zero exit, malformed terminal trace, or another Claude process error. It is never scored as non-compliance.
- **LOW CONFIDENCE** means fewer than three conclusive samples support at least one measured level. One run is a hint, never a robust result.
- A theater warning requires at least three conclusive supportive and competing runs and a gap of at least 50 percentage points.

Exit status is `0` when no conclusive failure or infrastructure error exists, `1` for non-compliant runs, and `2` for configuration or infrastructure errors. JSON reports retain stderr and exit metadata. Raw trace files are always cleaned unless `--retain-traces` is explicit.

## Anti-patterns

- **Testing an installed cache by accident.** Confirm the printed `--plugin-dir`; point it at the candidate source checkout.
- **Using a personal path in a shared scenario.** Keep workdir out of scenario files and pass it at invocation time.
- **Calling one sample robust.** Require repeated conclusive results.
- **Counting auth/CLI failures as skill failures.** Infrastructure errors are a separate class.
- **Claiming hook enforcement.** Use deterministic hook tests for hooks; this harness measures skill invocation only.
- **Retaining every trace.** Traces may contain project/prompt context; retain only for deliberate debugging and clean them after review.
