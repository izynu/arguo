---
title: The Research Workflow
description: The ten pipeline stages A to J, what each consumes, and what each produces.
group: core-concepts
slug: cc-workflow
order: 3
---

## The stages

| Stage | Name | Consumes | Produces |
| --- | --- | --- | --- |
| A | Intake | The question, profile, and flags such as `--since` and `--max-sources` | A normalized request and a started RunManifest |
| B | Planning | The request and the profile | A ResearchPlan with subquestions, queries, evidence requirements, and anticipated limitations |
| C | Search | Plan queries | NormalizedResults from the search provider, deduplicated |
| D | Retrieval and extraction | The deduplicated results | Fetched page text, titles, content types, passage splits; failures become sources with access notes |
| E | Evidence collection | Fetched text and the subquestion focus | SourceRecords and EvidenceRecords in the ledger, with hashes and provenance |
| F | Gap analysis | The ledger and the plan | Followup queries for weak subquestions, bounded by the profile's followup rounds |
| G | Verification | Ledger records | SourceAssessment records, corroboration groups, and contradiction findings |
| H | Synthesis | Claims and their linked evidence | Cited draft sections with per claim verdicts |
| I | Claim audit | The draft, ledger, and sources | audit.json: CitationIssue records, verdict counts, and the automation limitation note |
| J | Reporting | Everything above | report.md plus all six artifacts and the completed manifest |

## Two things worth knowing

**The loop is bounded.** Stages C to F can repeat within the profile's search rounds and followup rounds, but budgets are hard limits. When the BudgetTracker says a limit is spent, collection stops cleanly or the run ends with exit code 11, never with an unbounded loop.

**Verification is separate from collection.** Stage E records what a passage says and how it was retrieved; it does not judge truth. Stage G judges structure and quality: rubric scores, independence of corroboration, and numeric contradictions. Stage I audits citations mechanically. Each layer only claims what it actually checks.

## Where you can intervene

The plan from stage B is a file you can read and edit before spending budget. The ledger from stage E is readable JSON. If the plan looks wrong, the rest of the run will be too, which is exactly why it is written to `research_plan.json` first.
