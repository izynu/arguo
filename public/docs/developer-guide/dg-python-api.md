---
title: Python API Reference
description: The key public functions and classes of arguo with their real signatures.
group: developer-guide
slug: dg-python-api
order: 3
---

Settings and profiles. get_settings(env: dict[str, str] | None = None, reload: bool = False) -> Settings caches a module-level instance; pass env or reload to re-read. PROFILES is a dict[str, ProfileConfig] with the keys quick, standard, deep, academic. Settings.from_env() resolves the ARGUO_ variables and TAVILY_API_KEY.

Orchestrator. ResearchOrchestrator(settings: Settings, profile: ProfileConfig, offline: bool = False, search_fixtures: dict[str, list[dict]] | None = None). It selects OpenAICompatibleAdapter when a model base URL and name are configured and offline is False, otherwise NullModelAdapter. await orchestrator.run(question: str, since: date | None = None, until: date | None = None, max_sources: int | None = None, output_dir: str | Path | None = None) -> RunManifest executes stages A to J and writes the six artifacts.

Ledger. EvidenceLedger methods: add_source(url, *, title=None, final_url=None, publisher=None, author=None, source_type=SourceType.UNKNOWN, published_at=None, ..., provider=None, snippets=None, access_note=None, domains_seen_in=None) -> SourceRecord assigns S{n}; add_evidence(source_id, source_url, relevant_passage, *, claim_ids=None, ..., supports_or_contradicts=SUPPORTS, relevance=DIRECT, ..., content_hash=None, provenance=None) -> EvidenceRecord assigns E{n} and raises InvalidSourceError for an unknown source; add_claim(text, *, subquestion_id=None, claim_kind="unknown", evidence_ids=None, source_ids=None, notes=None) -> ClaimRecord assigns C{n}; link(claim_id, evidence_id) links both directions and is idempotent; views sources(), evidence(), claims(); get_source/get_evidence/get_claim; known_source_urls(); sources_by_domain(); corroboration_groups(); to_dict(), to_json(), and EvidenceLedger.from_dict(data).

Planning. await make_plan(question, profile, adapter, offline=False) -> ResearchPlan picks llm_plan when an adapter is given and offline is False, else heuristic_plan. heuristic_plan(question, profile, since=None, domain=None) is deterministic. llm_plan(question, profile, adapter) builds the versioned prompt with build_planning_prompt(question, profile) and validates output with the ResearchPlan model, raising ModelOutputError.

Collection. await collect(results: list[NormalizedResult], subquestion: SubQuestion | None, fetcher, ledger, budget) -> int fetches, extracts, splits passages, and adds evidence records. Fetcher(settings, guard, cache=None, budget=None) with await fetcher.fetch(url) -> FetchResult never raises.

Verification and synthesis. assess_source(source, evidence) -> SourceAssessment; await support_review(ledger, claims, adapter, min_overlap=0.10) -> dict[str, dict]; detect_numeric_contradictions(evidence) -> list[ContradictionRecord]; model_contradiction_scan(ledger, adapter) sync wrapper of the async scan; CitationChecker(ledger, report_markdown).run() -> AuditReport. await synthesize(question, plan, ledger, adapter, profile, offline) -> dict returns executive_summary, findings, limitations, gaps, follow_up_queries, generated_by.

Reporting. build_report(question, plan, ledger, assessments, contradictions, audit, support_results, synthesis, profile, manifest) -> str; render_html(markdown) -> str with stdlib-only escaping.
