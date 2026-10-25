"""Tests for arguo.verification.contradictions."""

from __future__ import annotations

import asyncio

from arguo.evidence.ledger import EvidenceLedger
from arguo.verification.contradictions import (
    detect_numeric_contradictions,
    extract_numbers,
    model_contradiction_scan_async,
)


def conflicting_numbers_ledger(same_domain: bool) -> EvidenceLedger:
    ledger = EvidenceLedger()
    s1 = ledger.add_source(url="https://example.org/a")
    if same_domain:
        s2 = ledger.add_source(url="https://example.org/also-a")
    else:
        s2 = ledger.add_source(url="https://example.net/b")
    e1 = ledger.add_evidence(
        s1.source_id, s1.url, "The survey reports 43 percent support."
    )
    e2 = ledger.add_evidence(
        s2.source_id, s2.url, "The second survey reports 58 percent support."
    )
    claim = ledger.add_claim(text="Support for the measure differs by survey.")
    ledger.link(claim.claim_id, e1.evidence_id)
    ledger.link(claim.claim_id, e2.evidence_id)
    return ledger


def test_different_numbers_different_domains_produce_one_contradiction() -> None:
    contradictions = detect_numeric_contradictions(
        conflicting_numbers_ledger(same_domain=False).evidence()
    )
    assert len(contradictions) == 1
    record = contradictions[0]
    assert record.contradiction_id == "X1"
    assert record.topic == "claim C1"
    assert record.evidence_ids == ["E1", "E2"]
    assert record.source_ids == ["S1", "S2"]
    assert record.resolution_status == "unresolved"
    assert "43" in record.description and "58" in record.description


def test_same_domain_numbers_are_not_a_contradiction() -> None:
    contradictions = detect_numeric_contradictions(
        conflicting_numbers_ledger(same_domain=True).evidence()
    )
    assert contradictions == []


def test_passages_without_numbers_produce_no_contradictions() -> None:
    ledger = EvidenceLedger()
    s1 = ledger.add_source(url="https://example.org/a")
    s2 = ledger.add_source(url="https://example.net/b")
    e1 = ledger.add_evidence(s1.source_id, s1.url, "The study reports broad agreement.")
    e2 = ledger.add_evidence(s2.source_id, s2.url, "The second study agrees broadly.")
    claim = ledger.add_claim(text="The studies agree.")
    ledger.link(claim.claim_id, e1.evidence_id)
    ledger.link(claim.claim_id, e2.evidence_id)
    assert detect_numeric_contradictions(ledger.evidence()) == []


def test_shared_fixture_ledger_has_no_numeric_conflicts(ledger: EvidenceLedger) -> None:
    assert detect_numeric_contradictions(ledger.evidence()) == []


def test_extract_numbers_with_units_and_thousands() -> None:
    assert extract_numbers("The route is 12,345.6 km long.") == [(12345.6, "km")]
    assert extract_numbers("Share rose 45%.") == [(45.0, "%")]
    assert extract_numbers("Pi is about 3.14.") == [(3.14, None)]


def test_extract_numbers_skips_bare_small_integers() -> None:
    # A bare small integer with no unit, dot, or comma is an index, not data.
    assert extract_numbers("The rating was a 7.") == []
    assert extract_numbers("No numbers here at all.") == []


def test_different_units_never_compare() -> None:
    ledger = EvidenceLedger()
    s1 = ledger.add_source(url="https://example.org/a")
    s2 = ledger.add_source(url="https://example.net/b")
    e1 = ledger.add_evidence(s1.source_id, s1.url, "It measured 1.2 C.")
    e2 = ledger.add_evidence(s2.source_id, s2.url, "It measured 2.5 km.")
    claim = ledger.add_claim(text="values differ")
    ledger.link(claim.claim_id, e1.evidence_id)
    ledger.link(claim.claim_id, e2.evidence_id)
    assert detect_numeric_contradictions(ledger.evidence()) == []


async def _scan(ledger, adapter):  # noqa: ANN001
    return await model_contradiction_scan_async(ledger, adapter)


def test_model_scan_without_adapter_returns_empty(ledger: EvidenceLedger) -> None:
    assert asyncio.run(_scan(ledger, None)) == []


def test_model_scan_failure_is_contained(ledger: EvidenceLedger) -> None:
    class Adapter:
        name = "failing"

        async def complete_json(self, prompt, schema_hint, system=None):  # noqa: ANN001
            raise RuntimeError("model down")

    assert asyncio.run(_scan(ledger, Adapter())) == []


def test_model_scan_output_is_validated_against_ledger(
    ledger: EvidenceLedger,
) -> None:
    class Adapter:
        name = "fabricator"

        async def complete_json(self, prompt, schema_hint, system=None):  # noqa: ANN001
            return {
                "contradictions": [
                    {
                        "claim_id": "C999",
                        "evidence_ids": ["E1"],
                        "source_ids": ["S1"],
                        "description": "Invented claim id must be dropped.",
                    },
                    {
                        "claim_id": "C1",
                        "evidence_ids": ["E1", "E999"],
                        "source_ids": ["S1"],
                        "description": "Unknown evidence ids are filtered.",
                    },
                    {
                        "claim_id": "C1",
                        "evidence_ids": ["E1", "E2"],
                        "source_ids": ["S1", "S2"],
                        "description": "A real model reported contradiction.",
                    },
                ]
            }

    results = asyncio.run(_scan(ledger, Adapter()))
    assert len(results) == 2
    assert results[0].evidence_ids == ["E1"]  # unknown E999 filtered, record kept
    assert results[0].description == "Unknown evidence ids are filtered."
    assert results[1].evidence_ids == ["E1", "E2"]
    assert "model-assisted scan by fabricator" in (results[1].notes or "")
