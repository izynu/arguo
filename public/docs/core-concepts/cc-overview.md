---
title: System Overview
description: The four parts of Arguo and how data flows between them during a research run.
group: core-concepts
slug: cc-overview
order: 1
---

## Four parts, one discipline

Arguo has four cooperating parts:

1. **The Agent Skills** (`skill/arguo/`, `skill/arguo-curator/`, `skill/arguo-source-audit/`) are text only methods that teach any agent the evidence first research process, catalog curation, and citation auditing, using references and templates.
2. **The Python agent** (`python/arguo/`) is the executable reference implementation. It runs the ten stage pipeline, enforces budgets and safety rules, and writes machine readable artifacts.
3. **The resource catalog** (`data/resources/` merged into `catalog/`) is a categorized collection of curated starting point resources with explicit verification status.
4. **The documentation site** is a Next.js app in the same repository that renders these markdown pages.

## Data flow

```text
research question
      |
      v
[A Intake] -> run manifest started
      |
      v
[B Planning] -> ResearchPlan (subquestions, queries, requirements)
      |
      v
[C Search] -> deduplicated NormalizedResults   <-- search provider (tavily/offline)
      |
      v
[D Retrieval + extraction] -> page text, passages  <-- HTTP fetcher behind SSRF guard
      |
      v
[E Evidence collection] -> ledger: sources, evidence, claims
      |
      v
[F Gap analysis] -> followup queries (bounded by followup rounds)
      |
      v
[G Verification] -> source assessments, corroboration groups, contradictions
      |
      v
[H Synthesis] -> cited draft sections
      |
      v
[I Claim audit] -> audit.json (issues, verdicts)
      |
      v
[J Reporting] -> report.md + sources.json + evidence.json
                 + research_plan.json + audit.json + manifest.json
```

## Design commitments

Every stage is inspectable: the plan is a file, the ledger is a file, the audit is a file. Unknowns are explicit nulls, never guesses. Content from the web is data, never instructions. Budgets are enforced, not advisory. And the final audit states its own limits: automated checks verify internal consistency and passage support, they cannot guarantee truth.
