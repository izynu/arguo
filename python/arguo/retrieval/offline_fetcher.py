"""Offline fetcher: builds FetchResult records from fixture search results.

In offline mode the pipeline must never touch the network. This class
mirrors the Fetcher interface but returns the fixture snippet as plain text,
clearly labeled, so collectors and extractors work unchanged and every
record stays honestly marked as fixture content.
"""

from __future__ import annotations

from arguo.models import NormalizedResult, utc_now_iso
from arguo.retrieval.fetcher import FetchResult
from arguo.utilities.logging import get_logger
from arguo.utilities.text import normalize_whitespace
from arguo.utilities.urls import normalize_url

logger = get_logger("arguo.retrieval.offline_fetcher")

_OFFLINE_NOTE = "offline fixture content: no network fetch performed"


class OfflineFetcher:
    """Fetcher-shaped provider that serves fixture content only."""

    def __init__(self, results: list[NormalizedResult]) -> None:
        self._results: dict[str, NormalizedResult] = {}
        for result in results or []:
            try:
                key = normalize_url(result.url)
            except ValueError:
                key = result.url
            self._results[key] = result

    @property
    def name(self) -> str:
        return "offline-fixture"

    def _lookup(self, url: str) -> NormalizedResult | None:
        try:
            key = normalize_url(url)
        except ValueError:
            key = url
        return self._results.get(key)

    async def fetch(self, url: str) -> FetchResult:
        """Return fixture content for url; never performs network activity.

        Unknown URLs produce a FetchResult with an error, mirroring the
        Fetcher contract that fetch never raises.
        """
        retrieved_at = utc_now_iso()
        result = self._lookup(url)
        if result is None:
            return FetchResult(
                page_text=None,
                title=None,
                content_type=None,
                status_code=None,
                bytes_downloaded=0,
                final_url=url,
                retrieved_at=retrieved_at,
                error="offline fixture has no content for this URL",
            )
        parts = []
        if result.title:
            parts.append(result.title)
        if result.snippet:
            parts.append(result.snippet)
        body = normalize_whitespace(". ".join(parts))
        if body and not body.endswith("."):
            body += "."
        return FetchResult(
            page_text=body or None,
            title=None,
            content_type="text/plain",
            status_code=200,
            bytes_downloaded=len(body.encode("utf-8")) if body else 0,
            final_url=url,
            retrieved_at=retrieved_at,
            error=None,
            note=_OFFLINE_NOTE,
        )
