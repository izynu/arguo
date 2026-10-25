"""Typed data models shared across the research pipeline.

All records are Pydantic models so that missing values stay explicit and
serialization to JSON is schema checked. Unknown dates, authors, and licenses
are represented with None, never fabricated.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

DateUnknown = Literal[None]


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


class VerificationStatus(StrEnum):
    SUPPORTED = "supported"
    PARTIALLY_SUPPORTED = "partially-supported"
    CONTRADICTED = "contradicted"
    INSUFFICIENT_EVIDENCE = "insufficient-evidence"
    SOURCE_UNAVAILABLE = "source-unavailable"
    REQUIRES_HUMAN_REVIEW = "requires-human-review"


class Relevance(StrEnum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    INFERRED = "inferred"


class SourceType(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    UNKNOWN = "unknown"


class SupportRelation(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT = "context"


class SourceRecord(BaseModel):
    """A retrieved source with provenance. Retrieval time is always recorded."""

    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(description="Stable id such as S1, S2 used in reports")
    url: str
    final_url: str | None = None
    title: str | None = None
    publisher: str | None = None
    author: str | None = None
    source_type: SourceType = SourceType.UNKNOWN
    published_at: str | None = Field(default=None, description="Publication date if actually known")
    updated_at: str | None = None
    event_or_observation_date: str | None = None
    retrieved_at: str = Field(default_factory=utc_now_iso)
    content_type: str | None = None
    content_hash: str | None = None
    license: str | None = None
    provider: str | None = Field(default=None, description="Search provider that surfaced this source")
    snippets: list[str] = Field(default_factory=list)
    access_note: str | None = Field(default=None, description="For example paywall, robots block, timeout")
    domains_seen_in: list[str] = Field(default_factory=list, description="Registrable domains that cited or repeated this source")

    @field_validator("url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("source url must be http(s)")
        return v


class EvidenceRecord(BaseModel):
    """One evidentiary passage linked to its source and claim context."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str
    claim_ids: list[str] = Field(default_factory=list, description="Claims this passage bears on")
    source_id: str
    source_url: str
    source_title: str | None = None
    relevant_passage: str = Field(min_length=1)
    passage_locator: str | None = Field(default=None, description="Heading, section, or offset when known")
    source_type: SourceType = SourceType.UNKNOWN
    author_or_publisher: str | None = None
    published_at: str | None = None
    updated_at: str | None = None
    event_or_observation_date: str | None = None
    retrieved_at: str = Field(default_factory=utc_now_iso)
    supports_or_contradicts: SupportRelation = SupportRelation.SUPPORTS
    relevance: Relevance = Relevance.DIRECT
    methodology_notes: str | None = None
    independence_group: str | None = Field(default=None, description="Registrable domain or syndication group")
    limitations: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = VerificationStatus.REQUIRES_HUMAN_REVIEW
    content_hash: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)


class ClaimRecord(BaseModel):
    """A factual assertion extracted from or checked against evidence."""

    model_config = ConfigDict(extra="forbid")

    claim_id: str
    text: str
    evidence_ids: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    subquestion_id: str | None = None
    claim_kind: Literal["fact", "estimate", "interpretation", "comparison", "unknown"] = "unknown"
    verification_status: VerificationStatus = VerificationStatus.REQUIRES_HUMAN_REVIEW
    support_review: dict[str, Any] | None = Field(default=None, description="Outcome of the support review stage")
    notes: str | None = None


class SubQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subquestion_id: str
    text: str
    priority: int = Field(default=2, ge=1, le=3)
    search_queries: list[str] = Field(default_factory=list)
    evidence_requirements: str | None = None
    preferred_source_types: list[str] = Field(default_factory=list)
    time_constraint: str | None = None


class ResearchPlan(BaseModel):
    """Stage B output: structured, inspectable, and editable."""

    model_config = ConfigDict(extra="forbid")

    research_question: str
    domain: str | None = None
    audience: str | None = None
    depth: str = "standard"
    time_boundary: str | None = Field(default=None, description="Date range constraint stated in the request")
    since: date | None = None
    until: date | None = None
    subquestions: list[SubQuestion] = Field(default_factory=list)
    anticipated_limitations: list[str] = Field(default_factory=list)
    notes: str | None = None
    generated_by: str = "heuristic"
    created_at: str = Field(default_factory=utc_now_iso)

    @property
    def all_queries(self) -> list[str]:
        seen: list[str] = []
        for sq in self.subquestions:
            for q in sq.search_queries:
                if q not in seen:
                    seen.append(q)
        return seen


class SourceAssessment(BaseModel):
    """Stage output of the transparent source quality rubric."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    authority_for_question: Literal["high", "medium", "low", "unknown"] = "unknown"
    primary_vs_secondary: SourceType = SourceType.UNKNOWN
    methodological_quality: Literal["strong", "adequate", "weak", "not-applicable", "unknown"] = "unknown"
    recency: Literal["current", "aging", "outdated", "unknown"] = "unknown"
    directness: Relevance = Relevance.DIRECT
    transparency: Literal["documented", "partial", "opaque", "unknown"] = "unknown"
    conflict_of_interest: Literal["none-known", "possible", "declared", "unknown"] = "unknown"
    corroboration: Literal["independent", "syndicated", "single-source", "unknown"] = "unknown"
    limitations: list[str] = Field(default_factory=list)
    rationale: str = ""


class ContradictionRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contradiction_id: str
    topic: str
    evidence_ids: list[str]
    source_ids: list[str]
    description: str
    resolution_status: Literal["unresolved", "explained", "one-source-weaker", "measurement-difference"] = "unresolved"
    notes: str | None = None


class CitationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    issue_id: str
    kind: Literal[
        "missing-source", "unused-source", "invalid-url", "fabricated-citation",
        "unsupported-claim", "duplicate-source", "unresolved-reference", "missing-metadata",
    ]
    detail: str
    claim_id: str | None = None
    source_id: str | None = None
    severity: Literal["error", "warning", "info"] = "warning"


class AuditReport(BaseModel):
    """Stage I output: everything the citation and claim audit found."""

    model_config = ConfigDict(extra="forbid")

    citations_checked: int = 0
    claims_checked: int = 0
    issues: list[CitationIssue] = Field(default_factory=list)
    verdict_counts: dict[str, int] = Field(default_factory=dict)
    automated_note: str = (
        "Automated checks verify internal consistency and passage support. "
        "They cannot guarantee truth."
    )
    generated_at: str = Field(default_factory=utc_now_iso)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


class StageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: str
    status: Literal["ok", "partial", "failed", "skipped"]
    started_at: str
    finished_at: str
    duration_ms: int
    details: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class RunManifest(BaseModel):
    """Observable record of one research run: stages, budgets, and outcomes."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    research_question: str
    profile: str
    started_at: str
    finished_at: str | None = None
    stages: list[StageResult] = Field(default_factory=list)
    providers: dict[str, str] = Field(default_factory=dict)
    budget_snapshot: dict[str, Any] = Field(default_factory=dict)
    search_rounds_used: int = 0
    sources_retrieved: int = 0
    evidence_records: int = 0
    model_calls: int = 0
    offline_mode: bool = False
    warnings: list[str] = Field(default_factory=list)


class NormalizedResult(BaseModel):
    """Provider independent search result. Providers map into this shape."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    url: str
    snippet: str | None = None
    published_at: str | None = None
    score: float | None = None
    provider: str
    raw_metadata: dict[str, Any] = Field(default_factory=dict)
