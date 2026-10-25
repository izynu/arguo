---
title: Development Setup
description: How to install the toolkit for development, build the catalog, run validators, tests, and lint.
group: developer-guide
slug: dg-setup
order: 1
---

Prerequisites. Python 3.11 or newer (pyproject.toml declares `requires-python = ">=3.11"`), pip or uv, and git. A Tavily key is optional, needed only for live web search; offline development needs none. The docs site is Next.js; bun is optional, only needed to edit or build it.

Install. Clone, create a virtual environment, and install editable with the dev extra:

```bash
git clone <your repository URL> arguo
cd arguo
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The dev extra adds pytest, pytest-asyncio, and ruff; runtime dependencies stay small: pydantic, typer, httpx.

Verify the install:

```bash
python3 -c "import arguo; print('ok')"
arguo --help
```

`arguo doctor` reports import status, configured providers, and catalog presence without any network call.

Build the catalog. Resource commands read built artifacts, not seeds, so build once after cloning:

```bash
python3 scripts/build_resource_catalog.py
```

It regenerates catalog/catalog.json, catalog/catalog.jsonl, and catalog/stats.json from the JSONL seeds in data/resources. Without it, resources commands raise ResourceCatalogError pointing at this command.

Run validators. Check one resource file against the schema rules, then the skill package:

```bash
python3 scripts/validate_catalog_file.py data/resources/academic-1.jsonl
python3 scripts/validate_skill.py all
```

`arguo resources validate` checks every file in data/resources in one pass. Both validators also enforce the standing style rules: no em dashes, no en dashes, no emoji.

Tests and lint. Run the suite and the linter:

```bash
python3 -m pytest tests/ -q
ruff check python/ tests/ scripts/ evals/ examples/
```

pyproject sets testpaths to tests, puts python on the import path, and adds `-q`. The suite is being built: until test files land, pytest reports no tests ran and exits 5. Ruff uses line length 100, target py311, rules E, F, I, UP, B, W, ignoring E501.

## Project layout

| Directory | Purpose |
| --- | --- |
| python/arguo | Python package (CLI, orchestrator, providers, models) |
| skill/ | Three skill packages: arguo (research method), arguo-curator (catalog curation), arguo-source-audit (citation auditing) |
| data/ | Resource seeds, categories, JSON schemas |
| catalog/ | Built catalog artifacts (catalog.json, catalog.jsonl, stats.json) |
| docs/ | Markdown documentation groups (getting-started, developer-guide, and others) |
| evals/ | Evaluation harness: run_evals.py, cases, fixtures, rubrics, schemas |
| examples/ | Example scripts and sample reports |
| scripts/ | Build and validator scripts |
| src/ | Next.js documentation website |
| .github/ | Issue templates and workflows |
| tests/ | Test suite (planned: unit, integration, security) and offline fixtures |
