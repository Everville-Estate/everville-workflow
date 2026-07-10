# Marketplace schema reference

The catalog lives at `.claude-plugin/marketplace.json` in the repository root.

## Minimal shape

```json
{
  "name": "everville-workflow",
  "owner": {
    "name": "Everville Estate PTE LTD",
    "email": "niko@everville.estate"
  },
  "plugins": [
    {
      "name": "example-plugin",
      "source": "./plugins/example-plugin",
      "description": "What the plugin adds",
      "version": "0.1.0",
      "author": { "name": "Everville Estate PTE LTD" }
    }
  ]
}
```

The marketplace requires `name`, `owner`, and `plugins`. Each local entry requires a stable `name` and a `source` relative to the marketplace root. Keep the entry's version synchronized with the source plugin's `.claude-plugin/plugin.json`; the plugin manifest version takes precedence when both are present.

Use only fields accepted by the installed Claude Code schema. Confirm the current contract rather than copying metadata from npm, VS Code, or an old marketplace example:

```bash
claude plugin validate . --strict
```

Without `--strict`, unrecognized fields are warnings and the marketplace may still load. Strict mode is the release gate.

## Distribution and scopes

Add the GitHub marketplace with:

```bash
claude plugin marketplace add Everville-Estate/everville-workflow
```

Install a catalog entry with an explicit scope:

```bash
claude plugin install example-plugin@everville-workflow --scope project
```

- `user`: available across projects; CLI install default
- `project`: shared project configuration
- `local`: project-specific, normally gitignored
- `managed`: organization-controlled; updates are policy-owned

Choose scope according to the plugin's hooks, context cost, network access, and side effects. A team workflow normally belongs at project or managed scope, not silently at user scope.

## Updating

```bash
claude plugin marketplace update everville-workflow
claude plugin update example-plugin@everville-workflow --scope project
```

Installed updates require restart to apply. Mid-session plugin processes may retain the previous cached path until reload or restart.
