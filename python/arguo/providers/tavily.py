"""Tavily search provider mapped onto the provider-neutral NormalizedResult.

Construction performs no network activity: the HTTP client is created inside
the async search call, so adapters are safe to build at startup and use under
asyncio.run. The API key is never included in log output or exceptions.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from arguo.exceptions import ProviderError, RateLimitError
from arguo.models import NormalizedResult
from arguo.providers.base import SearchProvider
from arguo.utilities.logging import REGISTRY, get_logger

logger = get_logger("arguo.providers.tavily")

_TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_BACKOFF_BASE_S = 0.5
_BACKOFF_CAP_S = 4.0


def _backoff_delay_s(attempt: int) -> float:
    """Exponential backoff: 0.5s, 1s, 2s, capped at 4s."""
    return min(_BACKOFF_BASE_S * (2 ** attempt), _BACKOFF_CAP_S)


def _parse_tavily_item(item: dict) -> NormalizedResult:
    """Map one Tavily result object into a NormalizedResult.

    Tolerant by design: any missing or mistyped field becomes None rather
    than raising, because dropping a whole result over one missing optional
    field would hide evidence. The url degrades to an empty string, which
    downstream URL validation filters out.
    """
    title = item.get("title")
    url = item.get("url")
    snippet = item.get("content")
    published_at = item.get("published_date")
    score = item.get("score")
    return NormalizedResult(
        title=title if isinstance(title, str) else None,
        url=url if isinstance(url, str) else "",
        snippet=snippet if isinstance(snippet, str) else None,
        published_at=published_at if isinstance(published_at, str) else None,
        score=float(score) if isinstance(score, (int, float)) else None,
        provider="tavily",
        raw_metadata={},
    )


class TavilySearchProvider(SearchProvider):
    """SearchProvider backed by the Tavily REST search API.

    Retries HTTP 429 and 5xx responses plus transport errors with exponential
    backoff (0.5s, 1s, capped at 4s). After retries are exhausted, 429 maps to
    RateLimitError and everything else to ProviderError with the HTTP status
    in the message.
    """

    def __init__(self, api_key: str, timeout_s: float = 15.0, max_retries: int = 2) -> None:
        self._api_key = api_key
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        REGISTRY.register(api_key)

    @property
    def name(self) -> str:
        return "tavily"

    async def search(self, query: str, max_results: int) -> list[NormalizedResult]:
        """Run one Tavily basic-depth search and return normalized results."""
        if not query or not query.strip():
            raise ProviderError("Tavily search requires a non-empty query.")
        payload: dict[str, Any] = {
            "api_key": self._api_key,
            "query": query,
            "max_results": max(int(max_results), 0),
            "search_depth": "basic",
        }
        async with httpx.AsyncClient(timeout=self._timeout_s) as client:
            response = await self._post_with_retry(client, payload)
        try:
            body = response.json()
            raw_results = body["results"]
        except (ValueError, KeyError, TypeError) as exc:
            raise ProviderError(
                f"Tavily returned an unexpected response shape: {exc}"
            ) from exc
        if not isinstance(raw_results, list):
            raise ProviderError("Tavily response field 'results' is not a list.")
        parsed: list[NormalizedResult] = []
        for item in raw_results:
            if isinstance(item, dict):
                parsed.append(_parse_tavily_item(item))
        return parsed

    async def _post_with_retry(self, client: httpx.AsyncClient, payload: dict) -> httpx.Response:
        """POST the search payload, retrying 429/5xx and transport errors."""
        last_status: int | None = None
        last_text: str | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await client.post(_TAVILY_SEARCH_URL, json=payload)
            except httpx.HTTPError as exc:
                if attempt < self._max_retries:
                    logger.warning("Tavily transport error, retrying: %s", exc)
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise ProviderError(
                    f"Tavily request failed after {self._max_retries + 1} attempts: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
            if response.status_code == 429:
                last_status = response.status_code
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise RateLimitError(
                    f"Tavily rate limited the request (HTTP 429) after "
                    f"{self._max_retries + 1} attempts.",
                    hint="Retry later or reduce max_search_rounds in the profile.",
                )
            if response.status_code >= 500:
                last_status = response.status_code
                last_text = response.text[:200]
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise ProviderError(
                    f"Tavily server error (HTTP {last_status}) after "
                    f"{self._max_retries + 1} attempts: {last_text}"
                )
            if not response.is_success:
                raise ProviderError(
                    f"Tavily request failed with HTTP {response.status_code}: "
                    f"{response.text[:200]}",
                    hint="Check TAVILY_API_KEY and the request payload.",
                )
            return response
        raise ProviderError(
            f"Tavily request did not complete (last HTTP status: {last_status})."
        )
