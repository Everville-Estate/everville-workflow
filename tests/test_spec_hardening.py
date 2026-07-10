from __future__ import annotations

import contextlib
import importlib.util
import io
import pathlib
import re
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "plugins/everville-workflow/skills/everville-spec-hardening"
SKILL = SKILL_ROOT / "SKILL.md"
REFERENCES = SKILL_ROOT / "references"
SCENARIOS = ROOT / "tests/fixtures/everville-spec-hardening.json"
COMPLY_SCRIPT = ROOT / "plugins/everville-meta/skills/everville-skill-comply/scripts/skill_comply.py"
VALIDATOR_SCRIPT = ROOT / "scripts/validate_repository.py"


class SpecHardeningPackageTests(unittest.TestCase):
    def test_frontmatter_routes_proportionally(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(?P<body>.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        fields = {
            line.split(":", 1)[0]
            for line in match.group("body").splitlines()
            if ":" in line
        }
        self.assertEqual(fields, {"name", "description"})
        self.assertLess(len(text.splitlines()), 250)
        description = match.group("body").lower()
        for phrase in (
            "approved or implementation-bound",
            "multiple components",
            "full design/plan",
            "initial brainstorming",
            "bypass/light",
            "code review or debugging",
            "prose cleanup",
            "single-component plan",
        ):
            self.assertIn(phrase, description)

    def test_mode_verdict_and_authority_contract(self) -> None:
        body = SKILL.read_text(encoding="utf-8")
        for exact in ("**REVIEW**", "**HARDEN**", "**DELIVER**"):
            self.assertIn(exact, body)
        for exact in (
            "**READY**",
            "**READY WITH EXPLICIT DEFERS**",
            "**NOT READY**",
        ):
            self.assertIn(exact, body)
        lowered = body.lower()
        for phrase in (
            "never edit local inputs",
            "external mutations require separate explicit authority",
            "preserving the historical input",
            "do not create a parallel status ledger",
            "subagents are optional",
            "use a single-agent path",
        ):
            self.assertIn(phrase, lowered)

    def test_reference_inventory_is_flat_complete_and_direct(self) -> None:
        files = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual(
            files,
            {
                "SKILL.md",
                "references/boundary-review.md",
                "references/decision-coverage.md",
                "references/delivery.md",
            },
        )
        body = SKILL.read_text(encoding="utf-8")
        for name in ("boundary-review.md", "decision-coverage.md", "delivery.md"):
            self.assertIn(f"(references/{name})", body)
            self.assertNotIn("references/", (REFERENCES / name).read_text(encoding="utf-8"))

    def test_reference_loading_is_conditional(self) -> None:
        body = SKILL.read_text(encoding="utf-8")
        self.assertIn("only when required behavior", body)
        self.assertIn("only when components exchange", body)
        self.assertIn("only when producing or updating", body)
        self.assertNotIn("read all", body.lower())

    def test_private_reasoning_and_per_item_bureaucracy_are_rejected(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL, *sorted(REFERENCES.glob("*.md")))
        ).lower()
        self.assertIn("never request or persist full, private", combined)
        self.assertIn("do not store private reasoning", combined)
        forbidden = (
            "human reviews every section",
            "human decides every structural fix",
            "one item at a time",
            "one subagent per dimension",
            "dispatch parallel subagents",
            "readme is the source of truth",
        )
        for phrase in forbidden:
            self.assertNotIn(phrase, combined)

    def test_archive_fingerprints_are_absent(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        ).lower()
        forbidden = (
            "spec-interrogation",
            "spec-cross-cutting-review",
            "spec-reconciliation",
            "spec-synthesis",
            "sp1-the-spine",
            "gdd-lead-prompt",
            "kuzudb",
            "apache age",
            "actualize readme",
            "full subagent analysis",
            "prioritize: must > should > add",
            "the eight dimensions",
            "feed-forward validation",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, combined)

    def test_repository_policy_rejects_fingerprint_extra_file_and_traversal(self) -> None:
        spec = importlib.util.spec_from_file_location("validate_repository", VALIDATOR_SCRIPT)
        assert spec and spec.loader
        validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(validator)

        def copy_candidate(destination: pathlib.Path) -> None:
            for source in SKILL_ROOT.rglob("*"):
                if source.is_file():
                    target = destination / source.relative_to(SKILL_ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "candidate"
            copy_candidate(candidate)
            skill = candidate / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\n<!-- spec-synthesis -->\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.ValidationError, "source fingerprint"):
                validator.validate_spec_hardening(candidate)

        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "candidate"
            copy_candidate(candidate)
            (candidate / "README.md").write_text("duplicate ledger", encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "invalid package inventory"):
                validator.validate_spec_hardening(candidate)

        with tempfile.TemporaryDirectory() as directory:
            candidate = pathlib.Path(directory) / "candidate"
            copy_candidate(candidate)
            skill = candidate / "SKILL.md"
            skill.write_text(
                skill.read_text(encoding="utf-8") + "\n[escape](../../outside.md)\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.ValidationError, "unsafe or missing local link"):
                validator.validate_spec_hardening(candidate)


class SpecHardeningScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("skill_comply", COMPLY_SCRIPT)
        assert spec and spec.loader
        cls.comply = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.comply)

    def test_scenarios_cover_positive_negative_and_all_levels(self) -> None:
        config = self.comply.load_config(SCENARIOS)
        self.assertEqual(config["skill"], "everville-spec-hardening")
        self.assertEqual(len(config["scenarios"]), 4)
        self.assertEqual(
            {scenario["level"] for scenario in config["scenarios"]},
            {"supportive", "neutral", "competing"},
        )
        positive = [scenario for scenario in config["scenarios"] if scenario["expect"]]
        negative = [scenario for scenario in config["scenarios"] if scenario["expect_absent"]]
        self.assertEqual(len(positive), 3)
        self.assertEqual(len(negative), 1)

    def test_dry_run_never_executes_a_scenario(self) -> None:
        with (
            mock.patch.object(self.comply, "run_scenario") as run_scenario,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            status = self.comply.main([
                str(SCENARIOS),
                "--plugin-dir",
                str(ROOT / "plugins/everville-workflow"),
                "--workdir",
                str(ROOT),
                "--dry-run",
            ])
        self.assertEqual(status, 0)
        run_scenario.assert_not_called()


if __name__ == "__main__":
    unittest.main()
