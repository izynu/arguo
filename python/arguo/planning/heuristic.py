"""Deterministic heuristic research planner.

This planner is the offline fallback for stage B. It uses a fixed set of
subquestion templates and query variants derived from the question terms, so
the same question and profile always produce the same plan. It never invents
facts or dates: it only decides what to search for.
"""

from __future__ import annotations

import re
from datetime import date

from arguo.config import ProfileConfig
from arguo.models import ResearchPlan, SubQuestion
from arguo.utilities.text import normalize_whitespace

_TOKEN_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "with", "from", "by", "as", "is", "are", "was", "were", "be", "been",
    "being", "am", "do", "does", "did", "has", "have", "had", "can", "could",
    "should", "would", "will", "shall", "may", "might", "must", "what",
    "which", "who", "whom", "whose", "why", "how", "when", "where", "it",
    "its", "this", "that", "these", "those", "there", "their", "about",
    "into", "over", "under", "more", "most", "than", "then", "also", "very",
}

_MAX_KEYWORD_TOKENS = 10

_QUERIES_PER_SUBQUESTION = 3


def _keywords(question: str) -> str:
    """Extract the content terms of the question as a lowercase phrase."""
    tokens = _TOKEN_RE.findall(question.lower())
    kept = [t for t in tokens if t not in _STOPWORDS]
    if not kept:
        return normalize_whitespace(question.lower())
    return " ".join(kept[:_MAX_KEYWORD_TOKENS])


def _queries(
    question: str,
    kw: str,
    variants: list[str],
    scholarly_variants: list[str],
    scholarly_mode: bool,
    since: date | None,
    year_terms: list[str],
) -> list[str]:
    """Build a deduplicated, capped query list: raw question, variants, extras.

    In scholarly mode the scholarly variants come first so they survive the
    per-subquestion query cap.
    """
    queries: list[str] = [normalize_whitespace(question)]
    if scholarly_mode:
        queries.extend(scholarly_variants)
    for query in variants:
        queries.append(query)
    if since is not None:
        queries.extend(year_terms)
    deduped: list[str] = []
    for query in queries:
        cleaned = normalize_whitespace(query)
        if cleaned and cleaned not in deduped:
            deduped.append(cleaned)
    return deduped[:_QUERIES_PER_SUBQUESTION]


def heuristic_plan(
    question: str,
    profile: ProfileConfig,
    since: date | None = None,
    domain: str | None = None,
) -> ResearchPlan:
    """Produce a deterministic ResearchPlan without any model call.

    The plan decomposes the question into at most profile.subquestion_target
    subquestions drawn from a fixed template set: definition, current state,
    key numbers, recent developments, evidence for and against, and causes.
    Each subquestion carries 2-3 search queries built from the question
    terms, plus scholarly and year variants when applicable.
    """
    kw = _keywords(question)
    scholarly_mode = bool(profile.scholarly_mode)

    template_specs: list[dict] = [
        {
            "key": "definition",
            "text": f"What is {kw}, and how do authoritative sources define or measure it?",
            "priority": 1,
            "variants": [f"{kw} definition", f"{kw} explained"],
            "scholarly": [f"{kw} study"],
            "year_terms": [],
            "evidence_requirements": (
                "An authoritative definition or measurement standard with a citable source."
            ),
            "preferred_source_types": ["reference", "secondary"],
            "time_constraint": None,
        },
        {
            "key": "current-state",
            "text": f"What is the current state of {kw}?",
            "priority": 1,
            "variants": [f"{kw} latest"],
            "scholarly": [f"{kw} systematic review"],
            "year_terms": [f"{kw} {since.year}"] if since else [],
            "evidence_requirements": (
                "Current status reporting from a primary or high-quality secondary source."
            ),
            "preferred_source_types": ["primary", "secondary"],
            "time_constraint": f"on or after {since.isoformat()}" if since else None,
        },
        {
            "key": "key-numbers",
            "text": f"What key numbers or statistics describe {kw}?",
            "priority": 2,
            "variants": [f"{kw} statistics", f"{kw} data"],
            "scholarly": [f"{kw} meta-analysis"],
            "year_terms": [],
            "evidence_requirements": (
                "Numeric values with source, date, units, and measurement definition."
            ),
            "preferred_source_types": ["primary", "secondary"],
            "time_constraint": None,
        },
        {
            "key": "recent-developments",
            "text": f"What have been the most recent developments involving {kw}?",
            "priority": 2,
            "variants": (
                [f"{kw} latest", f"{kw} since {since.year}"]
                if since
                else [f"{kw} latest", f"{kw} news"]
            ),
            "scholarly": [],
            "year_terms": [],
            "evidence_requirements": (
                "Dated reports or announcements covering the recent period."
            ),
            "preferred_source_types": ["primary"],
            "time_constraint": f"on or after {since.isoformat()}" if since else None,
        },
        {
            "key": "for-and-against",
            "text": f"What is the evidence for and against competing claims about {kw}?",
            "priority": 2 if profile.contradiction_focus else 3,
            "variants": [f"{kw} criticism", f"{kw} debate"],
            "scholarly": [f"{kw} systematic review"],
            "year_terms": [],
            "evidence_requirements": (
                "Evidence both supporting and contradicting the competing claims."
            ),
            "preferred_source_types": ["primary", "secondary"],
            "time_constraint": None,
        },
        {
            "key": "causes",
            "text": f"What factors cause or drive changes in {kw}?",
            "priority": 3,
            "variants": [f"{kw} causes", f"{kw} drivers"],
            "scholarly": [f"{kw} study"],
            "year_terms": [],
            "evidence_requirements": (
                "Analysis or research attributing causes, with stated uncertainty."
            ),
            "preferred_source_types": ["primary", "secondary"],
            "time_constraint": None,
        },
    ]

    selected = template_specs[: max(1, profile.subquestion_target)]
    subquestions: list[SubQuestion] = []
    for index, spec in enumerate(selected, start=1):
        subquestions.append(
            SubQuestion(
                subquestion_id=f"SQ{index}",
                text=spec["text"],
                priority=spec["priority"],
                search_queries=_queries(
                    question=question,
                    kw=kw,
                    variants=spec["variants"],
                    scholarly_variants=spec["scholarly"],
                    scholarly_mode=scholarly_mode,
                    since=since,
                    year_terms=spec["year_terms"],
                ),
                evidence_requirements=spec["evidence_requirements"],
                preferred_source_types=spec["preferred_source_types"],
                time_constraint=spec["time_constraint"],
            )
        )

    limitations = [
        "Heuristic plan may miss domain-specific terminology.",
        "Without a live model, query diversity is limited.",
    ]
    if since is None:
        limitations.append(
            "No explicit time boundary was supplied, so recency control depends on query terms."
        )

    return ResearchPlan(
        research_question=normalize_whitespace(question),
        domain=domain,
        depth=profile.name,
        since=since,
        subquestions=subquestions,
        anticipated_limitations=limitations,
        notes=(
            f"Deterministic heuristic plan for profile '{profile.name}'. "
            "Templates are fixed; queries come from question terms only."
        ),
        generated_by="heuristic",
    )
