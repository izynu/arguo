---
title: Testing Guide
description: How the test suite is organized, how the offline search fixtures work, and how to run subsets offline.
group: developer-guide
slug: dg-testing
order: 11
---

Organization. The suite is planned as three directories under tests/: tests/unit for models, config, planners, and validators in isolation; tests/integration for orchestrator runs end to end on fixture data; and tests/security for secret redaction, prompt injection defenses, and fetch guards. The current checkout already contains tests/fixtures/offline_search.json and a few shell helpers; test modules land in the three directories as they are written.

Offline fixtures. tests/fixtures/offline_search.json is a JSON object whose keys are query substrings (currently "refugee", "climate", "election", "vaccine", and "interest rate") and whose values are lists of result dicts with exactly four fields: title, url, snippet, and published_at as an ISO date string. Every URL uses example.org, example.net, or example.gov, and every snippet states that its content is a placeholder. The offline provider lowercases keys at load time and matches a key when it appears as a substring of the lowercased query or when its tokens are a subset of the query tokens. OfflineSearchProvider loads this file by default, ResearchOrchestrator accepts caller-supplied fixtures through search_fixtures, and the CLI keeps the path as OFFLINE_FIXTURE_PATH.

Shared fixtures. A tests/conftest.py will provide the shared setup: a settings factory that clears provider keys, an offline orchestrator with fixtures loaded from the JSON file, and tmp_path based output directories so runs never write into the repository. pytest-asyncio, already a dev dependency, covers async orchestrator and provider tests.

Running subsets. Use `pytest tests/unit -q`, `pytest tests/integration -q`, `pytest tests/security -q`, or select by keyword with `pytest -k models`. pyproject sets testpaths to tests, pythonpath to python (so the package imports without an install), and adds `-q` by default.

Philosophy. No test touches the network. No test requires TAVILY_API_KEY or a model endpoint. Provider behavior is doubled in code, and where an HTTP client must be exercised the transport is faked with httpx.MockTransport. Fixture data stays example.org style; security tests assert that secrets never reach logs or run artifacts.
