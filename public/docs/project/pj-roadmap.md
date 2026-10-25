---
title: Roadmap
description: What is implemented, what is in progress, and what is planned in Arguo, with no dates promised.
group: project
slug: pj-roadmap
order: 2
---

This roadmap states what is real today, what is being worked on, and what is intended. Plans may change at any time. No dates are promised, and nothing on this page is a commitment.

Implemented:

- Python engine core: URL guard with SSRF range blocking and redirect revalidation, prompt-injection heuristics with delimiter wrapping, TTL response cache, Tavily and offline search providers, heuristic and LLM planning, bounded fetcher with a content-type allowlist, standard-library HTML extractor, evidence ledger models, collector, and structured logging with secret redaction.
- Agent skill: arguo with 20 references, 5 templates, 2 examples, and a validator script.
- Resource catalog: 1,570 records across 50 categories and 82 regions, with schema validation, build scripts, and a rate-capped live link checker.
- Packaging and infrastructure: pyproject for arguo 0.1.0, pytest and ruff configuration, a test suite, and the documentation site.

In progress:

- Eval runner and benchmark cases under evals/.
- Link checking across the catalog. All records carry the documented status; a subset was live-checked during authoring, and the systematic pass is not done.

Planned:

- More search providers beyond Tavily and offline.
- Richer extraction, including PDF parsing and better main-text handling.
- Multi-language research support.

Each tier carries the same caveat: priorities move as the codebase and its users do. Items may be dropped, reordered, or replaced. The changelog, not the roadmap, is the record of what actually shipped, and the eval reports, not the roadmap, are the record of how it performs.
