"""Tests for arguo.evidence.ledger."""

from __future__ import annotations

import json

import pytest

from arguo.evidence.ledger import EvidenceLedger
from arguo.exceptions import InvalidSourceError


def test_sequential_ids_are_s1_e1_c1(ledger: EvidenceLedger) -> None:
    assert [s.source_id for s in ledger.sources()] == ["S1", "S2"]
    assert [e.evidence_id for e in ledger.evidence()] == ["E1", "E2", "E3"]
    assert [c.claim_id for c in ledger.claims()] == ["C1", "C2"]
    fresh = EvidenceLedger()
    fresh.add_source(url="https://example.org/x")
    assert fresh.sources()[0].source_id == "S1"
    fresh.add_evidence("S1", "https://example.org/x", "passage")
    assert fresh.evidence()[0].evidence_id == "E1"
    fresh.add_claim(text="fresh claim")
    assert fresh.claims()[0].claim_id == "C1"


def test_add_evidence_requires_known_source() -> None:
    ledger = EvidenceLedger()
    with pytest.raises(InvalidSourceError):
        ledger.add_evidence(
            source_id="S9", source_url="https://example.org/x", relevant_passage="p"
        )


def test_link_raises_on_unknown_ids(ledger: EvidenceLedger) -> None:
    with pytest.raises(InvalidSourceError):
        ledger.link("C99", "E1")
    with pytest.raises(InvalidSourceError):
        ledger.link("C1", "E99")


def test_link_updates_both_sides(ledger: EvidenceLedger) -> None:
    c1 = ledger.get_claim("C1")
    e1 = ledger.get_evidence("E1")
    e2 = ledger.get_evidence("E2")
    assert c1 is not None and e1 is not None and e2 is not None
    assert c1.evidence_ids == ["E1", "E2"]
    assert c1.source_ids == ["S1", "S2"]
    assert e1.claim_ids == ["C1"]
    assert e2.claim_ids == ["C1"]
    # Linking twice is a no-op, not a duplicate.
    ledger.link("C1", "E1")
    assert c1.evidence_ids == ["E1", "E2"]
    assert e1.claim_ids == ["C1"]


def test_corroboration_groups_mark_c1_independent_with_two_domains(
    ledger: EvidenceLedger,
) -> None:
    groups = ledger.corroboration_groups()
    c1 = groups["C1"]
    assert c1["independent_domains"] == ["example.net", "example.org"]
    assert c1["distinct_independent_domains"] == 2
    assert c1["syndication_suspected"] is False
    c2 = groups["C2"]
    assert c2["distinct_independent_domains"] == 1


def test_syndication_grouped_with_limitation_note() -> None:
    ledger = EvidenceLedger()
    s1 = ledger.add_source(url="https://example.org/a")
    s2 = ledger.add_source(url="https://example.net/b")
    passage = "The demonstration dataset reports a value of 42 units for the metric."
    ledger.add_evidence(s1.source_id, s1.url, passage)
    ledger.add_evidence(s2.source_id, s2.url, passage)
    claim = ledger.add_claim(text=passage)
    ledger.link(claim.claim_id, "E1")
    ledger.link(claim.claim_id, "E2")
    groups = ledger.corroboration_groups()
    info = groups[claim.claim_id]
    assert info["syndication_suspected"] is True
    assert info["syndication_groups"] == [["E1", "E2"]]
    for evidence_id in ("E1", "E2"):
        record = ledger.get_evidence(evidence_id)
        assert record is not None
        assert "possible syndication or shared upstream source" in record.limitations
        assert record.independence_group == "syndication:E1"


def test_to_dict_from_dict_roundtrip_preserves_counts_and_ids(
    ledger: EvidenceLedger,
) -> None:
    payload = ledger.to_dict()
    assert set(payload) == {"sources", "evidence", "claims"}
    payload_json = json.dumps(payload)
    assert json.loads(payload_json)
    rebuilt = EvidenceLedger.from_dict(json.loads(payload_json))
    assert [s.source_id for s in rebuilt.sources()] == ["S1", "S2"]
    assert [e.evidence_id for e in rebuilt.evidence()] == ["E1", "E2", "E3"]
    assert [c.claim_id for c in rebuilt.claims()] == ["C1", "C2"]
    assert len(rebuilt.claims()[0].evidence_ids) == 2
    # Id counters continue where the loaded ledger left off.
    next_source = rebuilt.add_source(url="https://example.org/next")
    assert next_source.source_id == "S3"


def test_domain_grouping_and_known_urls(ledger: EvidenceLedger) -> None:
    grouped = ledger.sources_by_domain()
    assert set(grouped) == {"example.org", "example.net"}
    assert ledger.known_source_urls() == {
        "https://example.org/tree-cover",
        "https://example.net/urban-heat",
    }
