---
title: Evaluation Philosophy
description: How Arguo evaluates itself, what the offline runner can and cannot measure, and why no score is published without a real run behind it.
group: quality-safety
slug: qs-evaluation
order: 1
---

Arguo treats evaluation as measurement, not marketing. The project does not publish leaderboard claims, comparison charts against other tools, or aggregate quality scores. When the toolkit reports numbers, they describe one specific run: how many sources were retrieved, how many citations resolved, how long the run took, and where the budget was spent.

The offline eval runner computes a narrow set of structural metrics per case: citation validity (whether cited URLs are well formed and fetchable), unsupported-claim rate (claims with no evidence record attached), source diversity (distinct independence groups or registrable domains), search rounds used, and runtime. These metrics are mechanical. Anyone can recompute them from the run artifacts, and they say nothing about whether a conclusion is true.

What requires human judgment: whether a cited passage actually supports its claim in context, whether two sources are genuinely independent of each other, whether a source type classification (primary, secondary) is correct, and whether the report fairly presents contradictions. The audit report model encodes this boundary in its own automated note: automated checks verify internal consistency and passage support, and they cannot guarantee truth.

No fabricated scores policy: the repository must never contain eval numbers that were not produced by a real run of the runner against real cases, and any published metric must link to the report artifact that produced it. The runner is being built in evals/; the directory tree for cases, fixtures, rubrics, schemas, and reports exists, the runner itself does not yet. Until live evals exist, every metric on these documentation pages is a structural definition, not a result.
