import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPO_ROOT / "plugins" / "everville-workflow" / "hooks" / "gate-check.py"


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

    def run_hook(self, payload, *, home=None, context=False):
        env = os.environ.copy()
        env["HOME"] = str(home or self.home)
        command = [sys.executable, str(HOOK)]
        if context:
            command.append("--context")
        return subprocess.run(
            command,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            env=env,
        )

    @staticmethod
    def edit_payload(cwd, path, session="session-1"):
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": "Edit",
            "session_id": session,
            "cwd": str(cwd),
            "tool_input": {"file_path": str(path)},
        }

    @staticmethod
    def bash_payload(cwd, command, session="session-1"):
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "session_id": session,
            "cwd": str(cwd),
            "tool_input": {"command": command},
        }

    def test_first_edit_is_denied_and_retry_is_allowed(self):
        repo = self.make_repo(self.base / "repo")
        payload = self.edit_payload(repo, repo / "tracked.txt")

        first = self.run_hook(payload)
        retry = self.run_hook(payload)

        self.assertEqual(first.returncode, 2)
        self.assertIn("one-time advisory", first.stderr)
        self.assertEqual(retry.returncode, 0)

    def test_marker_creation_failure_is_fail_open(self):
        repo = self.make_repo(self.base / "repo")
        invalid_home = self.base / "not-a-directory"
        invalid_home.write_text("file", encoding="utf-8")

        result = self.run_hook(
            self.edit_payload(repo, repo / "tracked.txt"), home=invalid_home
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_nested_cwd_uses_git_root_for_sibling_file(self):
        repo = self.make_repo(self.base / "repo")
        nested = repo / "packages" / "app"
        sibling = repo / "packages" / "shared" / "index.ts"
        nested.mkdir(parents=True)
        sibling.parent.mkdir(parents=True)

        result = self.run_hook(self.edit_payload(nested, sibling))

        self.assertEqual(result.returncode, 2)

    def test_linked_worktree_is_identified_from_its_own_root(self):
        repo = self.make_repo(self.base / "source")
        worktree = self.base / "linked"
        self.git(repo, "worktree", "add", "-q", "-b", "linked-test", str(worktree))
        nested = worktree / "packages" / "app"
        target = worktree / "packages" / "shared" / "index.ts"
        nested.mkdir(parents=True)
        target.parent.mkdir(parents=True)

        result = self.run_hook(self.edit_payload(nested, target))

        self.assertEqual(result.returncode, 2)

    def test_same_basename_repositories_do_not_share_marker(self):
        first_repo = self.make_repo(self.base / "one" / "project")
        second_repo = self.make_repo(self.base / "two" / "project")

        first = self.run_hook(
            self.edit_payload(first_repo, first_repo / "tracked.txt", "same-session")
        )
        second = self.run_hook(
            self.edit_payload(second_repo, second_repo / "tracked.txt", "same-session")
        )

        self.assertEqual(first.returncode, 2)
        self.assertEqual(second.returncode, 2)

    def test_remote_identity_change_does_not_reuse_marker(self):
        repo = self.make_repo(self.base / "repo")
        payload = self.edit_payload(repo, repo / "tracked.txt", "same-session")

        first = self.run_hook(payload)
        self.git(
            repo,
            "remote",
            "set-url",
            "origin",
            "git@github.com:Everville-Estate/renamed.git",
        )
        renamed_remote = self.run_hook(payload)

        self.assertEqual(first.returncode, 2)
        self.assertEqual(renamed_remote.returncode, 2)

    def test_lowercase_owner_is_recognized(self):
        repo = self.make_repo(
            self.base / "repo", "https://github.com/everville-estate/example.git"
        )

        result = self.run_hook(self.edit_payload(repo, repo / "tracked.txt"))

        self.assertEqual(result.returncode, 2)

    def test_similar_owner_or_non_github_host_is_not_recognized(self):
        similar = self.make_repo(
            self.base / "similar",
            "https://github.com/not-everville-estate/example.git",
        )
        other_host = self.make_repo(
            self.base / "other-host",
            "https://gitlab.com/Everville-Estate/example.git",
        )

        self.assertEqual(
            self.run_hook(self.edit_payload(similar, similar / "tracked.txt")).returncode,
            0,
        )
        self.assertEqual(
            self.run_hook(
                self.edit_payload(other_host, other_host / "tracked.txt")
            ).returncode,
            0,
        )

    def test_exemptions_are_anchored_to_repo_relative_prefixes(self):
        repo = self.make_repo(self.base / "repo")
        root_memory = repo / "memory" / "note.md"
        production_memory = repo / "src" / "memory" / "store.ts"
        root_memory.parent.mkdir()
        production_memory.parent.mkdir(parents=True)

        exempt = self.run_hook(self.edit_payload(repo, root_memory, "exempt"))
        production = self.run_hook(
            self.edit_payload(repo, production_memory, "production")
        )

        self.assertEqual(exempt.returncode, 0)
        self.assertEqual(production.returncode, 2)

    def test_file_outside_repository_is_not_gated(self):
        repo = self.make_repo(self.base / "repo")
        outside = self.base / "repo-other" / "file.ts"
        outside.parent.mkdir()

        result = self.run_hook(self.edit_payload(repo, outside))

        self.assertEqual(result.returncode, 0)

    def test_non_everville_repo_gets_no_gate_or_session_context(self):
        repo = self.make_repo(
            self.base / "repo", "https://github.com/example/example.git"
        )
        payload = self.edit_payload(repo, repo / "tracked.txt")

        edit = self.run_hook(payload)
        context = self.run_hook({"cwd": str(repo)}, context=True)

        self.assertEqual(edit.returncode, 0)
        self.assertEqual(context.returncode, 0)
        self.assertEqual(context.stdout, "")

    def test_session_context_is_emitted_only_for_everville_repo(self):
        repo = self.make_repo(self.base / "repo")

        result = self.run_hook({"cwd": str(repo)}, context=True)

        self.assertEqual(result.returncode, 0)
        self.assertIn("<everville-workflow-gate>", result.stdout)

    def test_common_mutating_bash_is_gated_but_read_only_bash_is_not(self):
        repo = self.make_repo(self.base / "repo")

        read_only = self.run_hook(
            self.bash_payload(repo, "git status --short", "read-only")
        )
        mutation = self.run_hook(
            self.bash_payload(repo, "sed -i.bak 's/a/b/' tracked.txt", "mutation")
        )
        retry = self.run_hook(
            self.bash_payload(repo, "sed -i.bak 's/a/b/' tracked.txt", "mutation")
        )

        self.assertEqual(read_only.returncode, 0)
        self.assertEqual(mutation.returncode, 2)
        self.assertEqual(retry.returncode, 0)

    def test_redirection_and_interpreter_bash_are_conservatively_gated(self):
        repo = self.make_repo(self.base / "repo")

        redirect = self.run_hook(
            self.bash_payload(repo, "printf x > generated.txt", "redirect")
        )
        interpreter = self.run_hook(
            self.bash_payload(repo, "python3 -c 'print(1)'", "interpreter")
        )

        self.assertEqual(redirect.returncode, 2)
        self.assertEqual(interpreter.returncode, 2)

    def test_multiline_mutating_bash_is_gated(self):
        repo = self.make_repo(self.base / "repo")

        result = self.run_hook(
            self.bash_payload(repo, "git status --short\ntouch generated.txt", "multiline")
        )

        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
