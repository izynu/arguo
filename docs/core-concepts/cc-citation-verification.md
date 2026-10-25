---
title: Citation Verification
description: The citation checker's rules, the verdict vocabulary, and what automated checking can and cannot establish.
group: core-concepts
slug: cc-citation-verification
order: 12
---

## The checker's rules

Stage I runs the citation checker over the draft and the ledger:

- Every `[S3]` and `[C2]` style reference must resolve to a real source or claim id in the ledger. Unresolvable references are flagged.
- A cited passage must actually be about the claim it is cited for, judged by passage support. A claim with no supporting passage is an `unsupported-claim` issue.
- Sources present in the ledger but never cited are reported as `unused-source` background, so you can see what was consulted but not used.
- Duplicate source records, missing metadata, and invalid URLs are flagged with the appropriate issue kinds.
- Issue kinds: `missing-source`, `unused-source`, `invalid-url`, `fabricated-citation`, `unsupported-claim`, `duplicate-source`, `unresolved-reference`, `missing-metadata`. Each carries a severity of error, warning, or info.

The output lands in `audit.json`: counts of citations and claims checked, the issue list, and verdict counts.

## Verdict vocabulary

Claims receive exactly one of six verdicts:

| Verdict | Meaning |
| --- | --- |
| `supported` | Linked passages support the claim as stated. |
| `partially-supported` | Some support exists but with gaps or weaker relevance. |
| `contradicted` | Credible evidence in the ledger opposes the claim. |
| `insufficient-evidence` | The ledger cannot settle the claim either way. |
| `source-unavailable` | The cited source could not be retrieved or read. |
| `requires-human-review` | The automated checks cannot classify it with confidence. |

These are the only values the pipeline emits; reports and downstream tooling can rely on the vocabulary.

## What automated checks cannot do

Automated checks verify internal consistency and passage support. They cannot guarantee truth. A fabricated number repeated across three independent looking sites passes consistency checks; a paraphrase that quietly reverses a source's meaning can defeat passage matching. The checker narrows the space where errors hide and makes the audit trail concrete, and the `automated_note` field in every audit carries this limitation so it travels with the artifact. Final judgment on whether a claim is true stays with a human reader who has the passages, the sources, and the rubric in front of them.
