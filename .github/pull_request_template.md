## Summary

Describe what this PR changes and why. Link the issue it closes if there is one.

## Type of change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds behavior)
- [ ] Breaking change (fix or feature that changes existing behavior, models, exit codes, or CLI surface)
- [ ] Documentation only
- [ ] Catalog data (records under `data/resources/`)
- [ ] Tooling, CI, or dependencies

## Checklist

- [ ] `make test` passes (pytest, fully offline)
- [ ] `make lint` is clean (ruff, no new findings)
- [ ] `make validate` passes (resource and skill validators)
- [ ] No em dashes, no en dashes, no emoji in any changed file
- [ ] Docs updated where behavior or counts changed
- [ ] New or changed catalog records pass `python3 scripts/validate_catalog_file.py`
- [ ] Counts and claims in the diff come from real files or real runs (no invented numbers, URLs, or test results)
- [ ] No secrets, API keys, or personal data in the diff
- [ ] Commit messages follow conventional commits, branch follows `feat|fix|docs|chore/topic`
