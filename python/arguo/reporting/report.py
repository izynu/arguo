"""Markdown research report assembly with a fixed section order.

The report is honest by construction: unknown values are rendered as
"unknown", dates are never invented, passage quotes stay verbatim, and the
audit summary quotes the automated note verbatim. No em dashes are emitted.
"""

from __future__ import annotations

import html
import re
from typing import Any

from arguo.config import ProfileConfig
from arguo.evidence.ledger import EvidenceLedger
from arguo.models import (
    AuditReport,
    ContradictionRecord,
    ResearchPlan,
    RunManifest,
    SourceAssessment,
)
from arguo.utilities.dates import format_date_or_unknown
from arguo.utilities.logging import get_logger
from arguo.utilities.text import normalize_whitespace
from arguo.utilities.urls import get_registrable_domain

logger = get_logger("arguo.reporting.report")

_S_TOKEN_RE = re.compile(r"\[S(\d+)\]")

_REQUIRED_SECTIONS = [
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

_NO_CONTRADICTION_NOTE = (
    "No material contradictions were detected by the automated scan. "
    "This does not guarantee absence of conflicts."
)


def _cell(text: Any) -> str:
    """Make a string safe for one markdown table cell."""
    value = "" if text is None else str(text)
    return normalize_whitespace(value).replace("|", "\\|")


def _assessment_map(
    assessments: list[SourceAssessment],
) -> dict[str, SourceAssessment]:
    return {assessment.source_id: assessment for assessment in assessments}


def _finding_map(synthesis: dict) -> dict[str, dict]:
    findings = {}
    for finding in synthesis.get("findings", []) or []:
        if isinstance(finding, dict) and finding.get("claim_id"):
            findings[str(finding["claim_id"])] = finding
    return findings


def build_report(
    question: str,
    plan: ResearchPlan,
    ledger: EvidenceLedger,
    assessments: list[SourceAssessment],
    contradictions: list[ContradictionRecord],
    audit: AuditReport,
    support_results: dict[str, dict],
    synthesis: dict,
    profile: ProfileConfig,
    manifest: RunManifest,
) -> str:
    """Assemble the full Markdown report with sections in fixed order."""
    lines: list[str] = []
    body_citation_text: list[str] = []
    by_assessment = _assessment_map(assessments)
    findings_by_claim = _finding_map(synthesis)
    sources = ledger.sources()
    claims = ledger.claims()

    def cite(*tokens: str) -> str:
        text = " ".join(tokens)
        body_citation_text.append(text)
        return text

    lines.append(f"# Research report: {normalize_whitespace(question)}")
    lines.append("")

    # Research question and scope -------------------------------------------
    lines.append("## Research question and scope")
    lines.append("")
    lines.append(f"Research question: {normalize_whitespace(question)}")
    if plan.since is not None or plan.until is not None:
        since_text = format_date_or_unknown(plan.since, "no start date")
        until_text = format_date_or_unknown(plan.until, "no end date")
        lines.append(f"Date range: {since_text} to {until_text}.")
    else:
        lines.append("Date range: no date restriction.")
    lines.append(
        f"Profile: {profile.name}. {profile.description} "
        f"Report length setting: {profile.report_length}."
    )
    lines.append("")

    # Method -----------------------------------------------------------------
    lines.append("## Method")
    lines.append("")
    lines.append(
        "Pipeline: intake, planning, search, retrieval and extraction, "
        "evidence linkage, gap analysis, verification (source assessment, "
        "numeric contradiction scan, claim support review), synthesis, "
        "citation audit, and report assembly."
    )
    if manifest.offline_mode:
        lines.append(
            "This run used offline fixture providers and heuristic analysis; "
            "no live search or model calls were made. All content below comes "
            "from clearly labeled fixture data."
        )
    lines.append(
        f"Search rounds used: {manifest.search_rounds_used}. "
        f"Sources retrieved: {manifest.sources_retrieved}. "
        f"Evidence records: {manifest.evidence_records}."
    )
    lines.append("")

    # Executive summary ------------------------------------------------------
    lines.append("## Executive summary")
    lines.append("")
    lines.append(str(synthesis.get("executive_summary", "")).strip() or
                 "No executive summary was produced.")
    lines.append("")

    # Main findings ----------------------------------------------------------
    lines.append("## Main findings")
    lines.append("")
    findings = synthesis.get("findings", []) or []
    if not findings:
        lines.append(
            "No findings could be produced from the collected evidence."
        )
    for index, finding in enumerate(findings, start=1):
        text = str(finding.get("text", "")).strip() or "Finding text unavailable."
        evidence_ids = [str(e) for e in finding.get("evidence_ids", []) or []]
        source_ids = [str(s) for s in finding.get("source_ids", []) or []]
        confidence = str(finding.get("confidence", "unknown"))
        reason = str(finding.get("reason", "")).strip()
        lines.append(f"{index}. {text}")
        evidence_refs = " ".join(f"[{eid}]" for eid in evidence_ids) or "none"
        source_refs = " ".join(f"[{sid}]" for sid in source_ids) or "none"
        cite(evidence_refs, source_refs)
        lines.append(
            f"   Evidence: {evidence_refs}. Sources: {source_refs}. "
            f"Confidence: {confidence}."
        )
        if reason:
            lines.append(f"   Reason: {reason}")
    lines.append("")

    # Claim and evidence table ----------------------------------------------
    lines.append("## Claim and evidence table")
    lines.append("")
    lines.append("| Claim | Evidence | Sources | Verdict | Confidence |")
    lines.append("| --- | --- | --- | --- | --- |")
    if not claims:
        lines.append("| No claims were recorded. | | | | |")
    for claim in claims:
        support = support_results.get(claim.claim_id, {}) or {}
        verdict = str(
            support.get("verdict", claim.verification_status.value)
        )
        finding = findings_by_claim.get(claim.claim_id, {})
        confidence = str(finding.get("confidence", "unknown"))
        evidence_refs = (
            " ".join(f"[{eid}]" for eid in claim.evidence_ids) or "none"
        )
        source_refs = (
            " ".join(f"[{sid}]" for sid in claim.source_ids) or "none"
        )
        cite(evidence_refs, source_refs)
        lines.append(
            f"| {_cell(claim.text)} | {evidence_refs} | {source_refs} | "
            f"{_cell(verdict)} | {_cell(confidence)} |"
        )
    lines.append("")

    # Source comparison ------------------------------------------------------
    lines.append("## Source comparison")
    lines.append("")
    lines.append("| Source | Title | Domain | Published | Type | Access note |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    if not sources:
        lines.append("| (none) | | | | | |")
    for source in sources:
        assessment = by_assessment.get(source.source_id)
        source_type = (
            assessment.primary_vs_secondary.value
            if assessment is not None
            else source.source_type.value
        )
        try:
            domain = get_registrable_domain(source.url)
        except ValueError:
            domain = "unknown"
        title = source.title if source.title else "title unknown"
        published = (
            format_date_or_unknown(source.published_at, "unknown")
            if source.published_at
            else "unknown"
        )
        access = source.access_note if source.access_note else "none"
        lines.append(
            f"| {source.source_id} | {_cell(title)} | {_cell(domain)} | "
            f"{_cell(published)} | {_cell(source_type)} | {_cell(access)} |"
        )
    lines.append("")

    # Conflicting evidence ---------------------------------------------------
    lines.append("## Conflicting evidence")
    lines.append("")
    if contradictions:
        lines.append("| Contradiction | Topic | Evidence | Sources | Description | Status |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for contradiction in contradictions:
            evidence_refs = " ".join(
                f"[{eid}]" for eid in contradiction.evidence_ids
            )
            source_refs = " ".join(
                f"[{sid}]" for sid in contradiction.source_ids
            )
            cite(evidence_refs, source_refs)
            lines.append(
                f"| {contradiction.contradiction_id} | {_cell(contradiction.topic)} | "
                f"{evidence_refs} | {source_refs} | "
                f"{_cell(contradiction.description)} | "
                f"{contradiction.resolution_status} |"
            )
    else:
        lines.append(_NO_CONTRADICTION_NOTE)
    lines.append("")

    # Strengths and weaknesses ----------------------------------------------
    lines.append("## Strengths and weaknesses of the evidence")
    lines.append("")
    evidence = ledger.evidence()
    known_dates = sum(1 for s in sources if s.published_at is not None)
    source_ids_with_evidence = {record.source_id for record in evidence}
    failed_fetches = sum(
        1
        for s in sources
        if s.access_note and s.source_id not in source_ids_with_evidence
    )
    multi_domain_claims = 0
    claims_without_evidence = 0
    corroboration = ledger.corroboration_groups()
    for claim in claims:
        domains = corroboration.get(claim.claim_id, {}).get(
            "independent_domains", []
        )
        if len(domains) >= 2:
            multi_domain_claims += 1
        if not claim.evidence_ids:
            claims_without_evidence += 1
    lines.append("Strengths:")
    lines.append(
        f"- {len(evidence)} evidence passages were captured from "
        f"{len(sources)} sources, each with a recorded retrieval time."
    )
    lines.append(
        f"- {multi_domain_claims} of {len(claims)} claims draw on evidence "
        "from two or more independent domains."
    )
    lines.append(
        f"- {known_dates} of {len(sources)} sources carry a publication date "
        "that could be parsed."
    )
    lines.append("Weaknesses:")
    lines.append(
        f"- {claims_without_evidence} of {len(claims)} claims have no linked "
        "evidence records."
    )
    lines.append(
        f"- {len(sources) - known_dates} of {len(sources)} sources have an "
        "unknown publication date."
    )
    if failed_fetches:
        lines.append(
            f"- {failed_fetches} sources could not be fully retrieved; see "
            "the access notes in the source comparison."
        )
    lines.append("")

    # Limitations and unanswered questions -----------------------------------
    lines.append("## Limitations and unanswered questions")
    lines.append("")
    limitations = synthesis.get("limitations", []) or []
    gaps = synthesis.get("gaps", []) or []
    if limitations:
        lines.append("Limitations:")
        for item in limitations:
            lines.append(f"- {item}")
    else:
        lines.append("Limitations: none recorded beyond those above.")
    lines.append("")
    if gaps:
        lines.append("Unanswered questions:")
        for item in gaps:
            lines.append(f"- {item}")
    else:
        lines.append("Unanswered questions: none recorded by the gap analysis.")
    lines.append("")

    # Confidence ---------------------------------------------------------------
    lines.append("## Confidence")
    lines.append("")
    verdict_counts = dict(audit.verdict_counts or {})
    if verdict_counts:
        counts_text = ", ".join(
            f"{count} {verdict}" for verdict, count in sorted(verdict_counts.items())
        )
        lines.append(
            f"Claim verdicts from the support review: {counts_text} "
            f"(out of {len(claims)} claims)."
        )
    else:
        lines.append(
            "No claim verdicts were recorded, so overall confidence is "
            "unassessed."
        )
    lines.append(
        "Confidence labels are qualitative (low, medium, high) and are "
        "derived only from recorded corroboration and review outcomes. The "
        "pipeline never assigns numeric scores or invented percentages."
    )
    lines.append("")

    body_text = "\n".join(body_citation_text)
    cited_ids = {f"S{n}" for n in _S_TOKEN_RE.findall(body_text)}

    # Sources ------------------------------------------------------------------
    lines.append("## Sources")
    lines.append("")
    if not sources:
        lines.append("No sources were recorded.")
    for source in sources:
        title = source.title if source.title else "title unknown"
        publisher = source.publisher if source.publisher else "publisher unknown"
        published = format_date_or_unknown(source.published_at, "date unknown")
        lines.append(
            f"[{source.source_id}] {title}, {publisher}, {source.url}, "
            f"published {published}, retrieved {source.retrieved_at}."
        )
    lines.append("")

    # Background sources -------------------------------------------------------
    lines.append("## Background sources")
    lines.append("")
    background = [s for s in sources if s.source_id not in cited_ids]
    if background:
        lines.append(
            "The following sources were collected but not cited in the body "
            "of this report:"
        )
        for source in background:
            title = source.title if source.title else "title unknown"
            lines.append(
                f"- [{source.source_id}] {title}, {source.url}"
            )
    else:
        lines.append(
            "None: every source in the ledger was cited in the report body."
        )
    lines.append("")

    # Research audit summary ---------------------------------------------------
    lines.append("## Research audit summary")
    lines.append("")
    lines.append(
        f"Citations checked: {audit.citations_checked}. "
        f"Claims checked: {audit.claims_checked}. "
        f"Errors: {audit.error_count}. Warnings: {audit.warning_count}."
    )
    if audit.verdict_counts:
        verdict_text = ", ".join(
            f"{count} {verdict}"
            for verdict, count in sorted(audit.verdict_counts.items())
        )
        lines.append(f"Verdict counts: {verdict_text}.")
    issues = audit.issues
    if issues:
        lines.append("Audit issues:")
        for issue in issues:
            lines.append(f"- [{issue.severity}] {issue.kind}: {issue.detail}")
    else:
        lines.append("No audit issues were found.")
    lines.append(audit.automated_note)
    lines.append("")

    # Suggested next steps -----------------------------------------------------
    lines.append("## Suggested next steps")
    lines.append("")
    follow_ups = synthesis.get("follow_up_queries", []) or []
    if follow_ups:
        for index, query in enumerate(follow_ups, start=1):
            lines.append(f"{index}. {query}")
    else:
        lines.append("No follow-up queries were produced.")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_UL_ITEM_RE = re.compile(r"^-\s+(.*)$")
_OL_ITEM_RE = re.compile(r"^(\d+)\.\s+(.*)$")
_CODE_SPAN_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def _inline(text: str) -> str:
    text = _CODE_SPAN_RE.sub(r"<code>\1</code>", text)
    text = _BOLD_RE.sub(r"<strong>\1</strong>", text)
    return text


def render_html(markdown: str) -> str:
    """Render Markdown to HTML with stdlib only, escaping everything first.

    The input is fully HTML-escaped before any tag insertion, so the output
    can only contain the limited tags this function adds itself: headings,
    paragraphs, list items, code spans, bold spans, and preformatted table
    blocks. Honesty over beauty: unsupported Markdown passes through as
    plain escaped text.
    """
    out: list[str] = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        "<title>Arguo report</title>",
        "</head>",
        "<body>",
    ]
    in_list: str | None = None
    in_table = False
    for raw_line in (markdown or "").splitlines():
        escaped = html.escape(raw_line)
        stripped = escaped.strip()
        if stripped.startswith("|"):
            if not in_table:
                out.append('<pre class="table">')
                in_table = True
                if in_list:
                    out.append(f"</{in_list}>")
                    in_list = None
            out.append(escaped)
            continue
        if in_table:
            out.append("</pre>")
            in_table = False
        heading = _HEADING_RE.match(stripped)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{_inline(heading.group(2))}</h{level}>")
            continue
        if not stripped:
            if in_list:
                out.append(f"</{in_list}>")
                in_list = None
            continue
        ul_item = _UL_ITEM_RE.match(stripped)
        ol_item = _OL_ITEM_RE.match(stripped)
        if ul_item or ol_item:
            wanted = "ul" if ul_item else "ol"
            if in_list != wanted:
                if in_list:
                    out.append(f"</{in_list}>")
                out.append(f"<{wanted}>")
                in_list = wanted
            content = (ul_item or ol_item).group(1)
            out.append(f"<li>{_inline(content)}</li>")
            continue
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None
        out.append(f"<p>{_inline(stripped)}</p>")
    if in_table:
        out.append("</pre>")
    if in_list:
        out.append(f"</{in_list}>")
    out.append("</body>")
    out.append("</html>")
    return "\n".join(out)
