# Everville Workflow

Shared Claude Code plugins for the Everville Estate team. Enforces a consistent development workflow across all projects (balicopter, eva.mba, everville-team-portal, etc.).

## What's inside

- **`everville-workflow`** — unified 11-step development ritual + trivial-change whitelist

More plugins (`everville-bootstrap`, `everville-e2e-discipline`, `everville-stack`) land in upcoming releases.

## Install

```bash
# Add this marketplace
claude plugin marketplace add Everville-Estate/everville-workflow

# Install the workflow plugin
claude plugin install everville-workflow@everville-workflow
```

Verify:

```bash
claude plugin list
# should show: everville-workflow (enabled)
```

## Upstream dependencies

These plugins assume you have `superpowers` installed. Install separately:

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin install superpowers@superpowers-marketplace
```

## Team

Maintainers: @nikoasta, @balicopter (Andrey), @maslennikov-ig (Igor).

## License

MIT © Everville Estate PTE LTD
