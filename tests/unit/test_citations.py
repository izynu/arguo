"""Tests for arguo.verification.citations."""

from __future__ import annotations

from arguo.evidence.ledger import EvidenceLedger
from arguo.verification.citations import CitationChecker


def make_report(body: str = "Canopy covered 22 percent of the area. [S1] [C1]") -> str:
    return (
        "# Research report: demo\n\n"
        f"{body}\n\n"
        "## Sources\n\n"
        "[S1] Example fixture: urban tree canopy data, publisher, "
        "https://example.org/tree-cover, published 2024-05-01.\n"
        "[S2] Example fixture: city heat measurements, publisher, "
        "https://example.net/urban-heat, published date unknown.\n"
    )


def issues_by_kind(audit) -> dict[str, list]:  # noqa: ANN001
    grouped: dict[str, list] = {}
    for issue in audit.issues:
        grouped.setdefault(issue.kind, []).append(issue)
    return grouped


def test_report_citing_s1_and_c1_has_zero_errors(ledger: EvidenceLedger) -> None:
    audit = CitationChecker(ledger, make_report()).run()
    assert audit.error_count == 0
    grouped = issues_by_kind(audit)
    # S2 is never cited in the body: that is informational, not an error.
    unused = grouped.get("unused-source", [])
    assert [issue.source_id for issue in unused] == ["S2"]
    assert unused[0].severity == "info"
    # Half of the sources lack publication dates: a warning.
    metadata = grouped.get("missing-metadata", [])
    assert len(metadata) == 1 and metadata[0].severity == "warning"


def test_nonexistent_source_reference_is_a_missing_source_error(
    ledger: EvidenceLedger,
) -> None:
    audit = CitationChecker(ledger, make_report("[S9] ghost [C1]")).run()
    grouped = issues_by_kind(audit)
    missing = grouped.get("missing-source", [])
    assert [issue.source_id for issue in missing] == ["S9"]
    assert missing[0].severity == "error"
    assert missing[0].issue_id == "ISS-001"


def test_claim_without_evidence_is_an_unsupported_claim_error() -> None:
    ledger = EvidenceLedger()
    ledger.add_source(url="https://example.org/plain")
    ledger.add_claim(text="Nobody linked evidence to this claim.")
    audit = CitationChecker(ledger, make_report("[S1] [C1]")).run()
    grouped = issues_by_kind(audit)
    unsupported = grouped.get("unsupported-claim", [])
    assert [issue.claim_id for issue in unsupported] == ["C1"]
    assert unsupported[0].severity == "error"


def test_uncited_source_is_an_unused_source_info(ledger: EvidenceLedger) -> None:
    audit = CitationChecker(ledger, make_report()).run()
    grouped = issues_by_kind(audit)
    unused = grouped.get("unused-source", [])
    assert [issue.source_id for issue in unused] == ["S2"]
    assert unused[0].severity == "info"


def test_background_sources_section_counts_as_cited(
    ledger: EvidenceLedger,
) -> None:
    report = (
        "# Research report: demo\n\n"
        "Body cites [S1] and [C1] only.\n\n"
        "## Sources\n\n"
        "[S1] Example fixture: urban tree canopy data, publisher, "
        "https://example.org/tree-cover.\n"
        "## Background sources\n\n"
        "- [S2] Example fixture: city heat measurements, "
        "https://example.net/urban-heat\n"
    )
    audit = CitationChecker(ledger, report).run()
    grouped = issues_by_kind(audit)
    assert grouped.get("unused-source", []) == []


def test_invalid_and_duplicate_urls_are_reported() -> None:
    ledger = EvidenceLedger()
    ledger.add_source(url="https://example.org/a b")
    ledger.add_source(url="https://example.net/dup")
    ledger.add_source(url="https://EXAMPLE.NET/dup")
    audit = CitationChecker(ledger, make_report("[S1] [S2] [S3]")).run()
    grouped = issues_by_kind(audit)
    invalid = grouped.get("invalid-url", [])
    assert [issue.source_id for issue in invalid] == ["S1"]
    duplicates = grouped.get("duplicate-source", [])
    assert len(duplicates) == 1 and duplicates[0].severity == "warning"


def test_counts_and_verdict_tallies(ledger: EvidenceLedger) -> None:
    audit = CitationChecker(ledger, make_report()).run()
    assert audit.citations_checked == 3  # [S1] in body plus [S1] and [S2] in Sources
    assert audit.claims_checked == 2
    assert audit.verdict_counts == {"requires-human-review": 2}
    ids = [issue.issue_id for issue in audit.issues]
    assert ids == [f"ISS-{i:03d}" for i in range(1, len(ids) + 1)]
