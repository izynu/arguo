---
title: Contradictions
description: How the toolkit detects numeric contradictions, where a model assisted scan fits, and how conflicts are resolved.
group: core-concepts
slug: cc-contradictions
order: 11
---

## What counts as a contradiction

A contradiction is recorded when two evidence records bear on the same claim or topic but cannot both be right as stated. The mechanical case is numeric: two passages assert the same quantity, such as a total, a rate, or a percentage, with different values. The check is conservative by design:

- The values must plausibly refer to the same thing, anchored by the claim text and subquestion context.
- The sources must come from different independence groups. Two passages from one domain disagreeing may be a typo or an update, not a real conflict.
- Units and measurement context are compared before flagging; a per capita figure against an absolute total is a measurement difference, not a contradiction.

## Model assisted scan

With a model endpoint configured, stage G also asks the model to scan claim linked evidence for qualitative conflicts: different causal explanations, incompatible timelines, or opposing characterizations. The scan is advisory. Model findings enter the same ContradictionRecord pipeline and are marked as model assisted in notes, so a human can weigh them. Without a model, only the numeric and structural checks run, and the manifest records that.

## Resolution statuses

Every ContradictionRecord carries a `resolution_status`:

| Status | Meaning |
| --- | --- |
| `unresolved` | The conflict stands; no source of reconciliation was found. |
| `explained` | A documented reason reconciles the values, such as different dates or scopes. |
| `one-source-weaker` | One side is weaker on the rubric, recorded without declaring a winner. |
| `measurement-difference` | The values measure different things: units, scope, or period. |

Contradictions are reported, never averaged away. A report cannot silently pick one number when credible sources give two. Unresolved conflicts surface in the synthesis and in the limitations section, and they are one path to an `insufficient-evidence` or `contradicted` verdict at audit time.
