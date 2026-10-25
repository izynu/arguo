---
title: Extending the Pipeline
description: How to add stages, providers, and versioned prompts while keeping the toolkit contracts stable.
group: developer-guide
slug: dg-extending
order: 10
---

Adding a stage. Stage names live in the _STAGES list in orchestrator.py (A-intake through J-reporting) and each stage appends one StageResult with a status of ok, partial, failed, or skipped. To add a stage: pick the next letter and name, add it to _STAGES so early stops mark it skipped, wrap the work in a timing block that appends a StageResult with details and warnings, check the time budget with the run's time_ok helper before doing expensive work, and raise only EvidenceLedgerError subclasses for fatal conditions. Keep the manifest observable: a stage that degrades must say so in status and warnings, not in a log line alone.

Adding a provider. Subclass SearchProvider or ModelAdapter from providers/base.py, following the documented contract: no network in __init__, typed exceptions, NormalizedResult output for search. Register credentials with the REGISTRY from utilities.logging so they are redacted from logs. The orchestrator selects providers in _build_search_provider and the adapter in __init__; extend those two decision points to plug in a new backend, and keep the offline path intact so tests and air-gapped runs keep working.

Prompt versioning. There is no prompts directory content; prompts live as constants in the modules that use them. planning/llm.py is the pattern to copy: a version constant (PROMPT_VERSION = "arguo-planning-v1") that is embedded both in the prompt text and in validation error messages, a _SYSTEM constant, a _SCHEMA_HINT JSON string describing the expected shape, and a build function. To add a new prompt: define the three constants next to the function that uses them (synthesis, support, and contradictions modules already follow this), bump the version string whenever instructions change so runs stay traceable in manifests, request strict JSON through adapter.complete_json, validate the output with a Pydantic model, and raise ModelOutputError on any violation so callers can fall back to heuristics.

Keeping contracts stable. Models forbid extra fields, so adding keys is a breaking change for stored artifacts; prefer new optional fields with None defaults. Exit codes in exceptions.py are public API. The NormalizedResult shape is the provider-neutral contract every search backend maps into. Ledger ids S{n}, E{n}, C{n} and the evidence.json layout are consumed by the skill templates and reports; keep them unchanged.
