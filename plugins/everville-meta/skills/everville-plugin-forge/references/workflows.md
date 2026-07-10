# Plugin development workflows

## Add or change a plugin

1. Create a dedicated branch from the current reviewed base.
2. Search existing components and read any candidate upstream source completely.
3. Specify prerequisites, side effects, state location, cleanup, permissions, and external-write boundaries.
4. Add the component under the plugin root and register only non-default paths in `plugin.json`.
5. For an action skill, add `disable-model-invocation: true` when it commits, deploys, publishes, sends, deletes, creates PRs, or changes remote state.
6. Preserve source attribution below frontmatter and the upstream license under `LICENSES/`.
7. Bump both the plugin manifest and marketplace entry versions.

## Validate

```bash
claude plugin validate . --strict
claude plugin validate plugins/<plugin-name> --strict
git diff --check
```

Then run component-specific checks:

- parse every changed `SKILL.md` frontmatter block;
- feed fixture JSON to hook commands and assert exit/output behavior;
- test missing dependencies and unwritable state directories;
- inspect any tool permissions, network calls, and secret handling;
- verify generated files stay in the documented directory;
- verify no command mutates GitHub or another external system without explicit authorization.

First-party validation checks manifests. It does not replace these behavioral tests.

## Test an unpublished checkout

Use a local marketplace source or launch a temporary Claude Code session with the plugin directory. Do not edit files in `~/.claude/plugins/cache`; they are copies, not source.

After changing an in-place skills-directory plugin, skill body changes can be detected during a session. Hooks, agents, MCP/LSP components, and other non-skill changes require `/reload-plugins` or restart. After `claude plugin update`, restart Claude Code.

## Release

1. Review the full diff and validation evidence.
2. Commit on the feature branch.
3. Open a pull request when authorized; do not push directly to `main`.
4. Obtain required independent review and CI.
5. Merge through repository policy.
6. Update the marketplace and installed plugin.
7. Restart/reload and verify the installed version and component inventory.

The forge workflow never grants implicit authority to push, open/edit a PR, merge, publish, or install a plugin for other users. Those are separate actions governed by the user's request and repository policy.

## Rollback

If a release misbehaves, disable the plugin first to stop new sessions from loading it, then revert through a reviewed change or install the last known-good version according to team policy. Persistent data under `${CLAUDE_PLUGIN_DATA}` is not automatically removed by uninstall; use `--keep-data` deliberately and document any cleanup.
