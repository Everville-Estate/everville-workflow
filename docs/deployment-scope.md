# Deployment scope

This is the operational boundary for the Everville Workflow marketplace. Repository paths are a 2026-08-14 workstation audit snapshot; GitHub organization identity, not a local folder name, is the durable authority.

## Plugin scopes

- `everville-workflow`: install at **project** scope only in a canonical repository whose effective `origin` resolves to `github.com/Everville-Estate/*`.
- `everville-meta`: install at **local** scope only in the canonical `Everville-Estate/everville-workflow` maintainer checkout.
- `everville-handoff`: may remain at **user** scope because it is explicit-only and writes nothing unless invoked.

Never enable the workflow globally. A checkout, folder, worktree, or stale clone does not become governed merely because its name contains `everville`.

## Verified canonical targets

The audit found 22 unique canonical/current Git repositories intended for project-scope workflow enablement:

`niko-health`, `private-coach`, `dev-environment`, `content-factory`, `everville`, `bali-bankruptcy`, `citadel-site`, `eva-mba`, `everville-core`, `everville-smm-brightbean`, `everville-website`, `everville-workflow`, `goodguys-core`, `jaga`, `mix-florist`, `ocean-directory`, `property-catalogue`, `roya-business`, `roya-resort`, `roya-surf`, `vibe-stack`, and `roya-resort-investor-presentation`.

Linked worktrees share project configuration with their common Git repository and are not separate installation targets.

`private-coach` was normalized during the audit from a local SSH alias to the canonical `git@github.com:Everville-Estate/private-coach.git` remote after direct read access was verified. The hook deliberately does not evaluate SSH configuration or accept alias hosts.

## Exclusions

- Nine older duplicate clones under `Developer/work/CORE-DEV` are not installation targets. Reconcile or retire them separately; do not add plugin configuration.
- Thirteen audited non-Everville repositories must not enable the workflow.
- Six adjacent repositories with personal/no remote identity (`atman-villa`, `baseline`, `cash-on-rails-mini-film`, `everville-atlas`, `everville-macbook-neo-rollout`, `everville-merge-src`) remain out of scope until their governance is explicitly decided and their remote identity is verifiable.
- Dormant prose that names a workflow skill is not evidence that the plugin is installed or active.

## Rollout gate

Project installations must use a merged, validated marketplace release. Before enabling a new version:

1. Verify the repository's effective `origin` and common Git directory.
2. Exclude stale duplicate clones and non-Everville remotes.
3. Install/update at the scope above.
4. Reload plugins or restart Claude Code.
5. Confirm `claude plugin list --json`, `/hooks`, and one SessionStart context check on the actual repository surface.

Do not use an unmerged feature checkout as the persistent marketplace source.
