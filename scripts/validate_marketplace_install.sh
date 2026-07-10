#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
TMP_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/everville-marketplace-install.XXXXXX")
trap 'rm -rf "$TMP_ROOT"' EXIT

mkdir -p "$TMP_ROOT/home" "$TMP_ROOT/config" "$TMP_ROOT/xdg"
export HOME="$TMP_ROOT/home"
export CLAUDE_CONFIG_DIR="$TMP_ROOT/config"
export XDG_CONFIG_HOME="$TMP_ROOT/xdg"

claude plugin marketplace add "$REPO_ROOT" --scope user >/dev/null

PLUGINS=(
  everville-workflow@everville-workflow
  everville-handoff@everville-workflow
  everville-meta@everville-workflow
)

for plugin in "${PLUGINS[@]}"; do
  claude plugin install "$plugin" --scope user >/dev/null
done

LIST_JSON="$TMP_ROOT/plugins.json"
claude plugin list --json >"$LIST_JSON"

python3 - "$LIST_JSON" "$REPO_ROOT" <<'PY'
from pathlib import Path
import json
import sys

plugins = json.loads(Path(sys.argv[1]).read_text())
repo_root = Path(sys.argv[2])
marketplace = json.loads((repo_root / ".claude-plugin" / "marketplace.json").read_text())
marketplace_name = marketplace["name"]
expected = {
    f"{entry['name']}@{marketplace_name}": entry["version"]
    for entry in marketplace["plugins"]
}
actual = {plugin["id"]: plugin for plugin in plugins}

if set(actual) != set(expected):
    raise SystemExit(f"installed plugin set mismatch: {sorted(actual)}")

for plugin_id, version in expected.items():
    plugin = actual[plugin_id]
    if plugin.get("version") != version:
        raise SystemExit(
            f"{plugin_id}: installed {plugin.get('version')!r}, expected {version!r}"
        )
    if plugin.get("scope") != "user" or plugin.get("enabled") is not True:
        raise SystemExit(f"{plugin_id}: expected enabled isolated user install")
    install_path = Path(plugin["installPath"])
    manifest = install_path / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        raise SystemExit(f"{plugin_id}: cached manifest missing at {manifest}")

workflow = Path(actual["everville-workflow@everville-workflow"]["installPath"])
meta = Path(actual["everville-meta@everville-workflow"]["installPath"])
handoff = Path(actual["everville-handoff@everville-workflow"]["installPath"])

required = (
    workflow / "hooks" / "hooks.json",
    workflow / "skills" / "unified-workflow" / "SKILL.md",
    meta / "skills" / "everville-skill-comply" / "scripts" / "skill_comply.py",
    meta / "skills" / "everville-skill-judge" / "SKILL.md",
    handoff / "skills" / "everville-handoff" / "scripts" / "handoff_validator.py",
)
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit("cached component missing: " + ", ".join(missing))

mispackaged = (
    workflow / "skills" / "everville-skill-comply",
    workflow / "skills" / "everville-skill-judge",
    workflow / "skills" / "everville-skill-stocktake",
    workflow / "skills" / "everville-agent-md-refactor",
)
unexpected = [str(path) for path in mispackaged if path.exists()]
if unexpected:
    raise SystemExit("maintenance skill leaked into workflow plugin: " + ", ".join(unexpected))

for plugin_id in expected:
    print(actual[plugin_id]["installPath"])
PY

while IFS= read -r install_path; do
  claude plugin validate "$install_path" --strict >/dev/null
done < <(python3 - "$LIST_JSON" <<'PY'
from pathlib import Path
import json
import sys

for plugin in json.loads(Path(sys.argv[1]).read_text()):
    print(plugin["installPath"])
PY
)

for plugin in "${PLUGINS[@]}"; do
  claude plugin details "$plugin" >"$TMP_ROOT/${plugin%@*}.details.txt"
done

echo "isolated marketplace install OK (3 plugins)"
