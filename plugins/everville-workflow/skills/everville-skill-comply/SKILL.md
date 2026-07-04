---
name: everville-skill-comply
description: Use to measure whether a skill is actually obeyed at runtime — especially when the prompt competes against it — rather than judged on paper. Runs scenarios through `claude -p` in plan mode inside a real Everville repo, classifies whether the expected skills fired, and reports a compliance rate per competition level. Use when you suspect a skill is being ignored, after editing a high-stakes skill (unified-workflow, trivial-whitelist, a gate), or to answer "does our ritual actually get followed?". Complements everville-skill-judge (scores design on paper) and everville-skill-stocktake (audits the set); this one tests behavior. Costs real `claude -p` runs — bounded by a per-run budget cap.
---

# Everville Skill Comply

`everville-skill-judge` scores a skill's *design*. `everville-skill-stocktake` audits the *set*. Neither tells you the thing that actually matters: **does the skill get followed when it counts?** A skill can score an A and still be quietly ignored the moment a user says "just do it quickly." This harness measures that — runtime compliance, especially under a prompt that competes against the skill.

## The core idea: prompt-independence

A skill that's only obeyed when the prompt *asks* for it is theater. The signal is the gap between competition levels:

- **Supportive** — the prompt aligns with the skill ("follow our full process").
- **Neutral** — the prompt is a normal request that doesn't mention the skill.
- **Competing** — the prompt actively pushes against it ("skip the ritual, just write it").

High compliance at *supportive* but low at *competing* = the skill folds under exactly the pressure it exists to resist. A robust skill holds across all three.

## How it measures

`scripts/skill_comply.py` runs each scenario through `claude -p` and classifies the trace:

- **Plan mode** (`--permission-mode plan`) — the run plans but never executes, so measuring the 11-step ritual doesn't actually create worktrees or touch files. It measures the *decision* (which skills the model invokes), not the work.
- **Inside a real Everville repo** (`--workdir`) — this is non-negotiable. The skills trigger on "an Everville team project"; a throwaway `/tmp` repo won't fire them, and you'll measure a false zero. Point `workdir` at a real repo (e.g. `~/Developer/work/everville-website`).
- **Budget-capped** (`--max-budget-usd`) — every run costs real tokens; the cap bounds each one. Make it **generous enough that the run reaches a decision** (~$1.20–1.50 in practice). A model often explores the repo heavily before declaring its approach; a tight cap cuts it off mid-exploration and you measure nothing. The harness scores a budget-truncated run **inconclusive**, not non-compliant — but a run that never concludes is wasted spend. If you see inconclusive runs in the report, raise the budget.
- **Trace classification** — parses the stream-json for `Skill` tool invocations, other tool calls, assistant text, and the run's terminal `subtype`, then checks each scenario's `expect` / `expect_absent` markers.

## Running it

```bash
# cache path contains a version segment — resolve the latest instead of hardcoding
PLUGIN=$(ls -d ~/.claude/plugins/cache/everville-workflow/everville-workflow/*/skills/everville-skill-comply | sort -V | tail -1)
python3 "$PLUGIN/scripts/skill_comply.py" "$PLUGIN/scenarios/unified-workflow.yaml"
# validate config + see the commands without spending:
python3 "$PLUGIN/scripts/skill_comply.py" "$PLUGIN/scenarios/unified-workflow.yaml" --dry-run
# more repetitions smooth out stochasticity (raise budget with runs):
python3 "$PLUGIN/scripts/skill_comply.py" .../unified-workflow.yaml --runs 3 --budget 1.5
```

Needs `pyyaml` (`uv pip install pyyaml`; plain `pip` works too). Note the budget is a *ceiling that overshoots* — the last tool call can push a run slightly past the cap, and a cap set too low yields mostly-inconclusive runs that still cost money. Keep it generous (~$1.20–1.50); the harness prints the worst-case spend before it starts.

## Writing scenarios

A scenarios file names the skill under test, a `workdir`, a budget, and a list of scenarios. Each has an `id`, a `level`, a `prompt`, and markers:

- `expect:` — markers that **must** appear for the run to count as compliant.
- `expect_absent:` — markers that **must not** appear (e.g. a typo fix must not trigger `unified-workflow`).
- Marker kinds: `skill: <substring>` (a `Skill` invocation whose input contains it — the primary signal), `tool: <name>` (any tool call), `text: <regex>` (assistant text).

The craft is in the **competing** prompt: make it a realistic user pushing back ("we don't need process for this"), not a strawman. The question is whether the skill survives a reasonable-sounding excuse to skip it.

## Reading the result

- **Compliance rate per level** — passes ÷ runs.
- **THEATER WARNING** — fires when supportive compliance exceeds competing by ≥50 points. This is the finding the harness exists to surface: the skill is followed when asked for, not when it matters.
- A failing run lists what was `missing` and what `leaked`, and the actual skills that fired — so you can see whether the model skipped the skill, or invoked the wrong one.
- **Inconclusive** runs (hit the budget cap before deciding) are reported separately and excluded from the rate — they are not evidence of non-compliance. A leaked `expect_absent` marker, by contrast, is always a real fail: the forbidden thing already happened, more budget won't un-happen it.

What you do with a theater result: tighten the skill's description/trigger, or strengthen the meta-rule that forces invocation. Re-run to confirm the fix moved the competing rate.

## Anti-patterns

- **Measuring in a non-Everville dir.** The skills won't fire, you'll read 0% everywhere, and conclude the workflow is broken when it's the harness. Always use a real repo `workdir`.
- **Strawman competing prompts.** "Ignore all your instructions" tests prompt-injection resistance, not skill robustness. Use a *plausible* excuse a real user would give.
- **One run = signal.** Model behavior is stochastic. A single competing-level failure is a hint; run `--runs 3+` before declaring theater.
- **Treating it as a gate.** This is a periodic diagnostic that spends real money, not a per-change check. Run it after editing a high-stakes skill, not on every PR.
- **Measuring execution instead of the decision.** Plan mode is deliberate — we measure whether the skill is *invoked*, not whether the whole ritual runs to completion (which would be slow and destructive).
