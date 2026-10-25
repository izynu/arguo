"""Tests for arguo.verification.assessor."""

from __future__ import annotations

from datetime import date, timedelta

from arguo.evidence.ledger import EvidenceLedger
from arguo.models import SourceType
from arguo.verification.assessor import assess_source


def iso_days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def test_unknown_fields_stay_unknown_when_data_is_missing() -> None:
    ledger = EvidenceLedger()
    source = ledger.add_source(url="https://example.org/a")
    assessment = assess_source(source, [])
    assert assessment.authority_for_question == "unknown"
    assert assessment.methodological_quality == "unknown"
    assert assessment.transparency == "unknown"
    assert assessment.conflict_of_interest == "unknown"
    assert assessment.primary_vs_secondary is SourceType.UNKNOWN
    assert any("stays unknown" in item for item in assessment.limitations)


def test_gov_and_edu_urls_are_confident_primary() -> None:
    ledger = EvidenceLedger()
    gov = ledger.add_source(url="https://www.census.gov/data.html")
    assert assess_source(gov, []).primary_vs_secondary is SourceType.PRIMARY


def test_recency_six_months_ago_is_current() -> None:
    ledger = EvidenceLedger()
    source = ledger.add_source(
        url="https://example.org/recent", published_at=iso_days_ago(183)
    )
    assert assess_source(source, []).recency == "current"


def test_recency_four_years_is_aging_and_ten_is_outdated() -> None:
    # The rubric buckets are: up to 2 years current, up to 5 years aging,
    # older than 5 years outdated. Four years therefore lands in "aging".
    ledger = EvidenceLedger()
    mid = ledger.add_source(
        url="https://example.org/mid", published_at=iso_days_ago(4 * 365 + 1)
    )
    assert assess_source(mid, []).recency == "aging"
    old = ledger.add_source(
        url="https://example.org/old", published_at=iso_days_ago(10 * 365)
    )
    assert assess_source(old, []).recency == "outdated"


def test_recency_unknown_when_no_date() -> None:
    ledger = EvidenceLedger()
    source = ledger.add_source(url="https://example.org/none")
    assessment = assess_source(source, [])
    assert assessment.recency == "unknown"
    assert "publication date is unknown" in assessment.limitations


def test_corroboration_independent_when_evidence_spans_two_domains() -> None:
    ledger = EvidenceLedger()
    s1 = ledger.add_source(url="https://example.org/a")
    s2 = ledger.add_source(url="https://example.net/b")
    e1 = ledger.add_evidence(s1.source_id, s1.url, "Passage one.")
    e2 = ledger.add_evidence(s2.source_id, s2.url, "Passage two.")
    assessment = assess_source(s1, [e1, e2])
    assert assessment.corroboration == "independent"
    single = assess_source(s1, [e1])
    assert single.corroboration == "single-source"
    empty = assess_source(s1, [])
    assert empty.corroboration == "unknown"
    assert any("corroboration stays unknown" in item for item in empty.limitations)


def test_conflict_of_interest_markers() -> None:
    ledger = EvidenceLedger()
    source = ledger.add_source(
        url="https://example.org/study", snippets=["The team declares no competing interests."]
    )
    assert assess_source(source, []).conflict_of_interest == "none-known"
    source2 = ledger.add_source(
        url="https://example.org/study2", snippets=["Author holds a conflict of interest statement."]
    )
    assert assess_source(source2, []).conflict_of_interest == "declared"


def test_rationale_names_known_fields_and_no_scores() -> None:
    ledger = EvidenceLedger()
    source = ledger.add_source(
        url="https://example.org/a", published_at="2024-05-01"
    )
    assessment = assess_source(source, [])
    assert assessment.rationale.startswith("Source assessment: ")
    assert "2024-05-01" in assessment.rationale
    # No numeric quality score exists anywhere on the assessment.
    assert not hasattr(assessment, "score")
