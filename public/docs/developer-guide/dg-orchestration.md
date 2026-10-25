---
title: Orchestration Internals
description: How ResearchOrchestrator runs stages A to J, records StageResults, enforces budgets, and degrades on model failures.
group: developer-guide
slug: dg-orchestration
order: 6
---

ResearchOrchestrator.run executes ten stages in fixed order: A-intake, B-planning, C-search, D-retrieval, E-evidence, F-gap-analysis, G-verification, H-synthesis, I-claim-audit, J-reporting. Every stage appends one StageResult to the manifest with started and finished timestamps, a duration in milliseconds, details, and warnings.

StageResult status semantics: "ok" when the stage completed as designed, "partial" when the run continued in degraded form (for example heuristic planning after a model failure, or fetch failures recorded as access notes), "failed" when the stage failed but the run continues, and "skipped" when a stage did not run, such as B-planning in offline mode, which uses the deterministic planner directly. A fatal intake failure (question length out of the 8 to 600 character range, or configuration validation) appends a failed A-intake StageResult and re-raises ConfigurationError. When the time budget runs out, the internal _RunStopped path marks every stage not yet reached as skipped, adds a run warning, and still writes the manifest.

Budget checks happen between stages and inside loops. The time budget is checked after each stage through BudgetTracker.check_time; overruns stop the run gracefully. Stage C records each search request and stops querying a subquestion when the search budget is exhausted. Stage D runs subquestion collection concurrently under an asyncio.Semaphore sized by profile.budget.concurrency; the collector stops on the source and byte budgets without raising. Stage F spends follow-up searches on subquestions with no evidence, up to 1 + followup_rounds rounds.

Model failures never kill a run. In B-planning a ModelOutputError or ProviderError from the LLM planner falls back to heuristic_plan and marks the stage partial. In G-verification the per-claim support review falls back to the token-overlap heuristic with a "model review failed" note, and unknown verdict strings become warnings. In H-synthesis a model failure falls back to heuristic synthesis, again partial. Verified model calls are counted into manifest.model_calls.

Artifact writing happens in J-reporting: report.md, sources.json, evidence.json, research_plan.json, and audit.json are written to output_dir (settings.output_dir / run_id, or the caller's path). manifest.json is written after the stage loop in its own guarded block, so a manifest exists even when reporting failed. providers, budget snapshot, counters, and deduplicated warnings are finalized before the manifest is returned.
