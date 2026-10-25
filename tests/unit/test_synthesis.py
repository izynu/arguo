"""Tests for arguo.synthesis.synthesizer."""

from __future__ import annotations

import asyncio

import pytest

from arguo.config import PROFILES
from arguo.exceptions import ModelOutputError
from arguo.synthesis.synthesizer import heuristic_synthesis, synthesize


def offline_synthesis(ledger, plan) -> dict:  # noqa: ANN001
    """Return the offline synthesis as a plain dict, as the pipeline consumes it."""
    return heuristic_synthesis("question", plan, ledger, offline=True).model_dump()


def test_offline_synthesis_returns_expected_shape(ledger, plan) -> None:
    result = offline_synthesis(ledger, plan)
    for key in (
        "executive_summary",
        "findings",
        "limitations",
        "gaps",
        "generated_by",
    ):
        assert key in result
    assert result["generated_by"] == "heuristic-offline"
    assert "offline demonstration mode" in result["executive_summary"]
    assert any("not model verified" in item for item in result["limitations"])


def test_findings_match_ledger_claims(ledger, plan) -> None:
    result = offline_synthesis(ledger, plan)
    by_claim = {finding["claim_id"]: finding for finding in result["findings"]}
    assert set(by_claim) == {"C1", "C2"}
    for claim in ledger.claims():
        finding = by_claim[claim.claim_id]
        assert finding["text"] == claim.text
        assert finding["evidence_ids"] == claim.evidence_ids
        assert finding["source_ids"] == claim.source_ids


def test_confidence_is_only_low_or_medium_never_high(ledger, plan) -> None:
    result = offline_synthesis(ledger, plan)
    confidences = [finding["confidence"] for finding in result["findings"]]
    assert set(confidences) <= {"low", "medium"}
    assert "high" not in confidences
    # C1 spans two independent domains: medium. C2 has one domain: low.
    by_claim = {finding["claim_id"]: finding for finding in result["findings"]}
    assert by_claim["C1"]["confidence"] == "medium"
    assert by_claim["C2"]["confidence"] == "low"


def test_gaps_cover_subquestions_without_evidence(ledger, plan) -> None:
    result = offline_synthesis(ledger, plan)
    assert any("SQ3" in gap for gap in result["gaps"])
    assert result["follow_up_queries"]


def test_synthesize_without_adapter_returns_plain_dict(ledger, plan) -> None:
    result = asyncio.run(
        synthesize("question", plan, ledger, None, PROFILES["quick"], True)
    )
    assert set(result) == {
        "executive_summary",
        "findings",
        "limitations",
        "gaps",
        "follow_up_queries",
        "generated_by",
    }
    assert result["generated_by"] == "heuristic-offline"


class Adapter:
    """Minimal adapter double returning a preset payload."""

    def __init__(self, response: dict, name: str) -> None:
        self._response = response
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def complete_json(self, prompt, schema_hint, system=None):  # noqa: ANN001
        return self._response


def test_model_output_with_unknown_claim_raises(ledger, plan) -> None:
    adapter = Adapter(
        {
            "executive_summary": "summary",
            "findings": [
                {
                    "claim_id": "C999",
                    "text": "Invented claim",
                    "evidence_ids": [],
                    "source_ids": [],
                    "confidence": "low",
                    "reason": "made up",
                }
            ],
            "limitations": [],
            "gaps": [],
            "follow_up_queries": [],
        },
        "fabricator",
    )
    with pytest.raises(ModelOutputError):
        asyncio.run(
            synthesize("question", plan, ledger, adapter, PROFILES["quick"], False)
        )


def test_model_high_confidence_is_clamped_without_two_domains(
    ledger, plan
) -> None:
    # C2 has evidence from a single domain, so "high" must be clamped.
    claim = ledger.get_claim("C2")
    assert claim is not None
    adapter = Adapter(
        {
            "executive_summary": "summary",
            "findings": [
                {
                    "claim_id": "C2",
                    "text": claim.text,
                    "evidence_ids": ["E3"],
                    "source_ids": ["S1"],
                    "confidence": "high",
                    "reason": "single domain only",
                }
            ],
            "limitations": [],
            "gaps": [],
            "follow_up_queries": [],
        },
        "overconfident",
    )
    result = asyncio.run(
        synthesize("question", plan, ledger, adapter, PROFILES["quick"], False)
    )
    finding = result["findings"][0]
    assert finding["confidence"] == "medium"
    assert "clamped to medium" in finding["reason"]
