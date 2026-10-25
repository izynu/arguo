"""Transparent, rule-based source assessment.

The rubric is deliberately conservative: every field stays "unknown" whenever
the underlying data is missing, and the rationale always names which fields
were actually known. This module never invents a numeric quality score.
"""

from __future__ import annotations

from datetime import date

from arguo.models import (
    EvidenceRecord,
    Relevance,
    SourceAssessment,
    SourceRecord,
    SourceType,
)
from arguo.utilities.dates import parse_date_lenient
from arguo.utilities.logging import get_logger
from arguo.utilities.urls import get_registrable_domain

logger = get_logger("arguo.verification.assessor")

_CURRENT_YEARS = 2.0
_AGING_YEARS = 5.0

_CONFLICT_MARKERS = (
    "conflict of interest",
    "conflicts of interest",
    "competing interest",
    "competing interests",
    "competing financial interest",
    "financial relationship",
    "financial relationships",
    "financial disclosure",
)
_NO_CONFLICT_MARKERS = (
    "no conflict of interest",
    "no conflicts of interest",
    "no competing interests",
    "no competing financial interests",
    "nothing to disclose",
    "declares no conflict",
    "declare no conflict",
    "declared no conflict",
    "no financial relationships",
)


def _registrable_domain_or_none(url: str) -> str | None:
    try:
        return get_registrable_domain(url)
    except ValueError:
        return None


def _is_confident_primary(url: str) -> bool:
    """Domain heuristics that justify calling a source primary.

    Confident markers only: government and education registrable domains
    (any label "gov" or "edu" among the domain labels) and DOI links. News
    sites, blogs, and aggregators are never guessed.
    """
    lowered = (url or "").lower()
    if "doi.org/" in lowered or lowered.startswith("doi:"):
        return True
    domain = _registrable_domain_or_none(url)
    if domain is None:
        return False
    labels = domain.split(".")
    return "gov" in labels or "edu" in labels


def _recency(
    published_at: str | None, today: date | None = None
) -> tuple[str, str | None]:
    """Bucket publication recency; unknown input stays unknown."""
    parsed = parse_date_lenient(published_at)
    if parsed is None:
        detail = (
            "publication date was provided but could not be parsed"
            if published_at
            else "publication date was not provided"
        )
        return "unknown", detail
    today = today if today is not None else date.today()
    years = (today - parsed).days / 365.25
    if years < 0:
        return "current", "publication date is in the future relative to the run date"
    if years <= _CURRENT_YEARS:
        return "current", None
    if years <= _AGING_YEARS:
        return "aging", None
    return "outdated", None


def _independence_groups(evidence: list[EvidenceRecord]) -> list[str]:
    groups: list[str] = []
    for record in evidence:
        if record.independence_group:
            groups.append(record.independence_group)
            continue
        domain = _registrable_domain_or_none(record.source_url)
        groups.append(domain if domain else f"unparsed:{record.source_id}")
    return groups


def _corroboration(evidence: list[EvidenceRecord]) -> tuple[str, int, int]:
    """Classify corroboration from independence groups.

    "independent" when at least two records come from different registrable
    domains, "syndicated" when any independence groups overlap (two or more
    records share a domain or a syndication group), "single-source" when
    exactly one record exists, and "unknown" when no records were supplied.
    """
    if not evidence:
        return "unknown", 0, 0
    groups = _independence_groups(evidence)
    distinct = set(groups)
    if len(distinct) < len(groups):
        return "syndicated", len(distinct), len(groups)
    if len(distinct) >= 2:
        return "independent", len(distinct), len(groups)
    return "single-source", 1, 1


def _conflict_of_interest(source: SourceRecord, evidence: list[EvidenceRecord]) -> str:
    """Scan available text for declared interests; otherwise stay unknown."""
    parts: list[str] = list(source.snippets)
    if source.access_note:
        parts.append(source.access_note)
    for record in evidence:
        parts.append(record.relevant_passage)
        if record.methodology_notes:
            parts.append(record.methodology_notes)
    blob = " ".join(parts).lower()
    if not blob:
        return "unknown"
    for marker in _NO_CONFLICT_MARKERS:
        if marker in blob:
            return "none-known"
    for marker in _CONFLICT_MARKERS:
        if marker in blob:
            return "declared"
    return "unknown"


def assess_source(
    source: SourceRecord, evidence: list[EvidenceRecord]
) -> SourceAssessment:
    """Assess one source against the evidence records that bear on its claims.

    Args:
        source: The ledger source record.
        evidence: Evidence records bearing on the claim(s) this source
            supports. Pass the claim-level evidence (which may come from
            other domains) so corroboration can be judged, not just the
            passages harvested from this source.

    Returns:
        A SourceAssessment with honest "unknown" values wherever data is
        missing. The rationale is a factual sentence describing which fields
        were known. No numeric quality score is produced.
    """
    limitations: list[str] = []

    if _is_confident_primary(source.url):
        source_type = SourceType.PRIMARY
    else:
        source_type = SourceType.UNKNOWN
        limitations.append(
            "source type could not be determined from the URL, so it stays unknown"
        )

    recency, recency_note = _recency(source.published_at)
    if recency_note:
        limitations.append(recency_note)

    corroboration, distinct_domains, group_count = _corroboration(evidence)
    if not evidence:
        limitations.append(
            "no evidence passages were available, so corroboration stays unknown"
        )

    conflict_of_interest = _conflict_of_interest(source, evidence)

    if evidence:
        relevances = {record.relevance for record in evidence}
        if Relevance.DIRECT in relevances:
            directness = Relevance.DIRECT
        elif Relevance.INFERRED in relevances:
            directness = Relevance.INFERRED
        else:
            directness = Relevance.INDIRECT
    else:
        # Passages in this pipeline always come from direct fetches of the
        # source itself; with no passages there is nothing to contradict it.
        directness = Relevance.DIRECT

    if source.title is None:
        limitations.append("title was not provided")
    if source.published_at is None:
        limitations.append("publication date is unknown")

    known_parts: list[str] = []
    known_parts.append(
        "the URL and retrieval time were known"
        if source.retrieved_at
        else "only the URL was known"
    )
    if source.published_at is not None:
        known_parts.append(f"the publication date {source.published_at} was provided")
    else:
        known_parts.append("no publication date was provided")
    if source_type is SourceType.PRIMARY:
        known_parts.append("a government, education, or DOI domain marker was present")
    else:
        known_parts.append("no confident domain marker was present")
    if evidence:
        known_parts.append(
            f"corroboration was judged from {group_count} evidence passage(s) "
            f"across {distinct_domains} distinct domain(s)"
        )
    else:
        known_parts.append("no evidence passages were available")
    rationale = "Source assessment: " + "; ".join(known_parts) + "."

    return SourceAssessment(
        source_id=source.source_id,
        authority_for_question="unknown",
        primary_vs_secondary=source_type,
        methodological_quality="unknown",
        recency=recency,  # type: ignore[arg-type]
        directness=directness,
        transparency="unknown",
        conflict_of_interest=conflict_of_interest,  # type: ignore[arg-type]
        corroboration=corroboration,  # type: ignore[arg-type]
        limitations=limitations,
        rationale=rationale,
    )
