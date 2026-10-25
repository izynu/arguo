---
title: Uncertainty
description: Qualitative confidence with reasons, no invented percentages, and insufficiency as a legitimate outcome.
group: core-concepts
slug: cc-uncertainty
order: 14
---

## Qualitative confidence, with reasons

Confidence in this toolkit is qualitative and always accompanied by its reasons. The vocabulary is the six verdicts (supported, partially-supported, contradicted, insufficient-evidence, source-unavailable, requires-human-review) plus the rubric scales such as high, medium, low, and unknown authority. Every rating must be traceable: the rubric's `rationale` field, the ledger's `limitations` lists, and the audit's issues are the reasons. A confidence statement you cannot trace to recorded evidence is not allowed to appear.

## No invented percentages

The pipeline never emits a probability it cannot justify. There is no "87 percent confident" anywhere in the code, because nothing in the checks computes such a number. What exists instead: counts of independent corroboration, recorded contradictions, rubric dimensions, and verdict counts from the audit. If you need a quantitative uncertainty estimate, the artifacts give you the raw inputs to compute one yourself, and you will own the assumptions.

## Insufficiency is a valid outcome

`InsufficientEvidenceError` exists as a first class, typed outcome, and the `insufficient-evidence` verdict is one of the six standard verdicts. A run that finds three conflicting statistics and no primary source should end by saying exactly that, not by picking a number because silence looks worse. The docstring for the exception states the intent plainly: reports must say when evidence is inadequate instead of manufacturing confidence. On the CLI this surfaces as exit code 9, which scripts should treat as "the honest answer was produced", not as a crash.

## Practical reading

When you read a report from this toolkit, the uncertainty signals to look for are: `date unknown` fields, `source_type: unknown`, `distinct_independent_domains` of 1, suspected syndication limitations, unresolved contradictions, and `requires-human-review` verdicts. Each one is a place where the pipeline refused to pretend it knew.
