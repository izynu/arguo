---
title: Architecture
description: Package layout of arguo, module by module, with each responsibility.
group: core-concepts
slug: cc-architecture
order: 2
---

## Package layout

The Python package lives at `python/arguo/` and installs as the `arguo` distribution with the `arguo` console script.

| Module | Responsibility |
| --- | --- |
| `models` | Pydantic records shared by every stage: SourceRecord, EvidenceRecord, ClaimRecord, ResearchPlan, SourceAssessment, ContradictionRecord, CitationIssue, AuditReport, StageResult, RunManifest, NormalizedResult. |
| `config` | Settings resolution from environment variables, the four profiles, ResearchBudget, and BudgetTracker enforcement. |
| `exceptions` | The typed error hierarchy; every class carries the exit code the CLI uses. |
| `utilities` | Text normalization and token overlap, date parsing with explicit unknowns, URL normalization and registrable domains, id helpers, structured logging with secret redaction. |
| `security` | URLGuard (scheme allowlist, credential rejection, SSRF IP blocking, redirect revalidation) and the prompt injection guard (untrusted content wrapping and pattern detection). |
| `storage` | ResponseCache, a content addressed JSON cache with TTL and corrupt file tolerance. |
| `providers` | The SearchProvider and ModelAdapter contracts, the Tavily adapter with retry and backoff, and NullModelAdapter which fails loudly when no model is configured. |
| `search` | The offline fixture provider and provider neutral deduplication of NormalizedResults. |
| `planning` | Heuristic planner (deterministic templates) and model assisted planner (versioned prompt, pydantic validated output). |
| `retrieval` | The fetcher: manual redirects with revalidation, byte caps, content type allowlist, cache integration, and FetchResult records that never raise. |
| `extraction` | Main text extraction with the standard library HTML parser, plus JSON and plain text paths, all size capped. |
| `evidence` | EvidenceLedger (ids, links, corroboration groups, serialization) and the collector that turns fetched pages into ledger records. |
| `verification` | Source quality assessment on the rubric, corroboration analysis, and contradiction checks. |
| `synthesis` | Drafting cited report sections from claims and their linked evidence. |
| `reporting` | Assembling report.md and writing the six run artifacts. |
| `orchestrator` | Sequencing stages A to J, owning the BudgetTracker, recording StageResult entries and the RunManifest. |
| `cli` | The Typer application: research, resources, config, doctor, and cache commands, mapping exceptions to exit codes. |

## Cross cutting rules

- Construction of providers and guards performs no network activity; clients live inside async methods.
- Every failure raises a typed exception with an optional hint, never a bare `Exception`.
- Secrets are registered at startup and scrubbed from all log records.
- `fetch()` and cache operations never raise; they return error records or treat damage as a miss, so a bad URL or a broken cache file cannot kill a run.
- Serialization preserves explicit nulls so an unknown stays an unknown.
