"""Evidence collection: fetch, extract, split, and ledger search results.

This module turns normalized search results into ledger evidence records.
Every passage keeps explicit unknowns (publication dates stay None when the
provider did not supply one), a content hash, and provenance pointing back to
the retrieval path.
"""

from __future__ import annotations

import hashlib
import re

from arguo.config import BudgetTracker
from arguo.evidence.ledger import EvidenceLedger
from arguo.exceptions import BudgetExceededError
from arguo.extraction.extractor import extract_from_fetch
from arguo.models import NormalizedResult, Relevance, SubQuestion, SupportRelation
from arguo.retrieval.fetcher import Fetcher
from arguo.utilities.logging import get_logger
from arguo.utilities.text import normalize_whitespace, token_overlap
from arguo.utilities.urls import get_registrable_domain, normalize_url

logger = get_logger("arguo.evidence.collector")

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")
_DEFAULT_MAX_CHARS = 700
_MIN_SENTENCES = 2
_MAX_SENTENCES = 4
_PASSAGES_PER_SOURCE = 3
_DIRECT_OVERLAP_THRESHOLD = 0.12


def split_passages(text: str, max_chars: int = _DEFAULT_MAX_CHARS) -> list[str]:
    """Split text into passages of roughly 2 to 4 sentences within max_chars.

    Sentence boundaries are punctuation-based. Sentences longer than
    max_chars are hard-split so no passage exceeds the limit by much, and a
    trailing single-sentence passage is kept rather than discarded.
    """
    cleaned = normalize_whitespace(text)
    if not cleaned:
        return []
    sentences: list[str] = []
    for raw in _SENTENCE_SPLIT_RE.split(cleaned):
        raw = raw.strip()
        if not raw:
            continue
        while len(raw) > max_chars:
            sentences.append(raw[:max_chars].rstrip())
            raw = raw[max_chars:].lstrip()
        if raw:
            sentences.append(raw)
    passages: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        addition = len(sentence) + (1 if current else 0)
        if current and (
            len(current) >= _MAX_SENTENCES
            or (current_len + addition > max_chars and len(current) >= _MIN_SENTENCES)
        ):
            passages.append(" ".join(current))
            current = []
            current_len = 0
            addition = len(sentence)
        current.append(sentence)
        current_len += addition
    if current:
        passages.append(" ".join(current))
    return passages


def _passage_hash(passage: str) -> str:
    return hashlib.sha256(passage.encode("utf-8")).hexdigest()


def _independence_group(url: str) -> str | None:
    try:
        return get_registrable_domain(url)
    except ValueError:
        return None


async def collect(
    results: list[NormalizedResult],
    subquestion: SubQuestion | None,
    fetcher: Fetcher,
    ledger: EvidenceLedger,
    budget: BudgetTracker,
) -> int:
    """Fetch results, extract passages, and add evidence records to the ledger.

    Returns the number of evidence records added. Behavior:

    - The source budget is respected: when budget.record_source() reports the
      max_sources limit as exhausted, collection stops without raising.
    - Results already present in the ledger (same normalized URL) are skipped.
    - Fetch failures become ledger sources with an access_note and no
      evidence, so the report can show what could not be retrieved.
    - Up to 3 passages per source are selected by token overlap with the
      subquestion text and queries; without a subquestion the first passages
      are taken. Overlap >= 0.12 records DIRECT relevance, lower overlap
      records INDIRECT (context-level) relevance; the support relation stays
      SUPPORTS at this stage, real verification happens later.
    """
    added = 0
    known_urls = ledger.known_source_urls()
    focus_text = ""
    if subquestion is not None:
        focus_text = normalize_whitespace(
            f"{subquestion.text} {' '.join(subquestion.search_queries)}"
        )

    for result in results:
        try:
            budget.record_source()
        except BudgetExceededError:
            logger.info("collector: source budget exhausted, stopping collection")
            break

        try:
            normalized = normalize_url(result.url)
        except ValueError:
            normalized = result.url
        if normalized in known_urls:
            continue

        fetch = await fetcher.fetch(result.url)
        if fetch.error:
            ledger.add_source(
                url=result.url,
                title=result.title,
                provider=result.provider,
                published_at=result.published_at,
                snippets=[result.snippet] if result.snippet else [],
                access_note=fetch.error,
            )
            continue

        try:
            budget.record_bytes(fetch.bytes_downloaded)
        except BudgetExceededError:
            logger.info("collector: byte budget exhausted, stopping collection")
            ledger.add_source(
                url=result.url,
                title=result.title,
                final_url=fetch.final_url,
                provider=result.provider,
                published_at=result.published_at,
                retrieved_at=fetch.retrieved_at,
                content_type=fetch.content_type,
                snippets=[result.snippet] if result.snippet else [],
                access_note="byte budget exhausted before extraction",
            )
            break

        title, text = extract_from_fetch(fetch)
        source = ledger.add_source(
            url=result.url,
            final_url=fetch.final_url,
            title=title or result.title,
            published_at=result.published_at,
            retrieved_at=fetch.retrieved_at,
            content_type=fetch.content_type,
            content_hash=_passage_hash(text) if text else None,
            provider=result.provider,
            snippets=[result.snippet] if result.snippet else [],
            access_note=fetch.note,
        )
        known_urls.add(normalized)
        if not text:
            if fetch.note is None:
                source.access_note = "no extractable main text"
            continue

        passages = split_passages(text)
        if not passages:
            continue
        if focus_text:
            scored = sorted(
                passages,
                key=lambda passage: token_overlap(focus_text, passage),
                reverse=True,
            )
            selected = [p for p in scored if token_overlap(focus_text, p) > 0.0]
            if not selected:
                selected = scored[:1]
            selected = selected[:_PASSAGES_PER_SOURCE]
        else:
            selected = passages[:_PASSAGES_PER_SOURCE]

        group = _independence_group(result.url)
        for passage in selected:
            overlap = token_overlap(focus_text, passage) if focus_text else 0.0
            relevance = (
                Relevance.DIRECT if overlap >= _DIRECT_OVERLAP_THRESHOLD else Relevance.INDIRECT
            )
            ledger.add_evidence(
                source_id=source.source_id,
                source_url=result.url,
                relevant_passage=passage,
                source_title=source.title,
                published_at=result.published_at,
                retrieved_at=fetch.retrieved_at,
                supports_or_contradicts=SupportRelation.SUPPORTS,
                relevance=relevance,
                independence_group=group,
                content_hash=_passage_hash(passage),
                provenance={
                    "retrieval": "direct-fetch",
                    "provider": result.provider,
                    "subquestion_id": subquestion.subquestion_id if subquestion else None,
                    "token_overlap": round(overlap, 4),
                },
            )
            added += 1
    return added
