---
title: Corroboration and Independence
description: How independence groups, syndication detection, and corroboration groups separate real confirmation from repetition.
group: core-concepts
slug: cc-corroboration
order: 10
---

## Independence groups

Independence is approximated mechanically: by default an evidence record's `independence_group` is the registrable domain of its source URL. Two passages from `news.example.co.uk` and `blog.example.co.uk` share one group; a passage from a different registrable domain is a distinct group. The registrable domain computation handles common two level suffixes (co.uk, com.au, gov.cn and many more) without a public suffix dependency, which is a documented approximation, not a perfect PSL implementation.

## Syndication detection

Different domains can still be one voice: wire copies and syndicated articles repeat nearly identical text. The ledger detects this by comparing passage text with token Jaccard similarity. When two or more passages for the same claim score 0.85 or higher, they are clustered as probable syndication. Clustered records are annotated, not deleted: each gains the limitation "possible syndication or shared upstream source" and a shared `syndication:{id}` independence group. A domain only keeps credit as independent corroboration when some of its evidence sits outside the suspected syndication set.

## corroboration_groups output

`ledger.corroboration_groups()` returns one entry per claim:

```json
{
  "claim_id": "C1",
  "text": "The program reduced losses by 12 percent.",
  "evidence_ids": ["E1", "E2", "E3"],
  "independent_domains": ["example.org", "example.edu"],
  "distinct_independent_domains": 2,
  "syndication_suspected": true,
  "syndication_groups": [["E2", "E3"]]
}
```

`distinct_independent_domains` counts genuinely separate voices supporting the claim. A claim with three citations but `distinct_independent_domains: 1` is a single source claim wearing three hats, and the report treats it that way.

## Honest limits

Domain equality is a proxy. Two domains under common ownership, or two outlets republishing with light edits, may evade both rules. That is why suspected syndication is recorded as a limitation with the threshold stated, and why the rubric's `corroboration` field and the final report carry the finding to a human rather than resolving it silently.
