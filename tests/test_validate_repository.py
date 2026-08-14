from __future__ import annotations

import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_repository", ROOT / "scripts" / "validate_repository.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class FrontmatterTests(unittest.TestCase):
    def test_reads_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "SKILL.md"
            path.write_text("---\nname: sample\ndescription: Useful sample\n---\nBody\n")
            fields = VALIDATOR.frontmatter(path, ("name", "description"))
            self.assertEqual(fields["name"], "sample")

    def test_rejects_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "SKILL.md"
            path.write_text("---\nname: sample\n---\nBody\n")
            with self.assertRaises(VALIDATOR.ValidationError):
                VALIDATOR.frontmatter(path, ("name", "description"))


class RepositoryInvariantTests(unittest.TestCase):
    def test_manifest_versions_and_inventory(self) -> None:
        VALIDATOR.validate_manifests()

    def test_python_sources_parse(self) -> None:
        VALIDATOR.validate_python()

    def test_spec_hardening_policy(self) -> None:
        VALIDATOR.validate_spec_hardening()

    def test_retired_runtime_surfaces_stay_removed(self) -> None:
        VALIDATOR.validate_components()
        self.assertFalse((ROOT / "scripts" / "orchestration").exists())
        self.assertFalse(
            (ROOT / "plugins" / "everville-workflow" / "commands").exists()
        )


class WorkflowPinTests(unittest.TestCase):
    def test_rejects_floating_step_action(self) -> None:
        text = "steps:\n  - uses: actions/checkout@v7\n"
        self.assertEqual(
            VALIDATOR.unpinned_external_actions(text),
            ["actions/checkout@v7"],
        )

    def test_rejects_floating_reusable_workflow(self) -> None:
        text = "jobs:\n  delegate:\n    uses: acme/ci/.github/workflows/check.yml@v1\n"
        self.assertEqual(
            VALIDATOR.unpinned_external_actions(text),
            ["acme/ci/.github/workflows/check.yml@v1"],
        )

    def test_accepts_pinned_reusable_workflow(self) -> None:
        sha = "a" * 40
        text = f"jobs:\n  delegate:\n    uses: acme/ci/.github/workflows/check.yml@{sha}\n"
        self.assertEqual(VALIDATOR.unpinned_external_actions(text), [])

    def test_accepts_local_action(self) -> None:
        text = "steps:\n  - uses: ./.github/actions/local-check\n"
        self.assertEqual(VALIDATOR.unpinned_external_actions(text), [])


if __name__ == "__main__":
    unittest.main()
