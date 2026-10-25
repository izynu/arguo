"""Citation and claim audit for one generated report draft.

The checker validates the report against the ledger: every [S%d] and [C%d]
reference must resolve, every ledger source must be cited in the body or
listed in the "Background sources" section, every claim must carry at least
one evidence id that exists, URLs must be syntactically valid http(s), and
duplicate source URLs or widespread missing metadata are flagged.
"""

from __future__ import annotations

import re
from collections import Counter
from urllib.parse import urlparse

from arguo.evidence.ledger import EvidenceLedger
from arguo.models import AuditReport, CitationIssue
from arguo.utilities.logging import get_logger
from arguo.utilities.urls import normalize_url

logger = get_logger("arguo.verification.citations")

_S_TOKEN_RE = re.compile(r"\[S(\d+)\]")
_C_TOKEN_RE = re.compile(r"\[C(\d+)\]")

_SOURCES_HEADING = "## Sources"
_BACKGROUND_HEADING = "## Background sources"


def _split_sections(report: str) -> tuple[str, str, str]:
    """Return (body, tail, background) parts of the report.

    body: everything before the "## Sources" heading (citation-bearing text).
    tail: everything from "## Sources" onward.
    background: the "## Background sources" section of the tail, or "".
    """
    lines = report.splitlines()
    sources_index = len(lines)
    for index, line in enumerate(lines):
        if line.strip() == _SOURCES_HEADING:
            sources_index = index
            break
    body = "\n".join(lines[:sources_index])
    tail_lines = lines[sources_index:]
    tail = "\n".join(tail_lines)
    background = ""
    in_background = False
    for line in tail_lines:
        stripped = line.strip()
        if stripped == _BACKGROUND_HEADING:
            in_background = True
            background = _BACKGROUND_HEADING
            continue
        if in_background:
            if stripped.startswith("## "):
                break
            background += "\n" + line
    return body, tail, background


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


class CitationChecker:
    """Audit one report draft against the ledger it was generated from."""

    def __init__(self, ledger: EvidenceLedger, report_markdown: str) -> None:
        self._ledger = ledger
        self._report = report_markdown or ""

    def run(self) -> AuditReport:
        issues: list[CitationIssue] = []

        body, tail, background = _split_sections(self._report)
        body_s_ids = [f"S{n}" for n in _S_TOKEN_RE.findall(body)]
        all_s_ids = [f"S{n}" for n in _S_TOKEN_RE.findall(self._report)]
        all_c_ids = [f"C{n}" for n in _C_TOKEN_RE.findall(self._report)]
        background_s_ids = [f"S{n}" for n in _S_TOKEN_RE.findall(background)]

        known_sources = {source.source_id for source in self._ledger.sources()}
        known_evidence = {record.evidence_id for record in self._ledger.evidence()}

        def add_issue(issue: CitationIssue) -> None:
            issues.append(issue)

        # 1. Every [S%d] reference anywhere in the report resolves.
        for source_id in _unique(all_s_ids):
            if source_id not in known_sources:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="missing-source",
                        detail=(
                            f"Report references {source_id}, which does not exist "
                            "in the evidence ledger."
                        ),
                        source_id=source_id,
                        severity="error",
                    )
                )

        # 2. Every ledger source is cited in the body or marked background.
        cited_ids = set(body_s_ids) | set(background_s_ids)
        for source in self._ledger.sources():
            if source.source_id not in cited_ids:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="unused-source",
                        detail=(
                            f"{source.source_id} is in the ledger but is neither "
                            "cited in the report body nor listed under "
                            "Background sources."
                        ),
                        source_id=source.source_id,
                        severity="info",
                    )
                )

        # 3. Every [C%d] resolves.
        known_claims = {claim.claim_id for claim in self._ledger.claims()}
        for claim_id in _unique(all_c_ids):
            if claim_id not in known_claims:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="unresolved-reference",
                        detail=(
                            f"Report references {claim_id}, which does not exist "
                            "in the evidence ledger."
                        ),
                        claim_id=claim_id,
                        severity="error",
                    )
                )

        # 4 and 5. Claim evidence integrity.
        for claim in self._ledger.claims():
            if not claim.evidence_ids:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="unsupported-claim",
                        detail=(
                            f"Claim {claim.claim_id} has no linked evidence "
                            "records."
                        ),
                        claim_id=claim.claim_id,
                        severity="error",
                    )
                )
            for evidence_id in claim.evidence_ids:
                if evidence_id not in known_evidence:
                    add_issue(
                        CitationIssue(
                            issue_id="",
                            kind="unresolved-reference",
                            detail=(
                                f"Claim {claim.claim_id} references evidence "
                                f"{evidence_id}, which does not exist in the ledger."
                            ),
                            claim_id=claim.claim_id,
                            severity="error",
                        )
                    )

        sources = self._ledger.sources()

        # 6. URLs syntactically valid http(s).
        for source in sources:
            url = source.url
            parsed = urlparse(url)
            valid = (
                isinstance(url, str)
                and parsed.scheme in ("http", "https")
                and bool(parsed.netloc)
                and " " not in url
            )
            if not valid:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="invalid-url",
                        detail=(
                            f"{source.source_id} has a URL that is not a valid "
                            f"http(s) URL: {url!r}."
                        ),
                        source_id=source.source_id,
                        severity="error",
                    )
                )

        # 7. Duplicate source URLs.
        by_normalized: dict[str, list[str]] = {}
        for source in sources:
            try:
                key = normalize_url(source.url)
            except ValueError:
                key = source.url
            by_normalized.setdefault(key, []).append(source.source_id)
        for key, source_ids in by_normalized.items():
            if len(source_ids) > 1:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="duplicate-source",
                        detail=(
                            f"URL {key} appears in {', '.join(source_ids)}; "
                            "these may be the same document."
                        ),
                        source_id=source_ids[0],
                        severity="warning",
                    )
                )

        # 8. Missing metadata: one warning when half or more lack dates.
        if sources:
            missing_dates = sum(1 for s in sources if s.published_at is None)
            if missing_dates / len(sources) >= 0.5:
                add_issue(
                    CitationIssue(
                        issue_id="",
                        kind="missing-metadata",
                        detail=(
                            f"{missing_dates} of {len(sources)} sources have no "
                            "publication date; recency cannot be assessed for them."
                        ),
                        severity="warning",
                    )
                )

        for index, issue in enumerate(issues, start=1):
            issue.issue_id = f"ISS-{index:03d}"

        verdict_counter: Counter[str] = Counter(
            claim.verification_status.value for claim in self._ledger.claims()
        )

        return AuditReport(
            citations_checked=len(all_s_ids),
            claims_checked=len(self._ledger.claims()),
            issues=issues,
            verdict_counts=dict(sorted(verdict_counter.items())),
        )
