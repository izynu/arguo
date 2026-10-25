---
title: Benchmark Cases
description: The planned benchmark case mix for Arguo, the case file format, how cases are run, and how new cases are added.
group: quality-safety
slug: qs-benchmarks
order: 2
---

The benchmark suite is a set of research cases that exercise the whole pipeline, including its failure paths. The planned mix covers: stable factual questions; time-sensitive questions; scientific claims; academic literature questions; market and industry questions; historical disputes; statistics and quantitative claims; contradictory sources; weak evidence; outdated sources; unsupported assumptions; missing evidence; duplicate or syndicated reporting; adversarial injection inside retrieved content; and citation mismatches, where a claim is cited to a source that does not contain it.

Case file format. Each case is one JSON file in evals/cases/. Planned fields: a stable id, the category from the list above, the research question, optional constraints such as a time boundary or profile, and a pointer to a rubric or an expected behavior. Schemas that cases must validate against live in evals/schemas/. Rubrics live in evals/rubrics/. Reusable offline fixtures (fixed search results and page bodies, so a case can run with no network) live in evals/fixtures/. Runner output, per case and summary, is written to evals/reports/.

How to run. The runner is evals/run_evals.py. It is being built concurrently with these docs: the evals/ directory tree exists, the runner and its schemas are not committed yet. The planned interface follows the Task 3-b specification: read the cases, run each through the pipeline under a profile budget using offline fixtures by default, compute the structural metrics from the evaluation philosophy page, and write reports into evals/reports/. Until the runner lands, treat this page as a structural description, not a working how-to.

How to add cases. Add one JSON file per case in evals/cases/, match the schema, pick the closest category, keep questions answerable from public web evidence, and state expected behavior in terms of the structural metrics or a rubric rather than a verdict.
