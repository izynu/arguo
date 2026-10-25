"""Tests for arguo.reporting.report."""

from __future__ import annotations

from arguo.config import PROFILES
from arguo.models import AuditReport, RunManifest, utc_now_iso
from arguo.reporting.report import build_report, render_html

SECTION_ORDER = [
    "## Research question and scope",
    "## Method",
    "## Executive summary",
    "## Main findings",
    "## Claim and evidence table",
    "## Source comparison",
    "## Conflicting evidence",
    "## Strengths and weaknesses of the evidence",
    "## Limitations and unanswered questions",
    "## Confidence",
    "## Sources",
    "## Background sources",
    "## Research audit summary",
    "## Suggested next steps",
]

QUESTION = "Does tree cover reduce heat in cities?"


def synthesis_dict() -> dict:
    return {
        "executive_summary": "Two sources were reviewed for this demonstration.",
        "findings": [
            {
                "claim_id": "C1",
                "text": "Tree canopy covered 22 percent of the study area.",
                "evidence_ids": ["E1", "E2"],
                "source_ids": ["S1", "S2"],
                "confidence": "medium",
                "reason": "Assembled from two passages on different domains.",
            },
            {
                "claim_id": "C2",
                "text": "The cooling effect near parks is measurable.",
                "evidence_ids": ["E3"],
                "source_ids": ["S1"],
                "confidence": "low",
                "reason": "Assembled from one passage.",
            },
        ],
        "limitations": ["Heuristic plan may miss domain-specific terminology."],
        "gaps": ["No evidence was collected for subquestion SQ3."],
        "follow_up_queries": ["urban tree cover statistics"],
        "generated_by": "heuristic-offline",
    }


def manifest_dict() -> RunManifest:
    return RunManifest(
        run_id="R1",
        research_question=QUESTION,
        profile="quick",
        started_at=utc_now_iso(),
        offline_mode=True,
        search_rounds_used=1,
        sources_retrieved=2,
        evidence_records=3,
    )


def build_report_for(ledger, plan) -> str:  # noqa: ANN001
    support_results = {
        "C1": {"verdict": "supported", "method": "heuristic"},
        "C2": {"verdict": "partially-supported", "method": "heuristic"},
    }
    return build_report(
        QUESTION,
        plan,
        ledger,
        [],  # assessments: intentionally empty
        [],  # contradictions: intentionally empty
        AuditReport(),
        support_results,
        synthesis_dict(),
        PROFILES["quick"],
        manifest_dict(),
    )


def test_report_contains_all_required_headings_in_order(ledger, plan) -> None:
    report = build_report_for(ledger, plan)
    positions = [report.index(section) for section in SECTION_ORDER]
    assert positions == sorted(positions)


def test_report_renders_unknown_date_honestly(ledger, plan) -> None:
    report = build_report_for(ledger, plan)
    # S2 has published_at None: the Sources section must say "date unknown".
    assert "date unknown" in report
    assert "[S2] Example fixture: city heat measurements" in report


def test_report_has_no_em_or_en_dashes(ledger, plan) -> None:
    report = build_report_for(ledger, plan)
    assert "\u2014" not in report
    assert "\u2013" not in report


def test_report_quotes_claims_and_citations(ledger, plan) -> None:
    report = build_report_for(ledger, plan)
    assert "## Claim and evidence table" in report
    assert "Tree canopy covered 22 percent" in report
    assert "[S1]" in report and "[E1]" in report
    assert "This run used offline fixture providers" in report
    # Empty contradictions produce the honest no-conflict note.
    assert "No material contradictions were detected" in report


def test_audit_summary_quotes_automated_note(ledger, plan) -> None:
    report = build_report_for(ledger, plan)
    assert "Citations checked: 0." in report
    assert (
        "Automated checks verify internal consistency and passage support." in report
    )


def test_render_html_escapes_raw_html() -> None:
    html = render_html("# Title\n\n<script>alert(1)</script>")
    assert "&lt;script&gt;" in html
    assert "<script>" not in html
