from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import pathlib
import tempfile
import unittest


SCRIPT = (
    pathlib.Path(__file__).parents[1]
    / "plugins/everville-handoff/skills/everville-handoff/scripts/handoff_validator.py"
)
SPEC = importlib.util.spec_from_file_location("handoff_validator", SCRIPT)
assert SPEC and SPEC.loader
handoff_validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(handoff_validator)


class HandoffValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = pathlib.Path(temporary.name)
        self.handoffs = self.root / ".claude" / "handoffs"
        self.handoffs.mkdir(parents=True)
        (self.root / "README.md").write_text("project", encoding="utf-8")

    def valid_text(self) -> str:
        created = datetime.now(timezone.utc).isoformat()
        sections = {
            "Current state": "The implementation is locally complete. Remote delivery still requires review.",
            "Verification at checkpoint": "- `python3 -m unittest` — 40 tests passed.",
            "Recent commits": "```text\nabc1234 fix validator\n```",
            "Working tree": "```text\n M README.md\n```",
            "Work completed": "- [x] Added fail-closed validation.",
            "Immediate next steps": "1. Review the final diff.\n2. Open an authorized pull request.",
            "Decisions and rationale": "| Decision | Rationale | Alternatives rejected |\n| --- | --- | --- |\n| Validate structure | Prevent false success | Prose-only checks |",
            "Critical files": "- `README.md` — onboarding contract.",
            "Blockers and external waits": "- Branch protection requires repository-owner authorization.",
            "Environment requirements": "- `ANTHROPIC_API_KEY` — required only for a paid live diagnostic.",
            "Assumptions and gotchas": "- Installed plugin caches require reload after update.",
            "Pending and deferred": "- [ ] Enable remote branch protection after authorization.",
            "Sharing status": "Local only; not staged, committed, pushed, uploaded, or sent.",
        }
        body = "\n\n".join(f"## {heading}\n\n{value}" for heading, value in sections.items())
        return (
            "# Handoff: Finish validator remediation\n\n"
            f"**Created:** {created}\n"
            "**Repository:** Everville-Estate/everville-workflow\n"
            "**Branch:** fix/workflow-remediation-0.12.0\n"
            f"**Head:** {'a' * 40}\n"
            "**Continues from:** None\n\n"
            f"{body}\n"
        )

    def write(self, text: str, name: str = "2026-07-10-153000-remediation.md") -> pathlib.Path:
        path = self.handoffs / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_complete_handoff_is_valid(self) -> None:
        self.assertEqual(
            handoff_validator.validate_handoff(self.write(self.valid_text()), self.root), []
        )

    def test_nearly_empty_handoff_fails_closed(self) -> None:
        issues = handoff_validator.validate_handoff(
            self.write("# Handoff: incomplete\n"), self.root
        )
        self.assertTrue(any("metadata 'Created'" in issue for issue in issues))
        self.assertTrue(any("section '## Current state'" in issue for issue in issues))

    def test_invalid_metadata_and_placeholder_are_rejected(self) -> None:
        text = self.valid_text().replace("**Head:** " + "a" * 40, "**Head:** short")
        text = text.replace("Review the final diff.", "<FIRST_ACTION>")
        issues = handoff_validator.validate_handoff(self.write(text), self.root)
        self.assertIn("Head must be a full 40- or 64-character commit SHA", issues)
        self.assertIn("placeholder remains: <FIRST_ACTION>", issues)

    def test_secret_and_missing_reference_are_rejected(self) -> None:
        text = self.valid_text().replace(
            "- `README.md` — onboarding contract.",
            "- `missing/file.md` — absent.\n- API_KEY=supersecretvalue123",
        )
        issues = handoff_validator.validate_handoff(self.write(text), self.root)
        self.assertIn("possible assigned secret value", issues)
        self.assertIn("missing referenced file: missing/file.md", issues)

    def test_filename_and_slug_cannot_escape_handoff_directory(self) -> None:
        issues = handoff_validator.validate_handoff(
            self.write(self.valid_text(), "nested-name.md"), self.root
        )
        self.assertIn("filename must be YYYY-MM-DD-HHMMSS-<safe-slug>.md", issues)
        self.assertEqual(handoff_validator.validated_slug("release_0.12-0"), "release_0.12-0")
        for value in ("../escape", "nested/path", " Upper", "-leading", "trailing-"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                handoff_validator.validated_slug(value)


if __name__ == "__main__":
    unittest.main()
