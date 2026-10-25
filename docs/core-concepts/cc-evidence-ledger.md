---
title: The evidence ledger
description: Every EvidenceRecord field, why explicit nulls matter, and the ledger JSON shape.
group: core-concepts
slug: cc-evidence-ledger
order: 6
---

## One record per passage

An EvidenceRecord is a single evidentiary passage tied to its source and, later, to claims. All fields:

| Field | Meaning |
| --- | --- |
| `evidence_id` | Sequential id E1, E2, ... |
| `claim_ids` | Claims this passage bears on, filled by linking. |
| `source_id` | The SourceRecord this passage came from. |
| `source_url`, `source_title` | Direct pointer back to the web. |
| `relevant_passage` | The quoted text, 2 to 4 sentences, size capped. |
| `passage_locator` | Heading, section, or offset when known. |
| `source_type` | primary, secondary, tertiary, or unknown. |
| `author_or_publisher`, `published_at`, `updated_at` | Attribution, or null when unknown. |
| `event_or_observation_date` | When the event happened, distinct from publication. |
| `retrieved_at` | When we fetched it, always recorded. |
| `supports_or_contradicts` | supports, contradicts, or context. |
| `relevance` | direct, indirect, or inferred. |
| `methodology_notes` | For studies: design and measurement notes. |
| `independence_group` | Registrable domain, or a syndication group id. |
| `limitations` | Explicit caveats, including suspected syndication. |
| `verification_status` | Starts at requires-human-review. |
| `content_hash` | SHA 256 of the passage text. |
| `provenance` | Retrieval path: provider, subquestion, token overlap. |

## Why explicit nulls matter

Serialization preserves nulls with sorted keys. An unknown publication date is stored as `null`, never as a guessed year, an empty string, or a silently dropped field. Downstream stages and human reviewers can therefore distinguish "we looked and it is unknown" from "nobody recorded this". That distinction is the whole point of an evidence ledger.

## The ledger JSON shape

`evidence.json` contains three arrays under sorted keys:

```json
{
  "claims": [{ "claim_id": "C1", "evidence_ids": ["E1"], "text": "..." }],
  "evidence": [{ "evidence_id": "E1", "source_id": "S1", "relevant_passage": "..." }],
  "sources": [{ "source_id": "S1", "url": "https://example.org/report" }]
}
```

Links are referential: `ledger.link(claim_id, evidence_id)` updates both records, and linking evidence also adds its source to the claim's `source_ids`. Unknown ids raise `InvalidSourceError`. `from_dict` rebuilds a ledger and restores the id counters, so a ledger round trips without renumbering.
