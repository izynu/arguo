---
title: Your First Research Run
description: A stage by stage walkthrough of one offline run, the files it produces, and how to read them.
group: getting-started
slug: gs-first-research
order: 4
---

## The command

```bash
arguo research "What is evidence based research and how is it applied?" --offline
```

Note the run id printed at the end. All artifacts land in `runs/{run_id}/`.

## What happens, stage by stage

| Stage | Name | What it does |
| --- | --- | --- |
| A | Intake | Normalizes the question, profile, and constraints; starts the run manifest. |
| B | Planning | Builds a ResearchPlan. Heuristic templates offline, model assisted when configured. |
| C | Search | Runs plan queries through the search provider and deduplicates results. |
| D | Retrieval and extraction | Fetches pages behind the SSRF guard, extracts main text, splits passages. |
| E | Evidence collection | Records sources and passages in the ledger with hashes and provenance. |
| F | Gap analysis | Finds subquestions with weak evidence and spends followup rounds on them. |
| G | Verification | Scores sources on the rubric, computes corroboration groups, scans for contradictions. |
| H | Synthesis | Drafts report sections from claims and linked evidence. |
| I | Claim audit | Runs the citation checker and produces issues and verdicts. |
| J | Reporting | Assembles `report.md` and writes all artifacts plus the manifest. |

## Reading `report.md`

The report answers each subquestion in order, with inline citations. Citations like `[S3]` point at source 3 and `[C2]` at claim 2. A section whose evidence is thin says so explicitly instead of padding. A limitations section lists what the run could not establish, and suspected syndication or single source claims are marked as such.

## Reading `evidence.json`

The file has three arrays: `sources`, `evidence`, and `claims`. Each evidence record carries `relevant_passage`, `source_id`, `supports_or_contradicts`, `relevance`, `independence_group`, and a `content_hash`. Nulls are explicit: a missing publication date is `null`, not a guess. Follow a claim's `evidence_ids` to the passages, then the passage's `source_id` to the URL and retrieval timestamp.

## Documented versus verified catalog statuses

When the pipeline consults the resource catalog, each record carries a `verification_status`. `documented` means the record was curated from established knowledge but has not had a live link check in the current sweep. `verified` means a live check actually confirmed the resource. The distinction is recorded, never blurred: seeds stay `documented` until something actually checked them.
