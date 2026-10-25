"""Verification: source assessment, citation auditing, support review, contradictions."""

from __future__ import annotations

from arguo.models import EvidenceRecord
from arguo.verification.assessor import assess_source
from arguo.verification.citations import CitationChecker
from arguo.verification.contradictions import (
    detect_numeric_contradictions,
    model_contradiction_scan,
)
from arguo.verification.support import support_review

__all__ = [
    "EvidenceRecord",
    "assess_source",
    "CitationChecker",
    "detect_numeric_contradictions",
    "model_contradiction_scan",
    "support_review",
]
