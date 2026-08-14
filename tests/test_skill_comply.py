from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest import mock


SCRIPT = (
    pathlib.Path(__file__).parents[1]
    / "plugins/everville-meta/skills/everville-skill-comply/scripts/skill_comply.py"
)
SPEC = importlib.util.spec_from_file_location("skill_comply", SCRIPT)
assert SPEC and SPEC.loader
skill_comply = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_comply)


def valid_config() -> dict:
    return {
        "schema_version": 1,
        "skill": "unified-workflow",
        "budget_usd": 1.25,
        "runs": 3,
        "timeout_seconds": 180,
        "scenarios": [
            {
                "id": "feature-neutral",
                "level": "neutral",
                "prompt": "Add a tested feature.",
                "expect": [{"skill": "unified-workflow"}],
                "expect_absent": [{"skill": "trivial-whitelist"}],
            }
        ],
    }


class ConfigTests(unittest.TestCase):
    def write_config(self, value: object, suffix: str = ".json") -> pathlib.Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = pathlib.Path(directory.name) / f"scenarios{suffix}"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_load_config_accepts_valid_json(self) -> None:
        self.assertEqual(skill_comply.load_config(self.write_config(valid_config())), valid_config())

    def test_load_config_rejects_non_json_and_invalid_schema(self) -> None:
        path = self.write_config({}, suffix=".yaml")
        path.write_text("skill: nope\n", encoding="utf-8")
        with self.assertRaisesRegex(skill_comply.ConfigError, "valid JSON"):
            skill_comply.load_config(path)

        cases = [
            ({**valid_config(), "schema_version": 2}, "schema_version"),
            ({**valid_config(), "runs": 0}, "runs"),
            ({**valid_config(), "runs": True}, "runs"),
            ({**valid_config(), "budget_usd": -1}, "budget_usd"),
            ({**valid_config(), "budget_usd": float("inf")}, "budget_usd"),
        ]
        for config, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(skill_comply.ConfigError, message):
                    skill_comply.load_config(self.write_config(config))

    def test_load_config_validates_ids_and_markers(self) -> None:
        cases = []
        bad_id = valid_config()
        bad_id["scenarios"][0]["id"] = "has spaces"
        cases.append((bad_id, "id"))

        duplicate = valid_config()
        duplicate["scenarios"].append(dict(duplicate["scenarios"][0]))
        cases.append((duplicate, "duplicate"))

        bad_marker = valid_config()
        bad_marker["scenarios"][0]["expect"] = [{"unknown": "value"}]
        cases.append((bad_marker, "marker"))

        empty_marker = valid_config()
        empty_marker["scenarios"][0]["expect"] = [{"skill": ""}]
        cases.append((empty_marker, "marker"))

        bad_regex = valid_config()
        bad_regex["scenarios"][0]["expect"] = [{"text": "["}]
        cases.append((bad_regex, "regex"))

        for config, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(skill_comply.ConfigError, message):
                    skill_comply.load_config(self.write_config(config))

    def test_resolve_workdir_and_plugin_dir_validate_directories(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            plugin = root / "plugin"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
            self.assertEqual(skill_comply.resolve_workdir(root), root.resolve())
            self.assertEqual(skill_comply.resolve_plugin_dir(plugin), plugin.resolve())

            with self.assertRaisesRegex(skill_comply.ConfigError, "workdir"):
                skill_comply.resolve_workdir(root / "missing")
            with self.assertRaisesRegex(skill_comply.ConfigError, "plugin.json"):
                skill_comply.resolve_plugin_dir(root)


class TraceAndEvaluationTests(unittest.TestCase):
    TRACE = "\n".join(
        [
            json.dumps(
                {
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Skill",
                                "input": {"skill": "unified-workflow"},
                            },
                            {"type": "text", "text": "LIGHT track selected"},
                        ]
                    }
                }
            ),
            json.dumps({"type": "result", "subtype": "success", "total_cost_usd": 0.12}),
        ]
    )

    def test_parse_trace_and_compliance_classification(self) -> None:
        signals = skill_comply.parse_trace_text(self.TRACE)
        result = skill_comply.classify_result(
            valid_config()["scenarios"][0],
            {**signals, "exit": 0, "stderr": "", "timed_out": False, "launch_error": None},
        )
        self.assertEqual(result["classification"], "compliant")
        self.assertTrue(result["pass"])

    def test_process_error_is_not_scored_as_non_compliance(self) -> None:
        signals = skill_comply.parse_trace_text("")
        result = skill_comply.classify_result(
            valid_config()["scenarios"][0],
            {
                **signals,
                "exit": 2,
                "stderr": "authentication failed",
                "timed_out": False,
                "launch_error": None,
            },
        )
        self.assertEqual(result["classification"], "infrastructure_error")
        self.assertFalse(result["conclusive"])
        self.assertIn("authentication failed", result["error"])

    def test_budget_cap_is_inconclusive(self) -> None:
        signals = skill_comply.parse_trace_text(
            json.dumps({"type": "result", "subtype": "error_max_budget_usd"})
        )
        result = skill_comply.classify_result(
            valid_config()["scenarios"][0],
            {**signals, "exit": 0, "stderr": "", "timed_out": False, "launch_error": None},
        )
        self.assertEqual(result["classification"], "inconclusive")
        self.assertFalse(result["conclusive"])

    def test_exit_zero_terminal_api_error_is_infrastructure_error(self) -> None:
        signals = skill_comply.parse_trace_text(
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": True,
                    "api_error_status": 401,
                    "result": "Invalid API key",
                    "total_cost_usd": 0,
                }
            )
        )
        result = skill_comply.classify_result(
            valid_config()["scenarios"][0],
            {**signals, "exit": 0, "stderr": "", "timed_out": False, "launch_error": None},
        )
        self.assertEqual(result["classification"], "infrastructure_error")
        self.assertFalse(result["conclusive"])
        self.assertIn("API status 401", result["error"])
        self.assertIn("Invalid API key", result["error"])


