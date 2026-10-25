---
title: Output Schemas
description: The six artifacts a research run writes, their fields, and small JSON examples.
group: developer-guide
slug: dg-output-schemas
order: 7
---

A run writes six artifacts into its output directory (settings.output_dir / run_id, or the path passed with --output-dir or output_dir).

report.md. A Markdown report with a fixed section order: title line, then Research question and scope, Method, Executive summary, Main findings, Claim and evidence table, Source comparison, Conflicting evidence, Strengths and weaknesses of the evidence, Limitations and unanswered questions, Confidence, Sources, Background sources, Research audit summary, Suggested next steps. Unknown values render as "unknown"; the citation audit expects this exact structure, including the "## Sources" and "## Background sources" headings.

sources.json. Sorted SourceRecord dumps: {"sources": [{"source_id": "S1", "url": "...", "retrieved_at": "...", ...}]}.

evidence.json. The full ledger as {"sources": [...], "evidence": [...], "claims": [...]} with sorted keys and explicit nulls preserved.

research_plan.json. The ResearchPlan model dump: research_question, subquestions with queries, anticipated_limitations, generated_by, timestamps.

audit.json. The AuditReport model dump plus three additions:

```json
{
  "citations_checked": 12,
  "claims_checked": 5,
  "issues": [{"kind": "unused-source", "severity": "info"}],
  "verdict_counts": {"supported": 3, "insufficient-evidence": 2},
  "support_results": {"C1": {"verdict": "supported", "method": "heuristic"}},
  "assessments": [{"source_id": "S1", "corroboration": "independent"}],
  "contradictions": [{"contradiction_id": "X1", "resolution_status": "unresolved"}]
}
```

manifest.json. The RunManifest dump: run_id, research_question, profile, started_at, finished_at, stages (each with stage, status, duration_ms, details, warnings), providers, budget_snapshot, counters (search_rounds_used, sources_retrieved, evidence_records, model_calls), offline_mode, and warnings. This file is written even when reporting failed, so every run leaves an observable record.

Consumers should treat the JSON files as schema-checked data: all four are produced from Pydantic model_dump or model_dump_json with sort_keys, and evidence.json additionally goes through EvidenceLedger.to_json. Report text, by contrast, is generated Markdown; the CitationChecker validates report citations against the ledger, so regenerate the audit after editing report.md by hand.
