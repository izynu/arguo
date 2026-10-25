# Contributing to Arguo

Thanks for considering a contribution. This document covers setup, conventions, and the review process. For the research method and catalog policies, see the docs site content under `docs/`.

## Setup

1. Fork the repository, then clone your fork (if you work from a fork, replace `izynu` with your own handle in the URL):

   ```bash
   git clone https://github.com/izynu/arguo.git
   cd arguo
   ```

2. Create a virtual environment and install with dev dependencies:

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   ```

3. Confirm everything is green before you start:

   ```bash
   make test        # 167 offline tests
   make lint        # ruff over python/, tests/, scripts/, evals/, examples/
   make validate    # resource and skill validators
   ```

4. Optional: enable the pre-commit hooks:

   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Branch naming

Name branches by change type, with a short kebab-case topic:

- `feat/short-topic`: new behavior or new commands
- `fix/short-topic`: bug fixes
- `docs/short-topic`: documentation only
- `chore/short-topic`: tooling, CI, dependencies, housekeeping

## Conventional commits

Write commit messages as `type(scope): summary`. Examples used in this repository:

```text
feat(cli): add --since and --until date bounds to research
fix(catalog): drop duplicate canonical_url records during merge
docs(quickstart): correct the offline run example
chore(ci): add scheduled resource validation workflow
```

Scope is optional but helpful: `cli`, `pipeline`, `catalog`, `skill`, `site`, `docs`, `ci`.

## Style rules for all authored copy

These are enforced by `tools/style_check.py`, in pre-commit, and in CI:

- No em dashes. Use hyphens, colons, or commas.
- No en dashes. Same substitutes.
- No emoji anywhere in code, docs, UI text, or commit messages.
- No invented numbers, test results, URLs, or review quotes. Every count must come from a real file or a real run.

## Pull request checklist

Before you open a PR, confirm:

- [ ] `make test` passes (pytest, currently 167 tests, fully offline)
- [ ] `make lint` is clean (ruff, no new findings)
- [ ] `make validate` passes (resource validators and skill validator)
- [ ] No em dashes, no en dashes, no emoji in any changed file
- [ ] Documentation is updated when behavior or counts change
- [ ] Any new or changed catalog records pass `scripts/validate_catalog_file.py`
- [ ] No secrets, API keys, or personal data in the diff
- [ ] The PR description states what changed and why

## Adding a catalog resource

The catalog is authored in `data/resources/*.jsonl`, one JSON record per line, validated against `data/schemas/resource.schema.json`.

1. Pick the authoring file that matches the category, or start a new file named `topic-n.jsonl` if none fits.
2. Add one JSON object per line with the fields required by the schema. Every record needs a unique `id`, a `name`, a `category` from `data/categories.json`, an `https` `canonical_url`, and verification status `documented` unless you have actually live-checked the URL.
3. Record provenance honestly. Do not copy third-party content beyond metadata. If the license is unknown, record the literal string `unknown`.
4. Validate your file:

   ```bash
   python3 scripts/validate_catalog_file.py data/resources/your-file.jsonl
   ```

5. Rebuild and check the merged outputs:

   ```bash
   python3 scripts/build_resource_catalog.py
   ```

   Cross-file duplicate ids and URLs are dropped with an audit trail. Reviewers check the dedupe lines.

Review criteria for catalog records: official source preferred, canonical URL is the stable official one, description is factual, category and region are correct, no marketing language, and no fabricated fields. Fabricating records to increase counts is grounds for rejection.

## Adding an eval case

Eval cases live in `evals/cases/*.json`. Each file holds a list of cases with an id, a question, fixture-based expected behavior, and structural checks. To add one:

1. Choose the topical file or start a new one.
2. Add a case with a unique id, a realistic question, and the minimum evidence fixtures needed to exercise the behavior. Use placeholder domains such as `example.org` in fixtures. Never real URLs with private content.
3. State `expected_behavior` as an observable property of the artifacts, for example "Report should not cite S2 for claim A".
4. Run the harness offline:

   ```bash
   python3 evals/run_evals.py --offline
   ```

Cases must run fully offline. A case that requires network access does not fit this harness.

## Review process

- A maintainer or, later, an approved reviewer reviews every PR.
- Review focuses on correctness against the docs, honesty of counts and claims, test coverage, and the style rules above.
- Changes to the Python package's public models, exit codes, or CLI surface need a stated reason in the PR description because downstream docs and tests depend on them.
- Small, safe fixes (typos, doc clarifications) can be merged after a single approval. Larger changes follow the decision process in [GOVERNANCE.md](GOVERNANCE.md).

## No CLA

There is no Contributor License Agreement. By opening a PR you agree that your contribution is licensed under the Apache-2.0 license of this repository.
