---
title: Budgets and Profiles
description: The ResearchBudget fields, how BudgetTracker enforces them, and how profiles differ.
group: core-concepts
slug: cc-budgets-profiles
order: 15
---

## ResearchBudget

One ResearchBudget applies per run. Defaults shown are the standard profile's baseline:

| Field | Default | Enforces |
| --- | --- | --- |
| `max_search_rounds` | 2 | Number of search rounds in stages C and F. |
| `results_per_query` | 6 | Results kept per query. |
| `max_sources` | 15 | Distinct sources recorded per run. |
| `max_total_bytes` | 8,000,000 | Total downloaded bytes. |
| `per_request_timeout_s` | 20.0 | HTTP timeout per request. |
| `concurrency` | 4 | Parallel fetches. |
| `max_model_output_tokens` | 2000 | Output cap per model call. |
| `max_retries` | 2 | Retry attempts for provider calls. |
| `max_runtime_s` | 300.0 | Wall clock limit for the run. |
| `max_model_calls` | 24 | Model calls per run. |
| `max_cost_usd` | null | Optional soft cost estimate cap; best effort only because provider pricing varies. |
| `followup_rounds` | 1 | Extra rounds stage F may spend on gaps. |

## BudgetTracker behavior

The orchestrator owns one BudgetTracker per run. It records search requests, model calls, retrieved bytes, and sources seen, and it checks elapsed time. Each `record_*` call increments a counter and raises `BudgetExceededError` when the corresponding limit is crossed. Collection stages treat source and byte exhaustion as a clean stop; model call and runtime exhaustion end the run with exit code 11. `snapshot()` returns the counters, elapsed seconds, and the full limits, and the orchestrator writes it into `manifest.json` so every run reports what it spent.

## How profiles differ

| Profile | Subquestions | Rounds | Results per query | Sources | Model calls | Followups | Runtime | Concurrency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quick | 3 | 1 | 4 | 8 | 8 | 0 | 120 s | 4 |
| standard | 5 | 2 | 6 | 15 | 18 | 1 | 300 s | 4 |
| deep | 8 | 3 | 8 | 30 | 30 | 2 | 600 s | 6 |
| academic | 6 | 2 | 8 | 20 | 24 | 1 | 480 s | 4 |

Profiles are the supported way to trade cost against depth. `deep` also enables contradiction focus, which lifts evidence for and against to a higher priority; `academic` enables scholarly mode with study oriented queries and methods, limitations, and gaps structure. `ARGUO_MAX_MODEL_CALLS` can tighten the model call cap below the profile's value, and `--max-sources` can tighten sources per run.
