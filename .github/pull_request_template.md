## Why

<!-- What problem or risk does this change address? -->

## What

<!-- Summarize behavior changes and affected plugins. -->

## Verification

- [ ] `python3 -m unittest discover -s tests -p 'test_*.py'`
- [ ] `python3 scripts/validate_repository.py`
- [ ] Marketplace and affected plugins pass `claude plugin validate`
- [ ] Runtime behavior changes include deterministic tests
- [ ] Independent reviewer is not the implementer

## Release and risk

- [ ] Affected plugin versions are bumped in both manifests
- [ ] External side effects and rollback are documented
- [ ] Any skipped step or accepted risk is named explicitly
- [ ] No direct push to `main`; merge through reviewed PR
