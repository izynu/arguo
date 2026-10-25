---
title: General research workflow
description: The core Arguo workflow for factual questions, from scoping to verdicts, with profiles and a worked command.
group: handbook
slug: general-research-workflow
order: 1
---

## The workflow at a glance

Arguo treats research as a sequence of checkable steps: scope the question, split it into subquestions with stopping rules, search in rounds, prefer primary sources, record every relevant passage in the evidence ledger, corroborate across independent domains, hunt contradictions, verify numbers and dates, audit citations, then report with explicit uncertainty. Research ends when evidence is sufficient, the budget runs out, or insufficiency is itself the honest verdict.

## A worked command

Claims about the catalog are claims like any other, so check them before repeating them. The merged catalog ships as JSONL, and one line of Python verifies a count you are about to cite:

```
python3 -c "import json; print(sum(1 for l in open('catalog/catalog.jsonl') if json.loads(l)['category']=='government-statistics'))"
```

Against the current build this prints 40, the number of government statistics resources in the catalog. The habit matters more than the example: run the count, cite the count, and note the build date it came from.

## Phrasing questions

A researchable question states its scope: jurisdiction, population, time boundary, and units where relevant. "Is X safe" cannot be answered; "what adverse events were reported in trials of X among adults between 2020 and 2024" can. If a question is ambiguous, record the interpretation you adopted instead of silently narrowing it.

## Choosing a profile

- quick: fast lookups. Three subquestions, one search round, concise report.
- standard: the default. Five subquestions, two rounds, up to 15 sources, citation audit included.
- deep: contested or contradictory topics. Eight subquestions, three rounds, up to 30 sources, contradiction focus on.
- academic: literature questions. Scholarly query variants and study level detail; see the academic page in this handbook.

Budgets are enforced per run, and a run that exceeds them stops with an explicit error rather than drifting.

## Reading verdicts

Verification is per claim, not per report. supported means primary or independently corroborated evidence backs the claim as worded. partially-supported, contradicted, insufficient-evidence, and source-unavailable each describe a different gap. requires-human-review is the default until passage support and corroboration have been checked. Each status appears in the claim-evidence table with a one line reason, and statuses may change as evidence accumulates: record the change, never overwrite the history.
