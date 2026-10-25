---
title: Installation
description: Prerequisites, clone and install steps, verification commands, and optional API key setup.
group: getting-started
slug: gs-installation
order: 2
---

## Prerequisites

- Python 3.11 or newer (the package declares `requires-python = ">=3.11"`).
- pip, or uv if you prefer a faster installer.
- Git to clone the repository.
- Network access for live research runs. Offline mode works without it.

## Install from the repository

```bash
git clone <your repository URL> arguo
cd arguo
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The editable install registers two things: the `arguo` distribution and the `arguo` console script, which points at `arguo.cli:app`. The `dev` extra adds pytest, pytest-asyncio, and ruff.

Runtime dependencies stay deliberately small: pydantic for typed models, typer for the CLI, and httpx for HTTP.

## Verify the installation

```bash
arguo --help
python -m arguo --help
```

Both should print the same command listing, including `research`, `resources`, `config`, `doctor`, and `cache`. Run `arguo doctor` next; it reports whether the Python package imports, which providers are configured, and whether the catalog can be found. It never makes network calls.

You can also run the test suite to confirm a healthy checkout:

```bash
pytest
```

## Optional: Tavily API key

Live web search uses Tavily. Copy the example environment file and add your key:

```bash
cp .env.example .env
# edit .env and set TAVILY_API_KEY=...
set -a; source .env; set +a
```

The package reads plain environment variables with the `ARGUO_` prefix, plus `TAVILY_API_KEY`. Nothing loads `.env` for you, so export the values in your shell or use `set -a` as shown. Keys are registered with the logging layer at startup and scrubbed from every log record, and they are never written into run artifacts.

Without a key you can still do everything offline: `arguo research "your question" --offline` runs the full pipeline on fixture data with heuristic planning and no model calls.

## A note on the website

The documentation site is a Next.js application in the same repository, driven by the markdown files under `docs/`. It is not needed for the Python toolkit; you only touch it if you want to edit or build the docs.
