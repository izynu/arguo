---
title: Data Models Reference
description: Field tables for the Pydantic models shared across the research pipeline.
group: developer-guide
slug: dg-data-models
order: 4
---

All models live in arguo.models, subclass pydantic BaseModel, and set extra="forbid" so unknown keys fail validation. Unknown dates, authors, and licenses stay None, never fabricated. Enum values are quoted strings.

| Model | Fields (type, meaning) |
| --- | --- |
| SourceRecord | source_id str, assigned S1, S2; url str, must be http or https; final_url, title, publisher, author str or null; source_type SourceType (primary, secondary, tertiary, unknown); published_at, updated_at, event_or_observation_date str or null, three distinct date kinds; retrieved_at str, auto UTC timestamp; content_type, content_hash, license, provider str or null; snippets list[str]; access_note str or null, why retrieval failed or was limited; domains_seen_in list[str], registrable domains that repeated the source |
| EvidenceRecord | evidence_id str, E1 style; claim_ids list[str]; source_id str; source_url str; source_title str or null; relevant_passage str, min length 1; passage_locator str or null; source_type SourceType; author_or_publisher str or null; published_at, updated_at, event_or_observation_date str or null; retrieved_at str; supports_or_contradicts SupportRelation (supports, contradicts, context); relevance Relevance (direct, indirect, inferred); methodology_notes str or null; independence_group str or null; limitations list[str]; verification_status VerificationStatus; content_hash str or null; provenance dict |
| ClaimRecord | claim_id str, C1 style; text str; evidence_ids, source_ids list[str]; subquestion_id str or null; claim_kind fact, estimate, interpretation, comparison, or unknown; verification_status VerificationStatus; support_review dict or null; notes str or null |
| ResearchPlan | research_question str; domain, audience str or null; depth str, defaults to profile name; time_boundary str or null; since, until date or null; subquestions list[SubQuestion]; anticipated_limitations list[str]; notes str or null; generated_by str, heuristic or adapter name; created_at str; all_queries property returns deduplicated queries |
| SubQuestion | subquestion_id str such as SQ1; text str; priority int 1 to 3, default 2; search_queries list[str]; evidence_requirements str or null; preferred_source_types list[str]; time_constraint str or null |
| SourceAssessment | source_id str; authority_for_question high, medium, low, unknown; primary_vs_secondary SourceType; methodological_quality strong, adequate, weak, not-applicable, unknown; recency current, aging, outdated, unknown; directness Relevance; transparency documented, partial, opaque, unknown; conflict_of_interest none-known, possible, declared, unknown; corroboration independent, syndicated, single-source, unknown; limitations list[str]; rationale str |
| ContradictionRecord | contradiction_id str; topic str; evidence_ids, source_ids list[str]; description str; resolution_status unresolved, explained, one-source-weaker, measurement-difference; notes str or null |
| CitationIssue | issue_id str; kind missing-source, unused-source, invalid-url, fabricated-citation, unsupported-claim, duplicate-source, unresolved-reference, missing-metadata; detail str; claim_id, source_id str or null; severity error, warning, info |
| AuditReport | citations_checked int; claims_checked int; issues list[CitationIssue]; verdict_counts dict[str, int]; automated_note str; generated_at str; error_count and warning_count properties |
| StageResult | stage str; status ok, partial, failed, skipped; started_at, finished_at str; duration_ms int; details dict; warnings list[str] |
| RunManifest | run_id str; research_question str; profile str; started_at str; finished_at str or null; stages list[StageResult]; providers dict[str, str]; budget_snapshot dict; search_rounds_used, sources_retrieved, evidence_records, model_calls int; offline_mode bool; warnings list[str] |
| NormalizedResult | title, snippet, published_at, score str or float or null; url str; provider str; raw_metadata dict, provider neutral search result shape |

VerificationStatus values: supported, partially-supported, contradicted, insufficient-evidence, source-unavailable, requires-human-review.
