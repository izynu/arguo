---
title: Source Quality Rubric
description: The SourceAssessment fields, how the rule based assessor works, and why there are no numeric trust scores.
group: core-concepts
slug: cc-source-quality
order: 9
---

## The rubric

Stage G produces one SourceAssessment per source. Each field is a short scale or an explicit unknown, never a number:

| Field | Values |
| --- | --- |
| `source_id` | The S id being assessed. |
| `authority_for_question` | high, medium, low, unknown. |
| `primary_vs_secondary` | primary, secondary, tertiary, unknown. |
| `methodological_quality` | strong, adequate, weak, not-applicable, unknown. |
| `recency` | current, aging, outdated, unknown. |
| `directness` | direct, indirect, inferred. |
| `transparency` | documented, partial, opaque, unknown. |
| `conflict_of_interest` | none-known, possible, declared, unknown. |
| `corroboration` | independent, syndicated, single-source, unknown. |
| `limitations` | Free text caveats. |
| `rationale` | Why the ratings were assigned. |

Every dimension can be `unknown`, and most start there. The assessment is evidence about fitness for the question, not a verdict on the source in general.

## Rule based assessor behavior

The built in assessor is rule driven and conservative: it assigns a rating only when the rule's inputs are actually available, such as measurable recency from known publication dates, or corroboration status derived from the corroboration analysis. When inputs are missing it records `unknown` and explains why in `rationale`. It does not guess, and it does not import opinions about publishers.

## Domain reputation is not proof of truth

The rubric deliberately has no "trusted domains" list and no numeric trust score. A high reputation domain publishes errors; a personal blog can be the most authoritative account of its own event. What matters is whether this source, for this question, has the authority, transparency, and corroboration the claim requires. Numeric scores would fake precision the checks do not have and invite threshold thinking where judgment is needed. Read the rubric as a structured set of things to verify, not a grade.
