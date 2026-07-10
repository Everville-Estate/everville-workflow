#!/usr/bin/env python3
"""Measure candidate-plugin skill invocation under competing prompts.

The harness intentionally runs Claude in plan mode. It measures whether the
candidate skill is invoked; it does not prove hook enforcement or end-to-end
workflow execution.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Any


LEVELS = ("supportive", "neutral", "competing")
MARKER_KINDS = ("skill", "tool", "text")
SCHEMA_VERSION = 1
DEFAULT_BUDGET = 1.50
DEFAULT_RUNS = 3
DEFAULT_TIMEOUT = 180
MIN_CONFIDENT_RUNS = 3
DEFAULT_PLUGIN_DIR = pathlib.Path(__file__).resolve().parents[3]


class ConfigError(ValueError):
    """A scenario file or CLI path is invalid."""


def _positive_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{field} must be a positive number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ConfigError(f"{field} must be a finite positive number")
    return number


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ConfigError(f"{field} must be an integer >= 1")
    return value


def _validate_markers(markers: Any, location: str) -> list[dict[str, str]]:
    if not isinstance(markers, list):
        raise ConfigError(f"{location} markers must be a list")
    validated: list[dict[str, str]] = []
    for index, marker in enumerate(markers):
        if not isinstance(marker, dict) or len(marker) != 1:
            raise ConfigError(f"{location} marker {index} must contain exactly one marker kind")
        kind, value = next(iter(marker.items()))
        if kind not in MARKER_KINDS or not isinstance(value, str) or not value.strip():
            raise ConfigError(
                f"{location} marker {index} must be a non-empty skill, tool, or text marker"
            )
        if kind == "text":
            try:
                re.compile(value)
            except re.error as error:
                raise ConfigError(f"{location} marker {index} has invalid text regex: {error}") from error
        validated.append({kind: value})
    return validated


def validate_config(config: Any) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise ConfigError("scenario file must contain a JSON object")
    allowed = {"schema_version", "skill", "budget_usd", "runs", "timeout_seconds", "scenarios"}
    unknown = sorted(set(config) - allowed)
    if unknown:
        raise ConfigError(f"unknown top-level field(s): {', '.join(unknown)}")
    if config.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(config.get("skill"), str) or not config["skill"].strip():
        raise ConfigError("skill must be a non-empty string")

    normalized = dict(config)
    normalized["budget_usd"] = _positive_number(config.get("budget_usd", DEFAULT_BUDGET), "budget_usd")
    normalized["runs"] = _positive_int(config.get("runs", DEFAULT_RUNS), "runs")
    normalized["timeout_seconds"] = _positive_number(
        config.get("timeout_seconds", DEFAULT_TIMEOUT), "timeout_seconds"
    )

    scenarios = config.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise ConfigError("scenarios must be a non-empty list")
    scenario_allowed = {"id", "level", "prompt", "expect", "expect_absent"}
    seen_ids: set[str] = set()
    normalized_scenarios = []
    for index, scenario in enumerate(scenarios):
        location = f"scenario {index}"
        if not isinstance(scenario, dict):
            raise ConfigError(f"{location} must be an object")
        unknown_scenario = sorted(set(scenario) - scenario_allowed)
        if unknown_scenario:
            raise ConfigError(f"{location} has unknown field(s): {', '.join(unknown_scenario)}")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", scenario_id):
            raise ConfigError(f"{location} id must match [a-z0-9][a-z0-9._-]*")
        if scenario_id in seen_ids:
            raise ConfigError(f"duplicate scenario id: {scenario_id}")
        seen_ids.add(scenario_id)
        level = scenario.get("level")
        if level not in LEVELS:
            raise ConfigError(f"scenario {scenario_id}: level must be one of {LEVELS}")
        prompt = scenario.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ConfigError(f"scenario {scenario_id}: prompt must be a non-empty string")
        expect = _validate_markers(scenario.get("expect", []), f"scenario {scenario_id} expect")
        expect_absent = _validate_markers(
            scenario.get("expect_absent", []), f"scenario {scenario_id} expect_absent"
        )
        if not expect and not expect_absent:
            raise ConfigError(f"scenario {scenario_id}: at least one marker is required")
        normalized_scenarios.append(
            {
                "id": scenario_id,
                "level": level,
                "prompt": prompt,
                "expect": expect,
                "expect_absent": expect_absent,
            }
        )
    normalized["scenarios"] = normalized_scenarios
    return normalized


def load_config(path: pathlib.Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ConfigError(f"{path}: must be readable, valid JSON ({error})") from error
    return validate_config(config)


def resolve_workdir(path: os.PathLike[str] | str) -> pathlib.Path:
    resolved = pathlib.Path(path).expanduser().resolve()
    if not resolved.is_dir():
        raise ConfigError(f"workdir does not exist or is not a directory: {resolved}")
    return resolved


def resolve_plugin_dir(path: os.PathLike[str] | str) -> pathlib.Path:
    resolved = pathlib.Path(path).expanduser().resolve()
    if not resolved.is_dir():
        raise ConfigError(f"plugin-dir does not exist or is not a directory: {resolved}")
    manifests = (resolved / ".claude-plugin" / "plugin.json", resolved / "plugin.json")
    if not any(manifest.is_file() for manifest in manifests):
        raise ConfigError(f"plugin-dir has no .claude-plugin/plugin.json: {resolved}")
    return resolved


def build_cmd(
    prompt: str,
    budget: float,
    model: str | None,
    plugin_dir: pathlib.Path,
) -> list[str]:
    cmd = [
        "claude",
        "--plugin-dir",
        str(plugin_dir),
        "-p",
        prompt,
        "--output-format",
        "stream-json",
        "--verbose",
        "--permission-mode",
        "plan",
        "--max-budget-usd",
        str(budget),
        "--no-session-persistence",
        "--disallowed-tools",
        "AskUserQuestion",
        "--append-system-prompt",
        (
            "You are running non-interactively for a measurement harness. "
            "Decide your approach normally, do not ask questions, and do not execute changes."
        ),
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


def _as_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run_scenario(
    prompt: str,
    workdir: pathlib.Path,
    budget: float,
    model: str | None,
    plugin_dir: pathlib.Path,
    *,
    timeout: float,
    retain_trace: bool,
    trace_dir: pathlib.Path | None = None,
) -> dict[str, Any]:
    """Run one scenario and clean its trace unless retention was explicitly requested."""
    cmd = build_cmd(prompt, budget, model, plugin_dir)
    trace_handle = tempfile.NamedTemporaryFile(
        "w", prefix="skill-comply-", suffix=".jsonl", delete=False, dir=trace_dir, encoding="utf-8"
    )
    trace_path = pathlib.Path(trace_handle.name)
    trace_handle.close()
    stdout = ""
    stderr = ""
    exit_code: int | None = None
    timed_out = False
    launch_error: str | None = None
    try:
        try:
            process = subprocess.run(
                cmd,
                cwd=str(workdir),
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            stdout = process.stdout or ""
            stderr = process.stderr or ""
            exit_code = process.returncode
        except subprocess.TimeoutExpired as error:
            timed_out = True
            stdout = _as_text(error.stdout or error.output)
            stderr = _as_text(error.stderr)
        except OSError as error:
            launch_error = str(error)
        trace_path.write_text(stdout, encoding="utf-8")
        signals = parse_trace_text(stdout)
        return {
            **signals,
            "exit": exit_code,
            "stderr": stderr.strip(),
            "timed_out": timed_out,
            "launch_error": launch_error,
            "trace": str(trace_path) if retain_trace else None,
        }
    finally:
        if not retain_trace:
            trace_path.unlink(missing_ok=True)


def parse_trace_text(trace: str) -> dict[str, Any]:
    """Collect marker signals and terminal metadata from a stream-json trace."""
    tools: list[str] = []
    skills: list[str] = []
    texts: list[str] = []
    cost = 0.0
    subtype: str | None = None
    result_is_error = False
    api_error_status: int | str | None = None
    result_error = ""
    result_seen = False
    invalid_lines = 0
    for raw_line in trace.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            invalid_lines += 1
            continue
        if not isinstance(event, dict):
            invalid_lines += 1
            continue
        if event.get("type") == "result":
            result_seen = True
            raw_cost = event.get("total_cost_usd")
            if isinstance(raw_cost, (int, float)) and not isinstance(raw_cost, bool):
                cost = float(raw_cost)
            subtype = event.get("subtype") if isinstance(event.get("subtype"), str) else None
            result_is_error = event.get("is_error") is True
            raw_status = event.get("api_error_status")
            if isinstance(raw_status, (int, str)) and not isinstance(raw_status, bool):
                api_error_status = raw_status
            raw_result = event.get("result")
            if isinstance(raw_result, str):
                result_error = raw_result.strip()
            elif raw_result is not None:
                result_error = json.dumps(raw_result, sort_keys=True)
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                name = block.get("name")
                if isinstance(name, str):
                    tools.append(name)
                    if name == "Skill":
                        skills.append(json.dumps(block.get("input", {}), sort_keys=True))
            elif block.get("type") == "text" and isinstance(block.get("text"), str):
                texts.append(block["text"])
    return {
        "tools": tools,
        "skills": skills,
        "text": "\n".join(texts),
        "cost": cost,
        "subtype": subtype,
        "result_is_error": result_is_error,
        "api_error_status": api_error_status,
        "result_error": result_error,
        "result_seen": result_seen,
        "invalid_trace_lines": invalid_lines,
    }


def marker_present(marker: dict[str, str], signals: dict[str, Any]) -> bool:
    kind, value = next(iter(marker.items()))
    if kind == "skill":
        return any(value in skill for skill in signals["skills"])
    if kind == "tool":
        return value in signals["tools"]
    return re.search(value, signals["text"], re.IGNORECASE) is not None


def classify_result(scenario: dict[str, Any], signals: dict[str, Any]) -> dict[str, Any]:
    """Classify process health before evaluating compliance markers."""
    subtype = signals.get("subtype")
    if subtype == "error_max_budget_usd":
        return _classification("inconclusive", "budget cap reached before a terminal decision")
    if signals.get("timed_out"):
        return _classification("infrastructure_error", "claude process timed out")
    if signals.get("launch_error"):
        return _classification("infrastructure_error", f"could not launch claude: {signals['launch_error']}")
    if signals.get("exit") != 0:
        detail = signals.get("stderr") or "no stderr"
        return _classification(
            "infrastructure_error", f"claude exited {signals.get('exit')}: {detail}"
        )
    if not signals.get("result_seen"):
        return _classification("infrastructure_error", "trace has no terminal result event")
    if signals.get("result_is_error") or signals.get("api_error_status") is not None:
        status = signals.get("api_error_status")
        detail = signals.get("result_error") or signals.get("stderr") or subtype or "unknown error"
        status_text = f" (API status {status})" if status is not None else ""
        return _classification(
            "infrastructure_error", f"claude terminal result reported an error{status_text}: {detail}"
        )
    if isinstance(subtype, str) and subtype.startswith("error"):
        detail = signals.get("stderr") or subtype
        return _classification("infrastructure_error", f"claude result error: {detail}")

    missing = [marker for marker in scenario["expect"] if not marker_present(marker, signals)]
    leaked = [
        marker for marker in scenario["expect_absent"] if marker_present(marker, signals)
    ]
    if not missing and not leaked:
        return _classification("compliant", None, missing, leaked)
    return _classification("non_compliant", None, missing, leaked)


def _classification(
    classification: str,
    error: str | None,
    missing: list[dict[str, str]] | None = None,
    leaked: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    return {
        "classification": classification,
        "pass": classification == "compliant",
        "conclusive": classification in {"compliant", "non_compliant"},
        "missing": missing or [],
        "leaked": leaked or [],
        "error": error,
    }


def _rate(results: list[dict[str, Any]]) -> tuple[float | None, int]:
    conclusive = [result for result in results if result["conclusive"]]
    if not conclusive:
        return None, 0
    return sum(result["pass"] for result in conclusive) / len(conclusive), len(conclusive)


def report(skill_name: str, workdir: pathlib.Path, results: list[dict[str, Any]]) -> None:
    by_level = {level: [result for result in results if result["level"] == level] for level in LEVELS}
    rates = {level: _rate(level_results) for level, level_results in by_level.items()}
    total_cost = sum(result["cost"] for result in results)

    print(f"\n## Skill Invocation Compliance — {skill_name}   (workdir: {workdir})\n")
    print("| Level | Compliance | Conclusive | Inconclusive | Infrastructure |")
    print("|-------|------------|------------|--------------|----------------|")
    for level in LEVELS:
        level_results = by_level[level]
        rate, conclusive_count = rates[level]
        inconclusive_count = sum(
            result["classification"] == "inconclusive" for result in level_results
        )
        infrastructure_count = sum(
            result["classification"] == "infrastructure_error" for result in level_results
        )
        percent = f"{rate * 100:.0f}%" if rate is not None else "—"
        print(
            f"| {level} | {percent} | {conclusive_count} | {inconclusive_count} | "
            f"{infrastructure_count} |"
        )

    supportive, supportive_count = rates["supportive"]
    competing, competing_count = rates["competing"]
    confidence_ready = (
        supportive_count >= MIN_CONFIDENT_RUNS and competing_count >= MIN_CONFIDENT_RUNS
    )
    if (
        confidence_ready
        and supportive is not None
        and competing is not None
        and supportive - competing >= 0.5
    ):
        print(
            f"\nTHEATER WARNING: invocation drops from {supportive * 100:.0f}% (supportive) "
            f"to {competing * 100:.0f}% (competing)."
        )
    elif competing is not None and competing_count >= MIN_CONFIDENT_RUNS and competing >= 0.8:
        print(f"\nRobust invocation signal: {competing * 100:.0f}% under competing prompts.")
    elif any(count and count < MIN_CONFIDENT_RUNS for _, count in rates.values()):
        print(
            f"\nLOW CONFIDENCE: fewer than {MIN_CONFIDENT_RUNS} conclusive runs in at least one "
            "measured level; do not make a strong reliability or theater claim yet."
        )

    inconclusive = [result for result in results if result["classification"] == "inconclusive"]
    if inconclusive:
        print(f"\n### Inconclusive runs ({len(inconclusive)})")
        for result in inconclusive:
            print(f"- {result['id']} ({result['level']}, run {result['run'] + 1}): {result['error']}")

    infrastructure = [
        result for result in results if result["classification"] == "infrastructure_error"
    ]
    if infrastructure:
        print(f"\n### Infrastructure errors ({len(infrastructure)})")
        for result in infrastructure:
            print(f"- {result['id']} ({result['level']}, run {result['run'] + 1}): {result['error']}")

    failures = [result for result in results if result["classification"] == "non_compliant"]
    if failures:
        print("\n### Non-compliant runs")
        for result in failures:
            missing = ", ".join(next(iter(marker.values())) for marker in result["missing"]) or "—"
            leaked = ", ".join(next(iter(marker.values())) for marker in result["leaked"]) or "—"
            print(
                f"- {result['id']} ({result['level']}, run {result['run'] + 1}): "
                f"missing [{missing}] · leaked [{leaked}]"
            )
    retained = [result for result in results if result.get("trace")]
    if retained:
        print("\n### Retained traces")
        for result in retained:
            print(f"- {result['id']} ({result['level']}, run {result['run'] + 1}): {result['trace']}")
    print(f"\nTotal cost: ${total_cost:.2f}")


def _dry_run_command(command: list[str]) -> str:
    redacted = list(command)
    redacted[redacted.index("-p") + 1] = "<prompt>"
    return shlex.join(redacted)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure candidate-plugin skill invocation under competing prompts."
    )
    parser.add_argument("scenarios", type=pathlib.Path, help="JSON scenario file")
    parser.add_argument(
        "--workdir", type=pathlib.Path, default=pathlib.Path.cwd(), help="target repo (default: cwd)"
    )
    parser.add_argument(
        "--plugin-dir",
        type=pathlib.Path,
        default=DEFAULT_PLUGIN_DIR,
        help="candidate plugin root loaded with claude --plugin-dir",
    )
    parser.add_argument("--budget", type=float, help="max USD per run (overrides config)")
    parser.add_argument("--runs", type=int, help="repetitions per scenario (overrides config)")
    parser.add_argument("--timeout", type=float, help="seconds per process (overrides config)")
    parser.add_argument("--model")
    parser.add_argument("--dry-run", action="store_true", help="validate and print commands only")
    parser.add_argument("--retain-traces", action="store_true", help="retain temporary JSONL traces")
    parser.add_argument("--json", dest="json_out", type=pathlib.Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        config = load_config(args.scenarios)
        workdir = resolve_workdir(args.workdir)
        plugin_dir = resolve_plugin_dir(args.plugin_dir)
        budget = _positive_number(
            args.budget if args.budget is not None else config["budget_usd"], "budget"
        )
        runs = _positive_int(args.runs if args.runs is not None else config["runs"], "runs")
        timeout = _positive_number(
            args.timeout if args.timeout is not None else config["timeout_seconds"], "timeout"
        )
    except ConfigError as error:
        print(f"skill_comply: {error}", file=sys.stderr)
        return 2

    worst_case = len(config["scenarios"]) * runs * budget
    if args.dry_run:
        print(
            f"Dry run: {len(config['scenarios'])} scenario(s) × {runs} run(s); "
            f"candidate: {plugin_dir}; workdir: {workdir}; timeout: {timeout:g}s; "
            f"budget: ${budget:.2f}/run; worst-case paid total: ${worst_case:.2f}."
        )
    else:
        print(
            f"Running {len(config['scenarios'])} scenario(s) × {runs} run(s) against candidate "
            f"{plugin_dir} at up to ${budget:.2f} each (worst case ${worst_case:.2f}).",
            file=sys.stderr,
        )

    results: list[dict[str, Any]] = []
    for scenario in config["scenarios"]:
        for run_number in range(runs):
            command = build_cmd(scenario["prompt"], budget, args.model, plugin_dir)
            if args.dry_run:
                print(
                    f"[dry-run] {scenario['id']} ({scenario['level']}) in {workdir}\n  "
                    f"{_dry_run_command(command)}"
                )
                continue
            signals = run_scenario(
                scenario["prompt"],
                workdir,
                budget,
                args.model,
                plugin_dir,
                timeout=timeout,
                retain_trace=args.retain_traces,
            )
            verdict = classify_result(scenario, signals)
            results.append(
                {
                    "id": scenario["id"],
                    "level": scenario["level"],
                    "run": run_number,
                    **verdict,
                    "cost": signals["cost"],
                    "subtype": signals["subtype"],
                    "result_is_error": signals["result_is_error"],
                    "api_error_status": signals["api_error_status"],
                    "result_error": signals["result_error"],
                    "exit": signals["exit"],
                    "stderr": signals["stderr"],
                    "skills_fired": signals["skills"],
                    "trace": signals["trace"],
                }
            )

    if args.dry_run:
        print(
            f"\nConfig OK: {len(config['scenarios'])} scenarios × {runs} runs; "
            f"candidate plugin: {plugin_dir}"
        )
        return 0

    report(config["skill"], workdir, results)
    if args.json_out:
        args.json_out.write_text(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "measurement": "skill-invocation-only",
                    "skill": config["skill"],
                    "workdir": str(workdir),
                    "plugin_dir": str(plugin_dir),
                    "results": results,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if any(result["classification"] == "infrastructure_error" for result in results):
        return 2
    if any(result["classification"] == "non_compliant" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