class ExecutionTests(unittest.TestCase):
    def test_build_cmd_loads_candidate_plugin(self) -> None:
        cmd = skill_comply.build_cmd("prompt", 1.0, "sonnet", pathlib.Path("/tmp/candidate"))
        self.assertIn("--plugin-dir", cmd)
        self.assertEqual(cmd[cmd.index("--plugin-dir") + 1], "/tmp/candidate")
        self.assertIn("--model", cmd)

    @mock.patch.object(skill_comply.subprocess, "run")
    def test_run_cleans_trace_and_preserves_stderr_and_exit(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            ["claude"], 9, stdout="not-json\n", stderr="login required"
        )
        with tempfile.TemporaryDirectory() as td:
            result = skill_comply.run_scenario(
                "prompt",
                pathlib.Path(td),
                1.0,
                None,
                pathlib.Path(td),
                timeout=30,
                retain_trace=False,
                trace_dir=pathlib.Path(td),
            )
            self.assertEqual(result["exit"], 9)
            self.assertEqual(result["stderr"], "login required")
            self.assertIsNone(result["trace"])
            self.assertEqual(list(pathlib.Path(td).glob("skill-comply-*.jsonl")), [])
            self.assertEqual(run.call_args.kwargs["timeout"], 30)

    def test_dry_run_prints_complete_pre_spend_summary(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            config_path = root / "scenarios.json"
            config_path.write_text(json.dumps(valid_config()), encoding="utf-8")
            plugin = root / "candidate"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                status = skill_comply.main(
                    [
                        str(config_path),
                        "--plugin-dir",
                        str(plugin),
                        "--workdir",
                        str(root),
                        "--dry-run",
                    ]
                )

            rendered = output.getvalue()
            self.assertEqual(status, 0)
            self.assertIn(f"candidate: {plugin.resolve()}", rendered)
            self.assertIn(f"workdir: {root.resolve()}", rendered)
            self.assertIn("3 run(s)", rendered)
            self.assertIn("timeout: 180s", rendered)
            self.assertIn("budget: $1.25/run", rendered)
            self.assertIn("worst-case paid total: $3.75", rendered)

    @mock.patch.object(skill_comply.subprocess, "run")
    def test_run_can_retain_trace_explicitly(self, run: mock.Mock) -> None:
        run.return_value = subprocess.CompletedProcess(
            ["claude"], 0, stdout=TraceAndEvaluationTests.TRACE, stderr="warning"
        )
        with tempfile.TemporaryDirectory() as td:
            result = skill_comply.run_scenario(
                "prompt",
                pathlib.Path(td),
                1.0,
                None,
                pathlib.Path(td),
                timeout=30,
                retain_trace=True,
                trace_dir=pathlib.Path(td),
            )
            self.assertTrue(pathlib.Path(result["trace"]).is_file())
            self.assertEqual(result["stderr"], "warning")

    @mock.patch.object(skill_comply.subprocess, "run")
    def test_timeout_is_an_infrastructure_error_and_trace_is_cleaned(self, run: mock.Mock) -> None:
        run.side_effect = subprocess.TimeoutExpired(
            ["claude"], 2, output="partial output", stderr="still running"
        )
        with tempfile.TemporaryDirectory() as td:
            signals = skill_comply.run_scenario(
                "prompt",
                pathlib.Path(td),
                1.0,
                None,
                pathlib.Path(td),
                timeout=2,
                retain_trace=False,
                trace_dir=pathlib.Path(td),
            )
            result = skill_comply.classify_result(valid_config()["scenarios"][0], signals)
            self.assertEqual(result["classification"], "infrastructure_error")
            self.assertIn("timed out", result["error"])
            self.assertEqual(list(pathlib.Path(td).glob("skill-comply-*.jsonl")), [])


class ReportingTests(unittest.TestCase):
    def result(self, run: int, classification: str = "compliant") -> dict:
        return {
            "id": "feature",
            "level": "competing",
            "run": run,
            "classification": classification,
            "pass": classification == "compliant",
            "conclusive": classification in {"compliant", "non_compliant"},
            "missing": [],
            "leaked": [],
            "cost": 0.1,
            "stderr": "",
            "exit": 0,
            "subtype": "success",
            "error": None,
            "skills_fired": [],
            "trace": None,
        }

    def render(self, results: list[dict]) -> str:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            skill_comply.report("unified-workflow", pathlib.Path("/repo"), results)
        return output.getvalue()

    def test_one_run_never_prints_strong_robust_claim(self) -> None:
        text = self.render([self.result(0)])
        self.assertNotIn("Robust", text)
        self.assertIn("LOW CONFIDENCE", text)

    def test_three_competing_runs_can_print_robust_claim(self) -> None:
        text = self.render([self.result(i) for i in range(3)])
        self.assertIn("Robust", text)

    def test_infrastructure_errors_are_reported_separately(self) -> None:
        broken = self.result(0, "infrastructure_error")
        broken["error"] = "claude exited 2: login required"
        text = self.render([broken])
        self.assertIn("Infrastructure errors", text)
        self.assertNotIn("Non-compliant runs", text)


class ExitStatusTests(unittest.TestCase):
    def run_main_with_classifications(self, classifications: list[str]) -> int:
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            config_path = root / "scenarios.json"
            config = valid_config()
            config["runs"] = len(classifications)
            config_path.write_text(json.dumps(config), encoding="utf-8")
            plugin = root / "candidate"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")

            verdicts = []
            for classification in classifications:
                conclusive = classification in {"compliant", "non_compliant"}
                verdicts.append(
                    {
                        "classification": classification,
                        "pass": classification == "compliant",
                        "conclusive": conclusive,
                        "missing": [],
                        "leaked": [],
                        "error": "measurement did not complete" if not conclusive else None,
                    }
                )
            signals = {
                "cost": 0.0,
                "subtype": "success",
                "result_is_error": False,
                "api_error_status": None,
                "result_error": "",
                "exit": 0,
                "stderr": "",
                "skills": [],
                "trace": None,
            }
            with (
                mock.patch.object(skill_comply, "run_scenario", return_value=signals),
                mock.patch.object(skill_comply, "classify_result", side_effect=verdicts),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
            ):
                return skill_comply.main(
                    [
                        str(config_path),
                        "--plugin-dir",
                        str(plugin),
                        "--workdir",
                        str(root),
                    ]
                )

    def test_inconclusive_measurement_has_distinct_nonzero_exit(self) -> None:
        self.assertEqual(
            self.run_main_with_classifications(["inconclusive"]),
            skill_comply.EXIT_INCONCLUSIVE,
        )

    def test_inconclusive_required_run_is_not_masked_by_noncompliance(self) -> None:
        self.assertEqual(
            self.run_main_with_classifications(["non_compliant", "inconclusive"]),
            skill_comply.EXIT_INCONCLUSIVE,
        )

    def test_conclusive_compliance_exits_zero(self) -> None:
        self.assertEqual(self.run_main_with_classifications(["compliant"]), 0)

    def test_infrastructure_and_noncompliance_keep_distinct_exits(self) -> None:
        self.assertEqual(
            self.run_main_with_classifications(["infrastructure_error"]),
            skill_comply.EXIT_INFRASTRUCTURE_ERROR,
        )
        self.assertEqual(
            self.run_main_with_classifications(["non_compliant"]),
            skill_comply.EXIT_NON_COMPLIANT,
        )


if __name__ == "__main__":
    unittest.main()
