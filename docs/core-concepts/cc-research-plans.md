---
title: Research Plans
description: The ResearchPlan schema, heuristic versus model planning, and the honest limits of both.
group: core-concepts
slug: cc-research-plans
order: 4
---

## The schema

Stage B produces a ResearchPlan, written to `research_plan.json`. It is a pydantic model with `extra="forbid"`, so its shape is stable and inspectable.

| Field | Meaning |
| --- | --- |
| `research_question` | The normalized question. |
| `domain`, `audience` | Optional framing supplied at intake. |
| `depth` | The profile name used. |
| `time_boundary` | Date range constraint stated in the request, as text. |
| `since`, `until` | Parsed date bounds, or null. |
| `subquestions` | List of SubQuestion records. |
| `anticipated_limitations` | What the planner already knows it cannot do well. |
| `notes` | Free text provenance of the plan. |
| `generated_by` | `heuristic` or the model planner identifier. |
| `created_at` | ISO timestamp. |

Each SubQuestion carries `subquestion_id` (SQ1, SQ2, ...), `text`, `priority` (1 highest to 3), `search_queries`, `evidence_requirements` (what would count as an answer), `preferred_source_types`, and an optional `time_constraint`.

## Heuristic planning

The heuristic planner is deterministic: the same question and profile always produce the same plan. It draws from six fixed templates: definition, current state, key numbers, recent developments, evidence for and against, and causes. Queries are built from the question's content terms only, capped at three per subquestion, with scholarly and year variants when the profile and `--since` call for them. It never invents facts or dates; it only decides what to search.

## Model assisted planning

With a configured model endpoint, a versioned prompt (`arguo-planning-v1`) asks for strict JSON matching the ResearchPlan shape. Output is validated by the pydantic model; a validation failure raises `ModelOutputError` instead of letting malformed plans flow downstream. The prompt forbids fabricated dates, sources, numbers, and facts.

## Honest limitations

The heuristic planner may miss domain specific terminology, its query diversity is limited without a live model, and when no time boundary is supplied, recency control depends on query terms alone; the plan says so in `anticipated_limitations`. Model plans are only as good as the model behind them and are validated for shape, not for sense. Neither planner guarantees coverage: gap analysis in stage F exists precisely because first plans miss things.
