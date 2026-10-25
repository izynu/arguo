"""Text helpers used by extraction, verification, and reporting."""

from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_whitespace(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text or "").strip()


def truncate_chars(text: str, max_chars: int, suffix: str = "...") -> str:
    text = text or ""
    if len(text) <= max_chars:
        return text
    if max_chars <= len(suffix):
        return text[:max_chars]
    return text[: max_chars - len(suffix)].rstrip() + suffix


def tokens(text: str) -> list[str]:
    return _WORD_RE.findall((text or "").lower())


def token_overlap(claim: str, passage: str) -> float:
    """Jaccard overlap between claim and passage tokens.

    Used by the offline heuristic support check. This is a rough signal for
    tests and demo mode only; real support review uses the model adapter.
    """
    claim_tokens = set(tokens(claim))
    passage_tokens = set(tokens(passage))
    if not claim_tokens:
        return 0.0
    if not passage_tokens:
        return 0.0
    intersection = claim_tokens & passage_tokens
    union = claim_tokens | passage_tokens
    return len(intersection) / len(union) if union else 0.0


_NEGATIONS = {"not", "no", "never", "cannot", "cant", "wont", "didnt", "isnt", "arent"}


def has_negation_conflict(claim: str, passage: str) -> bool:
    """Cheap heuristic: claim and passage disagree on negation of a shared term.

    Deliberately conservative: returns False unless a shared content word is
    negated in exactly one of the two texts.
    """
    claim_t = tokens(claim)
    passage_t = tokens(passage)
    claim_neg = set()
    for i, word in enumerate(claim_t):
        if word in _NEGATIONS and i + 1 < len(claim_t):
            claim_neg.add(claim_t[i + 1])
    passage_neg = set()
    for i, word in enumerate(passage_t):
        if word in _NEGATIONS and i + 1 < len(passage_t):
            passage_neg.add(passage_t[i + 1])
    claim_content = set(claim_t) - _NEGATIONS
    passage_content = set(passage_t) - _NEGATIONS
    shared = claim_content & passage_content
    for word in shared:
        if (word in claim_neg) != (word in passage_neg):
            return True
    return False
