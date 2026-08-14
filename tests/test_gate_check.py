import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "plugins" / "everville-workflow" / "hooks" / "gate-check.py"
HOOKS = REPO_ROOT / "plugins" / "everville-workflow" / "hooks" / "hooks.json"


class GateCheckTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.base = Path(self.tempdir.name)
        self.home = self.base / "home"
        self.home.mkdir()

    def tearDown(self):
        self.tempdir.cleanup()

    def git(self, repo, *args):
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def make_repo(self, path, remote="git@github.com:Everville-Estate/example.git"):
        path.mkdir(parents=True)
        self.git(path, "init", "-q")
        self.git(path, "config", "user.email", "test@example.com")
        self.git(path, "config", "user.name", "Gate Test")
        self.git(path, "remote", "add", "origin", remote)
        (path / "tracked.txt").write_text("initial\n", encoding="utf-8")
        self.git(path, "add", "tracked.txt")
        self.git(path, "commit", "-qm", "initial")
        return path

    def run_hook(self, cwd, *, env_extra=None):
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env.update(env_extra or {})
        return subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps(
                {
                    "hook_event_name": "SessionStart",
                    "session_id": "session-1",
                    "cwd": str(cwd),
                }
            ),
            capture_output=True,
            text=True,
            env=env,
        )

    def assert_context(self, result):
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")
        self.assertIn("<everville-workflow-context>", result.stdout)
        self.assertIn("verified Everville-Estate GitHub repository", result.stdout)
        self.assertIn("BYPASS, LIGHT, or FULL", result.stdout)

    def test_hooks_register_only_session_start(self):
        hooks = json.loads(HOOKS.read_text(encoding="utf-8"))["hooks"]

        self.assertEqual(list(hooks), ["SessionStart"])

    def test_verified_everville_repo_gets_short_factual_context(self):
        repo = self.make_repo(self.base / "repo")

        result = self.run_hook(repo)

        self.assert_context(result)
        self.assertNotIn("PreToolUse", result.stdout)
        self.assertNotIn("before ANY code change", result.stdout)

    def test_non_everville_and_non_repository_get_no_context(self):
        external = self.make_repo(
            self.base / "external", "https://github.com/example/example.git"
        )
        not_repo = self.base / "not-repo"
        not_repo.mkdir()

        self.assertEqual(self.run_hook(external).stdout, "")
        self.assertEqual(self.run_hook(not_repo).stdout, "")

    def test_remote_identity_is_live_not_session_cached(self):
        repo = self.make_repo(self.base / "repo")

        first = self.run_hook(repo)
        self.git(
            repo,
            "remote",
            "set-url",
            "origin",
            "https://github.com/example/example.git",
        )
        changed = self.run_hook(repo)

        self.assert_context(first)
        self.assertEqual(changed.stdout, "")

    def test_nested_included_origin_change_is_seen_live(self):
        repo = self.make_repo(self.base / "repo")
        first_include = self.base / "first.inc"
        everville = self.base / "everville.inc"
        external = self.base / "external.inc"
        everville.write_text(
            '[remote "origin"]\n\turl = git@github.com:Everville-Estate/example.git\n',
            encoding="utf-8",
        )
        external.write_text(
            '[remote "origin"]\n\turl = https://github.com/example/example.git\n',
            encoding="utf-8",
        )
        first_include.write_text(f"[include]\n\tpath = {everville}\n", encoding="utf-8")
        self.git(repo, "config", "--unset-all", "remote.origin.url")
        self.git(repo, "config", "include.path", str(first_include))

        first = self.run_hook(repo)
        first_include.write_text(f"[include]\n\tpath = {external}\n", encoding="utf-8")
        changed = self.run_hook(repo)

        self.assert_context(first)
        self.assertEqual(changed.stdout, "")

    def test_ssh_aliases_are_not_evaluated(self):
        for remote in (
            "git@github-work:Everville-Estate/example.git",
            "ssh://git@github-work/Everville-Estate/example.git",
        ):
            with self.subTest(remote=remote):
                repo = self.make_repo(self.base / str(len(remote)), remote)
                result = self.run_hook(repo)
                self.assertEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertEqual(result.stderr, "")

    def test_canonical_looking_local_path_is_not_a_remote(self):
        repo = self.make_repo(
            self.base / "repo", "github.com/everville-estate/example"
        )

        self.assertEqual(self.run_hook(repo).stdout, "")

    def test_linked_worktree_uses_its_own_root(self):
        repo = self.make_repo(self.base / "source")
        worktree = self.base / "linked"
        self.git(repo, "worktree", "add", "-q", "-b", "linked-test", str(worktree))

        result = self.run_hook(worktree)

        self.assert_context(result)

    def test_missing_git_fails_open(self):
        repo = self.make_repo(self.base / "repo")

        result = self.run_hook(repo, env_extra={"PATH": str(self.base / "empty-bin")})

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
