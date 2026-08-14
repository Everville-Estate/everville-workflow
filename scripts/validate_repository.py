#!/usr/bin/env python3
"""Dependency-free structural validation for the plugin marketplace."""

from __future__ import annotations

import ast
import json
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
WORKFLOW_USES_RE = re.compile(
    r"^\s*(?:-\s*)?uses:\s*(?P<value>[^#]+?)\s*(?:#.*)?$", re.MULTILINE
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((?P<target>[^)]+)\)")
SPEC_HARDENING_DIR = (
    ROOT / "plugins" / "everville-workflow" / "skills" / "everville-spec-hardening"
)


class ValidationError(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def display_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def load_json(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{display_path(path)}: invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{display_path(path)}: expected a JSON object")
    return value


def frontmatter(path: pathlib.Path, required: tuple[str, ...]) -> dict[str, str]:
    text = path.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail(f"{display_path(path)}: missing leading YAML frontmatter")

    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"\'')

    missing = [key for key in required if not fields.get(key)]
    if missing:
        fail(f"{display_path(path)}: missing frontmatter fields {', '.join(missing)}")
    return fields


def validate_manifests() -> None:
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    marketplace = load_json(marketplace_path)
    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or not entries:
        fail(".claude-plugin/marketplace.json: plugins must be a non-empty list")

    names: set[str] = set()
    registered_sources: set[pathlib.Path] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail(".claude-plugin/marketplace.json: every plugin entry must be an object")
        name = entry.get("name")
        source = entry.get("source")
        version = entry.get("version")
        if not all(isinstance(item, str) and item for item in (name, source, version)):
            fail(".claude-plugin/marketplace.json: plugin name/source/version are required strings")
        if name in names:
            fail(f".claude-plugin/marketplace.json: duplicate plugin {name}")
        names.add(name)

        plugin_root = (ROOT / source).resolve()
        if ROOT not in plugin_root.parents:
            fail(f"plugin {name}: source escapes repository")
        registered_sources.add(plugin_root)
        manifest = load_json(plugin_root / ".claude-plugin" / "plugin.json")
        if manifest.get("name") != name:
            fail(f"plugin {name}: manifest name is {manifest.get('name')!r}")
        if manifest.get("version") != version:
            fail(
                f"plugin {name}: marketplace version {version} != manifest version "
                f"{manifest.get('version')}"
            )

    actual_sources = {
        path.parent.parent.resolve()
        for path in (ROOT / "plugins").glob("*/.claude-plugin/plugin.json")
    }
    unregistered = sorted(actual_sources - registered_sources)
    if unregistered:
        fail("unregistered plugin directories: " + ", ".join(str(path.relative_to(ROOT)) for path in unregistered))


def validate_components() -> None:
    removed_surfaces = (
        ROOT / "scripts" / "orchestration",
        ROOT / "plugins" / "everville-workflow" / "commands",
    )
    present = [display_path(path) for path in removed_surfaces if path.exists()]
    if present:
        fail("retired orchestration/command surfaces returned: " + ", ".join(present))

    for path in sorted(ROOT.glob("plugins/*/skills/*/SKILL.md")):
        fields = frontmatter(path, ("name", "description"))
        if not re.fullmatch(r"[a-z0-9-]{1,64}", fields["name"]):
            fail(f"{path.relative_to(ROOT)}: invalid skill name {fields['name']!r}")

    for path in sorted(ROOT.glob("plugins/*/commands/**/*.md")):
        frontmatter(path, ("description",))

    for path in sorted(ROOT.glob("plugins/*/agents/*.md")):
        frontmatter(path, ("name", "description", "tools", "model"))

    for path in sorted(ROOT.glob("plugins/*/hooks/hooks.json")):
        hooks = load_json(path).get("hooks")
        if not isinstance(hooks, dict) or not hooks:
            fail(f"{path.relative_to(ROOT)}: hooks must be a non-empty object")

    dead_context = sorted(ROOT.glob("plugins/*/CLAUDE.md"))
    if dead_context:
        fail(
            "plugin-root CLAUDE.md is not loaded by Claude Code: "
            + ", ".join(str(path.relative_to(ROOT)) for path in dead_context)
        )

    explicit_only = (
        ROOT / "plugins/everville-workflow/skills/loop-on-ci/SKILL.md",
        ROOT / "plugins/everville-workflow/skills/explain-pr-changes/SKILL.md",
    )
    for path in explicit_only:
        fields = frontmatter(path, ("description", "disable-model-invocation"))
        if fields["disable-model-invocation"].lower() != "true":
            fail(f"{display_path(path)}: remote-capable component must be explicit-only")


def validate_spec_hardening(skill_dir: pathlib.Path = SPEC_HARDENING_DIR) -> None:
    expected = {
        "SKILL.md",
        "references/boundary-review.md",
        "references/decision-coverage.md",
        "references/delivery.md",
    }
    actual = {
        path.relative_to(skill_dir).as_posix()
        for path in skill_dir.rglob("*")
        if path.is_file()
    }
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        fail(
            "everville-spec-hardening: invalid package inventory "
            f"(missing={missing}, extra={extra})"
        )

    skill_path = skill_dir / "SKILL.md"
    text = skill_path.read_text()
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail("everville-spec-hardening/SKILL.md: missing frontmatter")
    keys = {
        line.split(":", 1)[0].strip()
        for line in match.group("body").splitlines()
        if line and not line[0].isspace() and ":" in line
    }
    if keys != {"name", "description"}:
        fail(f"everville-spec-hardening: frontmatter keys must be name/description, got {sorted(keys)}")

    for relative in sorted(expected - {"SKILL.md"}):
        target = skill_dir / relative
        if f"({relative})" not in text:
            fail(f"everville-spec-hardening: SKILL.md does not directly link {relative}")
        if MARKDOWN_LINK_RE.search(target.read_text()):
            fail(f"everville-spec-hardening: references must not chain links: {relative}")

    for link in MARKDOWN_LINK_RE.finditer(text):
        raw_target = link.group("target").split("#", 1)[0]
        if not raw_target or raw_target.startswith(("#", "http://", "https://")):
            continue
        resolved = (skill_dir / raw_target).resolve()
        if skill_dir.resolve() not in resolved.parents or not resolved.is_file():
            fail(f"everville-spec-hardening: unsafe or missing local link: {raw_target!r}")
        relative = resolved.relative_to(skill_dir.resolve()).as_posix()
        if relative not in expected:
            fail(f"everville-spec-hardening: unregistered local link: {raw_target!r}")

    lowered = "\n".join(
        path.read_text(errors="ignore")
        for path in skill_dir.rglob("*")
        if path.is_file()
    ).lower()
    required = (
        "**review**",
        "**harden**",
        "**deliver**",
        "**ready**",
        "**ready with explicit defers**",
        "**not ready**",
        "external mutations require separate explicit authority",
        "subagents are optional",
        "never request or persist full, private",
        "do not create a parallel status ledger",
    )
    for phrase in required:
        if phrase not in lowered:
            fail(f"everville-spec-hardening: required policy is absent: {phrase!r}")

    fingerprints = (
        "spec-interrogation",
        "spec-cross-cutting-review",
        "spec-reconciliation",
        "spec-synthesis",
        "sp1-the-spine",
        "gdd-lead-prompt",
        "actualize readme",
        "full subagent analysis",
        "prioritize: must > should > add",
        "the eight dimensions",
        "feed-forward validation",
    )
    for phrase in fingerprints:
        if phrase in lowered:
            fail(f"everville-spec-hardening: forbidden source fingerprint: {phrase!r}")


def validate_python() -> None:
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            ast.parse(path.read_text(), filename=str(path))
        except SyntaxError as exc:
            fail(f"{path.relative_to(ROOT)}: Python syntax error: {exc}")


def unpinned_external_actions(text: str) -> list[str]:
    issues: list[str] = []
    for match in WORKFLOW_USES_RE.finditer(text):
        value = match.group("value").strip().strip("\"'")
        if value.startswith(("./", "docker://")):
            continue
        if "@" not in value:
            issues.append(value)
            continue
        source, ref = value.rsplit("@", 1)
        if "/" not in source or not re.fullmatch(r"[0-9a-f]{40}", ref):
            issues.append(value)
    return issues


def validate_workflow_action_pins() -> None:
    workflows = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
    workflows += sorted((ROOT / ".github" / "workflows").glob("*.yaml"))
    for path in workflows:
        for action in unpinned_external_actions(path.read_text()):
            fail(f"{display_path(path)}: external action is not SHA-pinned: {action}")


def validate_docs_and_policy() -> None:
    active_markdown = [
        path
        for path in ROOT.rglob("*.md")
        if ".git" not in path.parts
        and "archive" not in path.parts
        and "LICENSES" not in path.parts
    ]
    combined = "\n".join(path.read_text(errors="ignore") for path in active_markdown)
    stale = {
        "TRIVIAL/LIGHT/FULL": "obsolete workflow verdict name",
        "plugin-level rules (loaded on enable)": "plugin-root CLAUDE.md runtime claim",
        "session_start, before_tool_use": "obsolete hook event names",
        "git push origin main": "direct-to-main publishing instruction",
        "pip install pyyaml": "undeclared runtime dependency instruction",
    }
    for needle, label in stale.items():
        if needle.lower() in combined.lower():
            fail(f"active documentation contains {label}: {needle!r}")

    stale_commands = {
        r"(?<![A-Za-z0-9_.-])/explain-pr-changes\b": "unnamespaced installed command",
        r"(?<![A-Za-z0-9_.-])/loop-on-ci\b": "unnamespaced explicit skill command",
    }
    for pattern, label in stale_commands.items():
        if re.search(pattern, combined):
            fail(f"active documentation contains {label}")

    readme = (ROOT / "README.md").read_text()
    for token in (
        "BYPASS",
        "LIGHT",
        "FULL",
        "--scope project",
        "everville-handoff",
        "everville-meta",
        "validate_marketplace_install.sh",
    ):
        if token not in readme:
            fail(f"README.md: missing first-time onboarding token {token!r}")

    judge = ROOT / "plugins/everville-meta/skills/everville-skill-judge/SKILL.md"
    if len(judge.read_text().splitlines()) > 500:
        fail("everville-skill-judge/SKILL.md exceeds its own 500-line quality ceiling")

    validate_workflow_action_pins()


def validate_filesystem() -> None:
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            fail(f"unexpected symlink: {path.relative_to(ROOT)}")


def main() -> int:
    checks = (
        validate_manifests,
        validate_components,
        validate_spec_hardening,
        validate_python,
        validate_docs_and_policy,
        validate_filesystem,
    )
    try:
        for check in checks:
            check()
    except ValidationError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"repository validation OK ({len(checks)} groups)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
