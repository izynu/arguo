---
title: Primary, Secondary, and Tertiary Sources
description: Definitions of the three source tiers, when each is appropriate, and how the toolkit records source_type.
group: core-concepts
slug: cc-primary-secondary
order: 8
---

## Definitions

| Tier | Definition | Examples |
| --- | --- | --- |
| Primary | Firsthand material produced by the actor or process under study, or a direct measurement of it. | A statistical agency's dataset, a court filing, a company's own filing, a diary, raw sensor output. |
| Secondary | Analysis, interpretation, or reporting based on primary material. | A news report of a study, a literature review of specific papers, an analyst's writeup of a filing. |
| Tertiary | Summaries or indexes that aggregate secondary material, usually without new analysis. | Encyclopedias, most textbooks, bibliographies, fact sheet compilations. |

The classification depends on the question. A government statistics portal is primary for the numbers it publishes and secondary or tertiary for claims about what those numbers mean. Context matters more than genre labels.

## When each is appropriate

- Planning targets: subquestions declare `preferred_source_types`, so definition questions may accept tertiary starting points while numeric questions should demand primary or strong secondary sources.
- Numbers and dates: primary sources are strongly preferred, because every retelling adds transcription risk.
- Orientation: tertiary sources are legitimate for orientation and for finding the primary trail, not for settling factual disputes.

## How the toolkit records source_type

`source_type` appears on both SourceRecord and EvidenceRecord with four values: `primary`, `secondary`, `tertiary`, and `unknown`. It defaults to `unknown` on purpose. Classifying a source reliably requires reading it with the specific question in mind, and a wrong confident label is worse than an honest unknown: a mislabeled primary can launder authority into a report. The rule based assessor only assigns a tier when the evidence for the classification is concrete, and planning requests for primary sources are satisfied by actually checking tiers in stage G, not by assuming the first hit qualifies. When you read `evidence.json`, treat `unknown` as "not yet classified" and check the passage yourself if the tier matters to your conclusion.
