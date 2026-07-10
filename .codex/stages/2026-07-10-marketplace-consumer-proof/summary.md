# Stage Summary - 2026-07-10 marketplace consumer proof

Objective: close the final local evidence gap by proving that this exact checkout installs and resolves correctly through Claude Code's consumer-facing marketplace commands.

## Execution decision

This was a simple sequential local verification stage: one isolated install script, one CI integration point, and the corresponding verification/documentation references share a single packaging contract. Delegation would add no isolation or parallelism benefit.

## Outcome

- Added `scripts/validate_marketplace_install.sh`.
- The script creates a disposable Claude configuration, adds the checkout as a local marketplace, installs all marketplace entries, derives expected versions from the marketplace manifest, verifies enabled cached installs and required packaged files, rejects maintenance-skill leakage into the workflow plugin, strictly validates each cached plugin, and resolves each consumer-facing plugin detail page.
- Isolated installation passed for `everville-workflow` 0.12.0, `everville-handoff` 0.4.0, and `everville-meta` 0.3.0.
- CI and repo closeout now run this consumer-install gate.
- The normal user Claude configuration was not read or modified by the test.

project-index: updated with the durable consumer-install entrypoint.

## Explicit defers

- Task tracked by Codex goal `019f4ad4-1f14-7041-81e1-eb91c641b137`: GitHub `main` protection and rulesets remain absent and require explicit owner authorization before remote mutation.
