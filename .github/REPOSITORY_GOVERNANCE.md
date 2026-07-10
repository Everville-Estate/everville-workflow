# Repository Governance

Required GitHub settings for `main`:

- Require a pull request before merging.
- Require at least one approval from someone other than the author.
- Dismiss stale approvals when new commits are pushed.
- Require review conversations to be resolved.
- Require the `Validate marketplace / validate` status check.
- Require the branch to be up to date before merge.
- Block force pushes and branch deletion.
- Apply the rules to administrators.

`CODEOWNERS` defines the default reviewers, but GitHub must enforce the settings above through branch protection or an organization ruleset. Repository files cannot activate those remote controls by themselves.

Release policy:

1. Merge only through a reviewed PR with green validation.
2. Confirm the affected marketplace and plugin manifest versions match.
3. Tag each changed plugin as `<plugin-name>@v<version>` after merge.
4. Update installed clients with `claude plugin marketplace update everville-workflow` followed by `claude plugin update <plugin>@everville-workflow`.
5. Never reuse a published version number; Claude Code caches marketplace plugins by version.
