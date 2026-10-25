---
title: Claims, Sources, and Provenance
description: ClaimRecord and SourceRecord fields, the S/E/C id scheme, provenance, and retrieval timestamps.
group: core-concepts
slug: cc-claims-sources-provenance
order: 7
---

## The id scheme

Every run uses three sequential id families assigned by the ledger in insertion order:

- `S1, S2, ...` for sources, one per URL considered.
- `E1, E2, ...` for evidence, one per recorded passage.
- `C1, C2, ...` for claims, one per factual assertion.

These ids are what reports cite. A report saying `[S3]` or `[C2]` is pointing at a record you can find in `sources.json` or `evidence.json`. Ids are per run; a fresh ledger always starts at S1, E1, C1.

## SourceRecord

A SourceRecord is one retrieved source with full provenance: `source_id`, `url`, `final_url` (after redirects), `title`, `publisher`, `author`, `source_type`, `published_at`, `updated_at`, `event_or_observation_date`, `retrieved_at`, `content_type`, `content_hash`, `license`, `provider` (which search provider surfaced it), `snippets`, `access_note` (paywall, robots block, timeout, unsupported content type), and `domains_seen_in`. URLs must be http(s). Sources whose fetch failed are still recorded, with the failure in `access_note`, so the report can show what could not be read instead of quietly dropping it.

## ClaimRecord

A ClaimRecord is one assertion: `claim_id`, `text`, `evidence_ids`, `source_ids`, `subquestion_id`, `claim_kind` (fact, estimate, interpretation, comparison, or unknown), `verification_status`, `support_review` (the support stage outcome), and `notes`. Claims start at `requires-human-review` and only move when the verification and audit stages actually examine them.

## Provenance fields and retrieval timestamps

Evidence records carry a `provenance` dict describing how the passage was obtained: the retrieval path (`direct-fetch`), the search provider, the subquestion it was collected for, and the token overlap score used for relevance. Every source and evidence record stores `retrieved_at` as a UTC ISO timestamp taken at fetch time. Retrieval time is not publication time: a page fetched today may have been published years ago or updated an hour ago, which is why the two are recorded separately and an unknown publication date stays null.
