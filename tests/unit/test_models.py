"""Tests for arguo.models validation and defaults."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from arguo.models import (
    ClaimRecord,
    EvidenceRecord,
    ResearchPlan,
    RunManifest,
    SourceRecord,
    SubQuestion,
    VerificationStatus,
)


def test_source_record_rejects_ftp_url() -> None:
    with pytest.raises(ValidationError):
        SourceRecord(source_id="S1", url="ftp://example.org/a")


def test_source_record_accepts_http_url() -> None:
    record = SourceRecord(source_id="S1", url="https://example.org/a")
    assert record.url == "https://example.org/a"


def test_published_at_none_stays_none_after_model_dump() -> None:
    record = SourceRecord(source_id="S1", url="https://example.org/a")
    assert record.published_at is None
    dumped = record.model_dump()
    assert dumped["published_at"] is None


def test_models_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        SourceRecord(source_id="S1", url="https://example.org/a", bogus="x")
    with pytest.raises(ValidationError):
        ClaimRecord(claim_id="C1", text="t", nope=1)


def test_evidence_record_defaults_are_explicit() -> None:
    record = EvidenceRecord(
        evidence_id="E1", source_id="S1", source_url="https://example.org/a",
        relevant_passage="A passage.",
    )
    assert record.verification_status is VerificationStatus.REQUIRES_HUMAN_REVIEW
    assert record.supports_or_contradicts.value == "supports"
    assert record.relevance.value == "direct"
    assert record.claim_ids == []
    with pytest.raises(ValidationError):
        EvidenceRecord(
            evidence_id="E1", source_id="S1", source_url="https://example.org/a",
            relevant_passage="",
        )


def test_claim_record_kind_is_a_closed_vocabulary() -> None:
    ClaimRecord(claim_id="C1", text="t", claim_kind="fact")
    with pytest.raises(ValidationError):
        ClaimRecord(claim_id="C1", text="t", claim_kind="hypothesis")


def test_research_plan_all_queries_dedupes_in_order() -> None:
    plan = ResearchPlan(
        research_question="q",
        subquestions=[
            SubQuestion(subquestion_id="SQ1", text="a", search_queries=["x", "y"]),
            SubQuestion(subquestion_id="SQ2", text="b", search_queries=["y", "z"]),
        ],
    )
    assert plan.all_queries == ["x", "y", "z"]


def test_verification_status_has_the_six_values() -> None:
    assert {status.value for status in VerificationStatus} == {
        "supported",
        "partially-supported",
        "contradicted",
        "insufficient-evidence",
        "source-unavailable",
        "requires-human-review",
    }
    assert len(VerificationStatus) == 6


def test_run_manifest_defaults() -> None:
    manifest = RunManifest(
        run_id="R1", research_question="q", profile="quick", started_at="now"
    )
    assert manifest.offline_mode is False
    assert manifest.stages == []
    assert manifest.warnings == []
