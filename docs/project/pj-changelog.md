---
title: Changelog
description: Notable changes to Arguo, starting with the 0.1.0 initial release.
group: project
slug: pj-changelog
order: 3
---

All notable changes to Arguo are documented here. The format follows Keep a Changelog, and versions follow semantic versioning.

## 0.1.0, initial release

Added:

- Python package arguo: URL guard (scheme allowlist, credential rejection, private, loopback, link-local, multicast, and reserved range blocking for IPv4 and IPv6, redirect revalidation), prompt guard (injection heuristics and untrusted content delimiters), TTL response cache, Tavily and offline search providers, heuristic and LLM planning, bounded fetcher (manual redirects with a maximum of 3 hops, byte caps, content-type allowlist), HTML main-text extractor, evidence ledger models and collector, structured logging with secret redaction, and run manifest plus audit report models.
- Agent skill arguo: SKILL.md, 20 reference files, 5 templates, 2 examples, README, and a validation script.
- Resource catalog: 1,570 unique records across 50 categories and 82 regions, built from 19 source files with cross-file dedupe and an audit trail, with JSON, JSONL, and stats outputs plus validation and build scripts.
- Documentation site: Next.js app with documentation content under docs/.
- Evals: directory scaffold for cases, fixtures, rubrics, schemas, and reports; the runner is in progress and not part of this release.
- Project infrastructure: pyproject with the Apache-2.0 license, pytest and ruff configuration, and a test suite.
