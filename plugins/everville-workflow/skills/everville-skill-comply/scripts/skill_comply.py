#!/usr/bin/env python3
"""skill_comply — measure whether a skill is actually obeyed, including when the prompt competes against it.

Runs each scenario through `claude -p` in plan mode (non-destructive) inside a real
Everville repo, captures the stream-json trace, and classifies whether the expected
skills fired. Reports a compliance rate per competition level; a skill that only
complies when the prompt is supportive is theater.

Usage:
  skill_comply.py SCENARIOS.yaml [--workdir DIR] [--budget USD] [--runs N]
                  [--dry-run] [--json OUT.json] [--model NAME]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

try:
    import yaml
except ModuleNotFoundError:
    sys.exit("skill_comply needs PyYAML — install it: `pip install pyyaml` (or `uv pip install pyyaml`).")

LEVELS = ("supportive", "neutral", "competing")


def load_config(path: pathlib.Path) -> dict:
    cfg = yaml.safe_load(path.read_text())
    if not isinstance(cfg, dict) or "scenarios" not in cfg:
        sys.exit(f"{path}: must be a mapping with a 'scenarios' list")
    for s in cfg["scenarios"]:
        if s.get("level") not in LEVELS:
            sys.exit(f"scenario {s.get('id')!r}: level must be one of {LEVELS}")
        if not s.get("prompt"):
            sys.exit(f"scenario {s.get('id')!r}: missing prompt")
    return cfg


def build_cmd(prompt: str, budget: float, model: str | None) -> list[str]:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json", "--verbose",
        "--permission-mode", "plan",          # never executes — measures the decision, not the work
        "--max-budget-usd", str(budget),
        "--no-session-persistence",
        "--disallowed-tools", "AskUserQuestion",  # headless can't answer; don't waste budget
        "--append-system-prompt",
        "You are running non-interactively for a measurement harness. Decide your approach to the request as you normally would. Do not ask the user questions.",
    ]
    if model:
        cmd += ["--model", model]
    return cmd


def run_scenario(prompt: str, workdir: str, budget: float, model: str | None) -> dict:
    cmd = build_cmd(prompt, budget, model)
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as tf:
        trace_path = tf.name
    with open(trace_path, "w") as out:
        proc = subprocess.run(cmd, cwd=os.path.expanduser(workdir), stdout=out,
                              stderr=subprocess.DEVNULL, text=True)
    return parse_trace(trace_path) | {"exit": proc.returncode, "trace": trace_path}


def parse_trace(path: str) -> dict:
    """Collect the signals a marker can match: tool names, Skill invocations, assistant text."""
    tools: list[str] = []
    skills: list[str] = []
    texts: list[str] = []
    cost = 0.0
    subtype = None
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("type") == "result":
            cost = e.get("total_cost_usd", cost)
            subtype = e.get("subtype")
        msg = e.get("message")
        if not isinstance(msg, dict):
            continue
        for c in msg.get("content") or []:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use":
                tools.append(c.get("name", ""))
                if c.get("name") == "Skill":
                    skills.append(json.dumps(c.get("input", {})))
            elif c.get("type") == "text":
                texts.append(c.get("text", ""))
    return {"tools": tools, "skills": skills, "text": "\n".join(texts), "cost": cost, "subtype": subtype}


def marker_present(marker: dict, signals: dict) -> bool:
    kind, val = next(iter(marker.items()))
    val = str(val)
    if kind == "skill":
        return any(val in s for s in signals["skills"])
    if kind == "tool":
        return val in signals["tools"]
    if kind == "text":
        import re
        return re.search(val, signals["text"], re.IGNORECASE) is not None
    sys.exit(f"unknown marker kind: {kind!r} (use skill / tool / text)")


def evaluate(scenario: dict, signals: dict) -> dict:
    expect = scenario.get("expect", [])
    expect_absent = scenario.get("expect_absent", [])
    missing = [m for m in expect if not marker_present(m, signals)]
    present_bad = [m for m in expect_absent if marker_present(m, signals)]
    passed = not missing and not present_bad
    # A run cut off by the budget cap before the expected skill fired is INCONCLUSIVE,
    # not non-compliant — the skill might have fired with more budget. (A leaked
    # expect_absent marker is a real fail regardless: it already happened.)
    truncated = signals.get("subtype") == "error_max_budget_usd"
    inconclusive = (not passed) and truncated and bool(missing) and not present_bad
    return {"pass": passed, "inconclusive": inconclusive, "missing": missing, "leaked": present_bad}


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure skill compliance under competing prompts.")
    ap.add_argument("scenarios", type=pathlib.Path)
    ap.add_argument("--workdir", help="Everville repo to run scenarios in (overrides config)")
    ap.add_argument("--budget", type=float, help="max USD per run (overrides config)")
    ap.add_argument("--runs", type=int, help="repetitions per scenario (overrides config)")
    ap.add_argument("--model")
    ap.add_argument("--dry-run", action="store_true", help="validate + print commands, don't call claude")
    ap.add_argument("--json", dest="json_out", type=pathlib.Path)
    args = ap.parse_args()

    cfg = load_config(args.scenarios)
    workdir = args.workdir or cfg.get("workdir") or "."
    budget = args.budget or cfg.get("budget_usd", 0.50)
    runs = args.runs or cfg.get("runs", 1)
    skill_name = cfg.get("skill", args.scenarios.stem)

    if not args.dry_run and not pathlib.Path(os.path.expanduser(workdir)).is_dir():
        sys.exit(f"workdir does not exist: {workdir} — point it at a real Everville repo")

    if not args.dry_run:
        worst_case = len(cfg["scenarios"]) * runs * budget
        print(f"This will run {len(cfg['scenarios'])} scenario(s) × {runs} run(s) via `claude -p` "
              f"at up to ${budget:.2f} each — worst-case ~${worst_case:.2f} of real spend.\n", file=sys.stderr)

    results = []
    for s in cfg["scenarios"]:
        for r in range(runs):
            if args.dry_run:
                cmd = build_cmd(s["prompt"], budget, args.model)
                print(f"[dry-run] {s['id']} ({s['level']}) in {workdir}:\n  {' '.join(cmd[:1])} -p <prompt> "
                      f"--permission-mode plan --max-budget-usd {budget} ...")
                continue
            sig = run_scenario(s["prompt"], workdir, budget, args.model)
            verdict = evaluate(s, sig)
            results.append({"id": s["id"], "level": s["level"], "run": r,
                            "pass": verdict["pass"], "inconclusive": verdict["inconclusive"],
                            "missing": verdict["missing"], "leaked": verdict["leaked"],
                            "cost": sig["cost"], "subtype": sig["subtype"],
                            "skills_fired": sig["skills"]})

    if args.dry_run:
        print(f"\nConfig OK: {len(cfg['scenarios'])} scenarios × {runs} run(s) against '{skill_name}'.")
        return

    report(skill_name, workdir, results)
    if args.json_out:
        args.json_out.write_text(json.dumps({"skill": skill_name, "workdir": workdir, "results": results}, indent=2))


def report(skill_name: str, workdir: str, results: list[dict]) -> None:
    by_level = {lvl: [r for r in results if r["level"] == lvl] for lvl in LEVELS}
    # Compliance is computed over CONCLUSIVE runs only — budget-truncated runs are excluded.
    rate = {}
    for lvl, rs in by_level.items():
        conclusive = [r for r in rs if not r["inconclusive"]]
        rate[lvl] = (sum(r["pass"] for r in conclusive) / len(conclusive)) if conclusive else None
    total_cost = sum(r["cost"] for r in results)
    inconclusive = [r for r in results if r["inconclusive"]]

    print(f"\n## Skill Compliance — {skill_name}   (workdir: {workdir})\n")
    print("| Level | Compliance | Conclusive | Inconclusive |")
    print("|-------|-----------|-----------|-------------|")
    for lvl in LEVELS:
        rs = by_level[lvl]
        conc = [r for r in rs if not r["inconclusive"]]
        inc = len(rs) - len(conc)
        pct = f"{rate[lvl]*100:.0f}%" if rate[lvl] is not None else "—"
        print(f"| {lvl} | {pct} | {len(conc)} | {inc} |")

    sup, comp = rate["supportive"], rate["competing"]
    if sup is not None and comp is not None and (sup - comp) >= 0.5:
        print(f"\n⚠️  THEATER WARNING: compliance drops from {sup*100:.0f}% (supportive) to "
              f"{comp*100:.0f}% (competing). The skill is followed when asked for, not when it matters.")
    elif comp is not None and comp >= 0.8:
        print(f"\n✅ Robust: {comp*100:.0f}% compliance even under competing prompts.")

    if inconclusive:
        print(f"\n🟡 {len(inconclusive)} run(s) hit the budget cap before deciding — scored INCONCLUSIVE, "
              f"not counted. Raise --budget so runs finish: " +
              ", ".join(f"{r['id']}({r['level']})" for r in inconclusive))

    fails = [r for r in results if not r["pass"] and not r["inconclusive"]]
    if fails:
        print("\n### Non-compliant runs")
        for r in fails:
            miss = ", ".join(next(iter(m.items()))[1] for m in r["missing"]) or "—"
            leak = ", ".join(next(iter(m.items()))[1] for m in r["leaked"]) or "—"
            print(f"- {r['id']} ({r['level']}): missing [{miss}] · leaked [{leak}]")
    print(f"\nTotal cost: ${total_cost:.2f}")


if __name__ == "__main__":
    main()
