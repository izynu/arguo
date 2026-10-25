---
title: FAQ
description: Straight answers about guarantees, costs, data storage, extensibility, and contribution.
group: getting-started
slug: gs-faq
order: 10
---

## Does Arguo guarantee accurate answers?

No. It structures research, records provenance, and audits citations for internal consistency and passage support. The audit note in every `audit.json` says exactly this: automated checks cannot guarantee truth. Sources can be wrong, extraction can miss context, and synthesis can overreach. The toolkit makes those failures visible; it does not prevent them.

## How do I control cost?

Three layers: `ARGUO_MAX_MODEL_CALLS` caps model calls per run, profiles cap rounds, sources, bytes, and runtime, and the `quick` profile targets 8 model calls with a 120 second budget. `manifest.json` records how much of each budget a run spent.

## Where is my data stored?

Everything is local files. Run artifacts go to `ARGUO_OUTPUT_DIR` (default `./runs`), cached fetch responses to `ARGUO_CACHE_DIR` (default `./.arguo-cache`). The only network calls are to your configured search provider and model endpoint. Delete the two directories and nothing remains.

## Can I add a search or model provider?

Yes. Implement the `SearchProvider` or `ModelAdapter` interfaces from `arguo.providers.base`: a `name` property, an async `search(query, max_results)` that returns `NormalizedResult` items, or `complete_json` and `complete_text` methods that raise typed exceptions. Construction must not touch the network. Register the provider where the CLI builds its adapters, and map all failures onto the typed exception classes.

## Why is offline mode capped?

Offline mode uses six built in fixture results and heuristic planning. It exists to exercise the full pipeline deterministically without keys, network, or cost, so it is deliberately small and clearly labeled. It is a smoke test, not a research substitute.

## How is the resource catalog maintained?

Catalog seeds live in `data/resources/*.jsonl`, one JSON object per line. `scripts/build_resource_catalog.py` merges, deduplicates across files with an audit trail, and writes `catalog/` outputs; `scripts/validate_catalog_file.py` checks schema and style rules. Records carry `verification_status`. `documented` means curated but not live checked; `verified` means a live check confirmed the resource. The status is only promoted by an actual check.

## What is the license?

Apache 2.0, as declared in `pyproject.toml`.

## How do I contribute?

Open an issue or pull request in the repository. Before submitting Python changes, run the test suite and the linter:

```bash
pytest
ruff check python tests
```

Keep authored copy free of em dashes, en dashes, and emoji, and never add invented statistics, URLs, or claims of verification.

## Can I run it without any model endpoint?

Yes. Live Tavily search with heuristic planning and template synthesis works with no model configured. You lose model assisted planning, contradiction scanning, and model assisted verification, and the run manifest will show it.
