"""Provider-neutral deduplication of search results.

Deduplication is deliberately conservative: exact URL duplicates are always
collapsed, and near-duplicates are collapsed only when both the title and the
registrable domain match. Syndication across different domains is handled
later by corroboration analysis, not here.
"""

from __future__ import annotations

from arguo.models import NormalizedResult
from arguo.utilities.urls import get_registrable_domain, normalize_url


def _normalized_title_key(title: str | None) -> str | None:
    if not title or not title.strip():
        return None
    return title.strip()


def _registrable_domain_or_none(url: str) -> str | None:
    try:
        return get_registrable_domain(url)
    except ValueError:
        return None


def dedupe_results(results: list[NormalizedResult]) -> list[NormalizedResult]:
    """Drop invalid, duplicate, and near-duplicate results, preserving order.

    Rules, applied per result in input order:

    - Results whose URL fails normalization or validation are skipped.
    - Exact duplicates (same normalized URL) are dropped, keeping the first.
    - Near-duplicates (identical title AND identical registrable domain) are
      dropped, keeping the first.

    Returns the kept results in their original relative order.
    """
    kept: list[NormalizedResult] = []
    seen_urls: set[str] = set()
    seen_title_domains: set[tuple[str, str]] = set()

    for result in results:
        try:
            normalized = normalize_url(result.url)
        except ValueError:
            continue
        if normalized in seen_urls:
            continue
        domain = _registrable_domain_or_none(normalized)
        title_key = _normalized_title_key(result.title)
        near_key = (title_key, domain) if title_key and domain else None
        if near_key is not None and near_key in seen_title_domains:
            continue
        seen_urls.add(normalized)
        if near_key is not None:
            seen_title_domains.add(near_key)
        kept.append(result)
    return kept
