---
title: Contributing Code
description: Setup for contributors, branch naming, commit style, the pull request checklist, and what reviewers look for.
group: developer-guide
slug: dg-contributing-code
order: 12
---

Setup. Follow Development Setup: clone the repository, create a virtual environment, install with `pip install -e ".[dev]"`, build the catalog with `python3 scripts/build_resource_catalog.py`, then run pytest and ruff once before you start so you work from a known state. Keep the offline path working; any change that breaks `--offline` runs breaks the tests too.

Branch naming. Prefix branches with the change type: `feat/`, `fix/`, or `docs/`, followed by a short hyphenated name, for example `feat/exa-search-provider`, `fix/cache-key-collision`, or `docs/output-schemas`.

Commit style. Use conventional commits: a type, a colon, and an imperative subject with no trailing period. Types in use are feat, fix, docs, test, refactor, and chore. Examples: `feat: add Exa search provider`, `fix: redact API keys in retrieval warnings`, `docs: document eval harness metrics`. Use the body to explain behavior changes and anything a downstream consumer must adjust.

Pull request checklist.

- Tests for the change are added and passing: `python3 -m pytest tests/ -q`.
- `ruff check python/ tests/ scripts/ evals/ examples/` reports no findings in the files you changed.
- Standing style rules are respected everywhere in the diff: no em dashes, no en dashes, no emoji, in code, comments, docs, and fixtures alike.
- Documentation is updated when behavior changes: the CLI reference, config reference, output schemas, or Python API pages as applicable.
- Fixtures and examples contain only placeholder example.org style data; no invented URLs, metrics, or test results.

Code review focus. Reviewers look first at contract stability: models set `extra="forbid"`, so new fields must be optional with None defaults, and the ledger id scheme S{n}, E{n}, C{n} plus the artifact layout stay unchanged. Exception usage must stay typed: raise only EvidenceLedgerError subclasses with a hint and a documented exit code, never bare Exception or SDK types. There are no print statements outside the CLI module; diagnostics go through utilities.logging. Finally, no network at import time: importing any module must not open sockets, and provider constructors perform no network activity.
