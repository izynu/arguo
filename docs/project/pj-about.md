---
title: About Arguo
description: Why the project exists, what is built today, what is not, and the design principles it follows.
group: project
slug: pj-about
order: 1
---

Arguo exists because research produced by language models is often fluent, weakly sourced, and impossible to audit. The project builds tooling where every claim carries its evidence with it, so a reader can check the work instead of trusting it.

What exists today:

- A Python package, arguo (PyPI name arguo), with the research engine: URL guard, prompt-injection guard, response cache, Tavily and offline search providers, heuristic and LLM planning, a bounded fetcher, a main-text extractor, evidence ledger models, and a collector.
- An agent skill, arguo, with SKILL.md, 20 reference files, 5 templates, 2 examples, and a README, plus a validation script.
- A curated resource catalog of 1,570 records across 50 categories and 82 regions, built from 19 source files with cross-file dedupe and an audit trail, published as JSON, JSONL, and stats. 150 records are live-checked and `verified`; the rest are `documented`.
- A documentation site, this Next.js app, with a resource explorer and 81 documentation pages.
- An evaluation harness with 56 structural benchmark cases in 8 files and an offline runner that checks citation consistency, claim support linkage, and source diversity.

What is explicitly not built yet: a full live link check across the catalog (the first rate-capped pass on 2026-10-25 verified 150 of 1,570 records; bot-blocked and unchecked records remain documented); PDF parsing and reader-quality extraction; additional search providers; multi-language support.

Who builds it: Arguo is built and maintained by [Zynu](https://github.com/izynu) (lead maintainer, repository owner) and [Shraddha](https://github.com/xhraddha) (co-maintainer).

Design principles: evidence before narrative; every claim links to a source and a passage; retrieval is bounded and defensive; web content is untrusted data; provenance and timestamps are recorded, not reconstructed; uncertainty is stated, not smoothed over; automated checks verify structure while humans judge meaning; budgets make cost and time visible; and nothing is published that a run did not actually produce.
