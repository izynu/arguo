"""Research run orchestrator: stages A through J with observable results.

Stages:
  A intake, B planning, C search, D retrieval+extraction, E evidence
  linkage, F gap analysis, G verification, H synthesis, I claim audit,
  J reporting.

Every stage appends a StageResult to the run manifest. Stage statuses:
"ok" when complete, "partial" when degraded, "failed" when the stage failed
but the run continues, and "skipped" when offline mode skips LLM planning.
A fatal intake failure raises ConfigurationError; a time-budget overrun
stops the run gracefully with the stages completed so far. Model failures
never kill a run: they degrade to the heuristic path with warnings.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import date
from pathlib import Path
from typing import Any

from arguo.config import BudgetTracker, ProfileConfig, ResearchBudget, Settings
from arguo.evidence.collector import collect
from arguo.evidence.ledger import EvidenceLedger
from arguo.exceptions import (
    BudgetExceededError,
    ConfigurationError,
    EvidenceLedgerError,
    ModelOutputError,
    ProviderError,
)
from arguo.models import (
    AuditReport,
    ContradictionRecord,
    EvidenceRecord,
    NormalizedResult,
    Relevance,
    ResearchPlan,
    RunManifest,
    SourceAssessment,
    StageResult,
    SubQuestion,
    VerificationStatus,
    utc_now_iso,
)
from arguo.planning import heuristic_plan, make_plan
from arguo.providers.base import ModelAdapter, NullModelAdapter
from arguo.providers.model import OpenAICompatibleAdapter
from arguo.providers.tavily import TavilySearchProvider
from arguo.reporting.report import build_report
from arguo.retrieval.fetcher import Fetcher
from arguo.retrieval.offline_fetcher import OfflineFetcher
from arguo.search.dedupe import dedupe_results
from arguo.search.offline import OfflineSearchProvider
from arguo.security.url_guard import URLGuard
from arguo.storage.cache import ResponseCache
from arguo.synthesis.synthesizer import synthesize
from arguo.utilities.ids import new_id
from arguo.utilities.logging import get_logger
from arguo.utilities.text import normalize_whitespace
from arguo.utilities.urls import normalize_url
from arguo.verification.assessor import assess_source
from arguo.verification.citations import CitationChecker
from arguo.verification.contradictions import (
    detect_numeric_contradictions,
    model_contradiction_scan_async,
)
from arguo.verification.support import support_review

logger = get_logger("arguo.orchestrator")

_MIN_QUESTION_CHARS = 8
_MAX_QUESTION_CHARS = 600
_MAX_CLAIMS_PER_SUBQUESTION = 2

_STAGES = [
    "A-intake",
    "B-planning",
    "C-search",
    "D-retrieval",
    "E-evidence",
    "F-gap-analysis",
    "G-verification",
    "H-synthesis",
    "I-claim-audit",
    "J-reporting",
]


class _RunStopped(Exception):
    """Internal control-flow signal: the time budget ended the run."""


def _make_stage(
    stage: str,
    status: str,
    started_mono: float,
    details: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> StageResult:
    duration_ms = int((time.monotonic() - started_mono) * 1000)
    return StageResult(
        stage=stage,
        status=status,  # type: ignore[arg-type]
        started_at=utc_now_iso(),
        finished_at=utc_now_iso(),
        duration_ms=max(0, duration_ms),
        details=details or {},
        warnings=warnings or [],
    )


def _evidence_by_subquestion(ledger: EvidenceLedger) -> dict[str, list[EvidenceRecord]]:
    grouped: dict[str, list[EvidenceRecord]] = {}
    for record in ledger.evidence():
        subquestion_id = record.provenance.get("subquestion_id")
        if isinstance(subquestion_id, str):
            grouped.setdefault(subquestion_id, []).append(record)
    return grouped


def _build_claims_from_evidence(
    ledger: EvidenceLedger, plan: ResearchPlan
) -> int:
    """Create claims that quote ledger passages verbatim.

    For each subquestion with evidence, up to two claims are created from
    the most relevant passages of distinct sources. Each claim links to all
    evidence gathered for that subquestion so corroboration can be judged.
    Returns the number of claims created.
    """
    grouped = _evidence_by_subquestion(ledger)
    created = 0
    for subquestion in plan.subquestions:
        records = grouped.get(subquestion.subquestion_id, [])
        if not records:
            continue

        def sort_key(record: EvidenceRecord) -> tuple[int, float]:
            overlap = record.provenance.get("token_overlap")
            return (
                0 if record.relevance == Relevance.DIRECT else 1,
                float(overlap) if isinstance(overlap, (int, float)) else 0.0,
            )

        ranked = sorted(records, key=sort_key, reverse=True)
        chosen: list[EvidenceRecord] = []
        used_sources: set[str] = set()
        for record in ranked:
            if len(chosen) >= _MAX_CLAIMS_PER_SUBQUESTION:
                break
            if record.source_id in used_sources:
                continue
            used_sources.add(record.source_id)
            chosen.append(record)
        for record in chosen:
            claim = ledger.add_claim(
                text=record.relevant_passage,
                subquestion_id=subquestion.subquestion_id,
                notes=f"Claim text quotes passage {record.evidence_id} verbatim.",
            )
            for linked in records:
                ledger.link(claim.claim_id, linked.evidence_id)
            created += 1
    return created


class ResearchOrchestrator:
    """Executes one research run and produces the run manifest and artifacts.

    Args:
        settings: Runtime settings resolved from the environment.
        profile: The research profile that sets the budget and shape.
        offline: When True, fixture providers and heuristic analysis are
            used and no network or model calls are made.
        search_fixtures: Optional caller-supplied fixture mapping for the
            offline search provider (used by the evaluation harness).
    """

    def __init__(
        self,
        settings: Settings,
        profile: ProfileConfig,
        offline: bool = False,
        search_fixtures: dict[str, list[dict]] | None = None,
    ) -> None:
        self._settings = settings
        self._profile = profile
        self._offline = offline
        self._search_fixtures = search_fixtures
        if not offline and settings.model_base_url and settings.model_name:
            self._adapter: ModelAdapter = OpenAICompatibleAdapter(
                base_url=settings.model_base_url,
                api_key=settings.model_api_key,
                model=settings.model_name,
                temperature=settings.model_temperature,
                timeout_s=max(30.0, float(self._profile.budget.per_request_timeout_s)),
                max_retries=profile.budget.max_retries,
            )
            self._model_enabled = True
        else:
            # NullModelAdapter semantics: every model stage treats the run
            # as having no model and uses the heuristic path instead.
            self._adapter = NullModelAdapter()
            self._model_enabled = False

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    def _effective_budget(self, max_sources: int | None) -> ResearchBudget:
        budget = self._profile.budget.model_copy()
        if max_sources is not None:
            budget.max_sources = max(1, min(int(max_sources), self._profile.budget.max_sources))
        return budget

    def _build_search_provider(self) -> OfflineSearchProvider | TavilySearchProvider:
        if not self._offline and self._settings.search_provider == "tavily" \
                and self._settings.tavily_api_key:
            return TavilySearchProvider(
                api_key=self._settings.tavily_api_key,
                timeout_s=self._profile.budget.per_request_timeout_s,
                max_retries=self._profile.budget.max_retries,
            )
        return OfflineSearchProvider(fixtures=self._search_fixtures)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    async def run(
        self,
        question: str,
        since: date | None = None,
        until: date | None = None,
        max_sources: int | None = None,
        output_dir: str | Path | None = None,
    ) -> RunManifest:
        """Execute stages A to J and return the run manifest."""
        run_id = new_id("R")
        manifest = RunManifest(
            run_id=run_id,
            research_question=normalize_whitespace(question),
            profile=self._profile.name,
            started_at=utc_now_iso(),
            offline_mode=self._offline,
        )
        tracker = BudgetTracker(self._effective_budget(max_sources))
        ledger = EvidenceLedger()
        provider = self._build_search_provider()
        stop_reasons: list[str] = []

        def time_ok() -> bool:
            try:
                tracker.check_time()
                return True
            except BudgetExceededError as exc:
                stop_reasons.append(f"time budget exceeded: {exc}")
                return False

        plan: ResearchPlan | None = None
        results_by_sq: dict[str, list[NormalizedResult]] = {}
        assessments: list[SourceAssessment] = []
        contradictions: list[ContradictionRecord] = []
        support_results: dict[str, dict] = {}
        synthesis: dict = {}
        audit = AuditReport()
        model_calls = 0
        rounds_used = 0

        try:
            # ------------------------------------------------------ A intake
            started = time.monotonic()
            try:
                cleaned = normalize_whitespace(question)
                if not (_MIN_QUESTION_CHARS <= len(cleaned) <= _MAX_QUESTION_CHARS):
                    raise ConfigurationError(
                        f"Research question must be between "
                        f"{_MIN_QUESTION_CHARS} and {_MAX_QUESTION_CHARS} "
                        f"characters after whitespace normalization, got "
                        f"{len(cleaned)}.",
                        hint="Shorten or expand the question text.",
                    )
                startup_warnings = self._settings.validate_for_research(self._offline)
            except ConfigurationError as exc:
                manifest.stages.append(
                    _make_stage("A-intake", "failed", started,
                                details={"error": exc.user_message()})
                )
                manifest.finished_at = utc_now_iso()
                raise
            manifest.warnings.extend(startup_warnings)
            manifest.stages.append(
                _make_stage(
                    "A-intake",
                    "ok",
                    started,
                    details={
                        "question_chars": len(cleaned),
                        "max_sources_effective": tracker.budget.max_sources,
                        "search_rounds_allowed": 1 + self._profile.budget.followup_rounds,
                    },
                )
            )

            if not time_ok():
                raise _RunStopped()

            # ---------------------------------------------------- B planning
            started = time.monotonic()
            if self._offline:
                plan = heuristic_plan(cleaned, self._profile, since)
                plan.until = until
                manifest.stages.append(
                    _make_stage(
                        "B-planning",
                        "skipped",
                        started,
                        details={
                            "generated_by": plan.generated_by,
                            "reason": "offline mode skips LLM planning",
                            "subquestions": len(plan.subquestions),
                        },
                    )
                )
            elif self._model_enabled:
                try:
                    plan = await make_plan(cleaned, self._profile, self._adapter, False)
                    model_calls += 1
                    plan.until = until
                    manifest.stages.append(
                        _make_stage(
                            "B-planning",
                            "ok",
                            started,
                            details={
                                "generated_by": plan.generated_by,
                                "subquestions": len(plan.subquestions),
                            },
                        )
                    )
                except (ModelOutputError, ProviderError) as exc:
                    logger.warning("LLM planning failed, using heuristic plan: %s", exc)
                    warning = f"LLM planning failed, heuristic plan used: {exc}"
                    manifest.warnings.append(warning)
                    plan = heuristic_plan(cleaned, self._profile, since)
                    plan.until = until
                    manifest.stages.append(
                        _make_stage(
                            "B-planning",
                            "partial",
                            started,
                            details={"generated_by": plan.generated_by,
                                     "subquestions": len(plan.subquestions)},
                            warnings=[warning],
                        )
                    )
            else:
                plan = heuristic_plan(cleaned, self._profile, since)
                plan.until = until
                manifest.stages.append(
                    _make_stage(
                        "B-planning",
                        "ok",
                        started,
                        details={
                            "generated_by": plan.generated_by,
                            "reason": "no model endpoint configured; heuristic plan",
                            "subquestions": len(plan.subquestions),
                        },
                    )
                )
            assert plan is not None

            if not time_ok():
                raise _RunStopped()

            # ------------------------------------------------------- C search
            started = time.monotonic()
            search_warnings: list[str] = []
            queries_searched = 0
            raw_results = 0
            deduped_results = 0
            seen_urls: set[str] = set()
            for subquestion in plan.subquestions:
                kept: list[NormalizedResult] = []
                for query in subquestion.search_queries:
                    try:
                        tracker.record_search()
                    except BudgetExceededError as exc:
                        search_warnings.append(f"search budget exhausted: {exc}")
                        break
                    try:
                        found = await provider.search(
                            query, tracker.budget.results_per_query
                        )
                    except EvidenceLedgerError as exc:
                        search_warnings.append(
                            f"search failed for query {query!r}: {exc}"
                        )
                        continue
                    queries_searched += 1
                    raw_results += len(found)
                    kept.extend(found)
                deduped = dedupe_results(kept)
                assigned: list[NormalizedResult] = []
                for result in deduped:
                    try:
                        key = normalize_url(result.url)
                    except ValueError:
                        continue
                    if key in seen_urls:
                        continue
                    seen_urls.add(key)
                    assigned.append(result)
                results_by_sq[subquestion.subquestion_id] = assigned
                deduped_results += len(assigned)
            rounds_used += 1
            status = "partial" if search_warnings else "ok"
            manifest.stages.append(
                _make_stage(
                    "C-search",
                    status,  # type: ignore[arg-type]
                    started,
                    details={
                        "provider": provider.name,
                        "queries_searched": queries_searched,
                        "raw_results": raw_results,
                        "deduped_results": deduped_results,
                        "rounds": 1,
                    },
                    warnings=search_warnings,
                )
            )

            if not time_ok():
                raise _RunStopped()

            # ------------------------------------- D retrieval + extraction
            started = time.monotonic()
            retrieval_warnings: list[str] = []
            semaphore = asyncio.Semaphore(self._profile.budget.concurrency)

            async def _collect_one(sq: SubQuestion) -> int:
                results = results_by_sq.get(sq.subquestion_id, [])
                if not results:
                    return 0
                if self._offline:
                    fetcher: Fetcher | OfflineFetcher = OfflineFetcher(results)
                else:
                    fetcher = Fetcher(
                        self._settings,
                        URLGuard(),
                        cache=ResponseCache(
                            self._settings.cache_dir, self._settings.cache_ttl_s
                        ),
                        budget=tracker.budget,
                    )
                async with semaphore:
                    return await collect(results, sq, fetcher, ledger, tracker)

            collected_counts = await asyncio.gather(
                *(_collect_one(sq) for sq in plan.subquestions)
            )
            evidence_added = sum(collected_counts)
            source_ids_with_evidence = {e.source_id for e in ledger.evidence()}
            fetch_failures = sum(
                1
                for s in ledger.sources()
                if s.access_note is not None
                and s.source_id not in source_ids_with_evidence
            )
            if fetch_failures:
                retrieval_warnings.append(
                    f"{fetch_failures} source(s) could not be fully retrieved; "
                    "see access notes."
                )
            d_status = "partial" if retrieval_warnings else "ok"
            manifest.stages.append(
                _make_stage(
                    "D-retrieval",
                    d_status,  # type: ignore[arg-type]
                    started,
                    details={
                        "sources": len(ledger.sources()),
                        "evidence_added": evidence_added,
                        "fetch_failures": fetch_failures,
                    },
                    warnings=retrieval_warnings,
                )
            )

            # ---------------------------------------------------- E evidence
            started = time.monotonic()
            claims_created = _build_claims_from_evidence(ledger, plan)
            manifest.stages.append(
                _make_stage(
                    "E-evidence",
                    "ok",
                    started,
                    details={
                        "claims_created": claims_created,
                        "evidence_total": len(ledger.evidence()),
                        "sources_total": len(ledger.sources()),
                    },
                )
            )

            if not time_ok():
                raise _RunStopped()

            # ------------------------------------------------ F gap analysis
            started = time.monotonic()
            gap_warnings: list[str] = []
            followups_used = 0
            max_rounds = 1 + self._profile.budget.followup_rounds

            def _gap_subquestions() -> list[SubQuestion]:
                grouped = _evidence_by_subquestion(ledger)
                return [
                    sq
                    for sq in plan.subquestions
                    if not grouped.get(sq.subquestion_id)
                ]

            gaps = _gap_subquestions()
            gaps_before_count = len(gaps)
            if gaps and self._profile.budget.followup_rounds > 0 and rounds_used < max_rounds:
                for sq in gaps:
                    if not time_ok():
                        raise _RunStopped()
                    try:
                        tracker.record_search()
                    except BudgetExceededError as exc:
                        gap_warnings.append(f"search budget exhausted: {exc}")
                        break
                    query = sq.search_queries[-1] if sq.search_queries else sq.text
                    try:
                        found = await provider.search(
                            query, tracker.budget.results_per_query
                        )
                    except EvidenceLedgerError as exc:
                        gap_warnings.append(
                            f"follow-up search failed for {sq.subquestion_id}: {exc}"
                        )
                        continue
                    fresh: list[NormalizedResult] = []
                    known = ledger.known_source_urls()
                    for result in dedupe_results(found):
                        try:
                            key = normalize_url(result.url)
                        except ValueError:
                            continue
                        if key in known:
                            continue
                        fresh.append(result)
                    if self._offline:
                        fetcher = OfflineFetcher(fresh)
                    else:
                        fetcher = Fetcher(
                            self._settings,
                            URLGuard(),
                            cache=ResponseCache(
                                self._settings.cache_dir, self._settings.cache_ttl_s
                            ),
                            budget=tracker.budget,
                        )
                    await collect(fresh, sq, fetcher, ledger, tracker)
                    followups_used += 1
                if followups_used:
                    rounds_used += 1
                gaps = _gap_subquestions()
            if gaps:
                remaining = ", ".join(sq.subquestion_id for sq in gaps)
                gap_warnings.append(
                    f"subquestions with no evidence after gap analysis: {remaining}"
                )
            f_status = "partial" if gap_warnings else "ok"
            manifest.stages.append(
                _make_stage(
                    "F-gap-analysis",
                    f_status,  # type: ignore[arg-type]
                    started,
                    details={
                        "gaps_before": gaps_before_count,
                        "followup_searches": followups_used,
                        "rounds_used": rounds_used,
                        "remaining_gaps": [sq.subquestion_id for sq in gaps],
                    },
                    warnings=gap_warnings,
                )
            )

            if not time_ok():
                raise _RunStopped()

            # -------------------------------------------------- G verification
            started = time.monotonic()
            verification_warnings: list[str] = []
            evidence_list = ledger.evidence()
            claim_evidence_map: dict[str, list[EvidenceRecord]] = {}
            for record in evidence_list:
                for claim_id in record.claim_ids:
                    claim_evidence_map.setdefault(claim_id, []).append(record)
            for source in ledger.sources():
                related_claims = {
                    claim_id
                    for record in evidence_list
                    if record.source_id == source.source_id
                    for claim_id in record.claim_ids
                }
                claim_evidence: list[EvidenceRecord] = []
                seen_evidence: set[str] = set()
                for claim_id in related_claims:
                    for record in claim_evidence_map.get(claim_id, []):
                        if record.evidence_id not in seen_evidence:
                            seen_evidence.add(record.evidence_id)
                            claim_evidence.append(record)
                assessments.append(assess_source(source, claim_evidence))

            contradictions = detect_numeric_contradictions(evidence_list)
            if self._model_enabled:
                model_scan = await model_contradiction_scan_async(ledger, self._adapter)
                model_calls += 1
                contradictions = contradictions + model_scan

            support_results = await support_review(
                ledger,
                ledger.claims(),
                self._adapter if self._model_enabled else None,
            )
            if self._model_enabled:
                model_calls += sum(
                    1
                    for result in support_results.values()
                    if result.get("method") == self._adapter.name
                )
                fallback_claims = [
                    result["claim_id"]
                    for result in support_results.values()
                    if any(
                        note.startswith("model review failed")
                        for note in result.get("notes", [])
                    )
                ]
                if fallback_claims:
                    verification_warnings.append(
                        "model support review fell back to the heuristic for "
                        f"{len(fallback_claims)} claim(s)"
                    )
            for claim in ledger.claims():
                result = support_results.get(claim.claim_id)
                if result is None:
                    continue
                try:
                    claim.verification_status = VerificationStatus(result["verdict"])
                except ValueError:
                    verification_warnings.append(
                        f"unknown verdict for {claim.claim_id}: {result['verdict']}"
                    )
                claim.support_review = result
            g_status = "partial" if verification_warnings else "ok"
            manifest.stages.append(
                _make_stage(
                    "G-verification",
                    g_status,  # type: ignore[arg-type]
                    started,
                    details={
                        "assessments": len(assessments),
                        "contradictions": len(contradictions),
                        "support_results": len(support_results),
                    },
                    warnings=verification_warnings,
                )
            )

            if not time_ok():
                raise _RunStopped()

            # --------------------------------------------------- H synthesis
            started = time.monotonic()
            try:
                synthesis = await synthesize(
                    cleaned,
                    plan,
                    ledger,
                    self._adapter if self._model_enabled else None,
                    self._profile,
                    self._offline,
                )
                if self._model_enabled:
                    model_calls += 1
                manifest.stages.append(
                    _make_stage(
                        "H-synthesis",
                        "ok",
                        started,
                        details={
                            "findings": len(synthesis.get("findings", [])),
                            "generated_by": synthesis.get("generated_by", ""),
                        },
                    )
                )
            except (ModelOutputError, ProviderError) as exc:
                logger.warning("model synthesis failed, using heuristic: %s", exc)
                warning = f"model synthesis failed, heuristic synthesis used: {exc}"
                manifest.warnings.append(warning)
                synthesis = await synthesize(cleaned, plan, ledger, None, self._profile, True)
                manifest.stages.append(
                    _make_stage(
                        "H-synthesis",
                        "partial",
                        started,
                        details={
                            "findings": len(synthesis.get("findings", [])),
                            "generated_by": synthesis.get("generated_by", ""),
                        },
                        warnings=[warning],
                    )
                )

            if not time_ok():
                raise _RunStopped()

            # Keep manifest counters current so the draft and final reports
            # show real numbers rather than zeros.
            manifest.search_rounds_used = rounds_used
            manifest.sources_retrieved = len(ledger.sources())
            manifest.evidence_records = len(ledger.evidence())

            # ------------------------------------------------ I claim audit
            started = time.monotonic()
            draft = build_report(
                cleaned,
                plan,
                ledger,
                assessments,
                contradictions,
                AuditReport(),
                support_results,
                synthesis,
                self._profile,
                manifest,
            )
            audit = CitationChecker(ledger, draft).run()
            manifest.stages.append(
                _make_stage(
                    "I-claim-audit",
                    "ok",
                    started,
                    details={
                        "citations_checked": audit.citations_checked,
                        "claims_checked": audit.claims_checked,
                        "errors": audit.error_count,
                        "warnings": audit.warning_count,
                    },
                )
            )

            if not time_ok():
                raise _RunStopped()

            # ---------------------------------------------------- J reporting
            started = time.monotonic()
            report = build_report(
                cleaned,
                plan,
                ledger,
                assessments,
                contradictions,
                audit,
                support_results,
                synthesis,
                self._profile,
                manifest,
            )
            base = Path(output_dir) if output_dir else self._settings.output_dir / run_id
            base.mkdir(parents=True, exist_ok=True)
            (base / "report.md").write_text(report, encoding="utf-8")
            sorted_sources = sorted(ledger.sources(), key=lambda s: s.source_id)
            (base / "sources.json").write_text(
                json.dumps(
                    {"sources": [s.model_dump() for s in sorted_sources]},
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (base / "evidence.json").write_text(ledger.to_json(), encoding="utf-8")
            (base / "research_plan.json").write_text(
                plan.model_dump_json(indent=2), encoding="utf-8"
            )
            (base / "audit.json").write_text(
                json.dumps(
                    {
                        **audit.model_dump(),
                        "support_results": support_results,
                        "assessments": [a.model_dump() for a in assessments],
                        "contradictions": [c.model_dump() for c in contradictions],
                    },
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            manifest.stages.append(
                _make_stage(
                    "J-reporting",
                    "ok",
                    started,
                    details={
                        "artifacts_dir": str(base),
                        "artifacts": [
                            "report.md",
                            "sources.json",
                            "evidence.json",
                            "research_plan.json",
                            "audit.json",
                            "manifest.json",
                        ],
                    },
                )
            )
        except _RunStopped:
            manifest.warnings.append(
                "Run stopped early: " + (stop_reasons[-1] if stop_reasons else "time budget")
            )
            for stage_name in _STAGES:
                if not any(s.stage == stage_name for s in manifest.stages):
                    manifest.stages.append(
                        _make_stage(
                            stage_name,
                            "skipped",
                            time.monotonic(),
                            details={"reason": "run stopped before this stage"},
                        )
                    )

        manifest.search_rounds_used = rounds_used
        manifest.sources_retrieved = len(ledger.sources())
        manifest.evidence_records = len(ledger.evidence())
        manifest.model_calls = model_calls
        manifest.providers = {
            "search": provider.name,
            "model": self._adapter.name if self._model_enabled else "null",
        }
        manifest.budget_snapshot = tracker.snapshot()
        manifest.finished_at = utc_now_iso()
        deduped_warnings: list[str] = []
        for warning in manifest.warnings:
            if warning not in deduped_warnings:
                deduped_warnings.append(warning)
        manifest.warnings = deduped_warnings

        base = Path(output_dir) if output_dir else self._settings.output_dir / run_id
        try:
            base.mkdir(parents=True, exist_ok=True)
            (base / "manifest.json").write_text(
                manifest.model_dump_json(indent=2), encoding="utf-8"
            )
        except OSError as exc:
            logger.warning("could not write manifest.json: %s", exc)
        return manifest
