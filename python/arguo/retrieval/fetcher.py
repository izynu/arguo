"""HTTP retrieval with SSRF revalidation, redirect handling, and byte limits.

The fetcher is defensive by default: it never follows redirects blindly, it
caps downloaded bytes, it only accepts a small set of content types, and it
never raises out of :meth:`Fetcher.fetch`. Failures are returned as
FetchResult records with an error message so callers (and the evidence
ledger) can record exactly what happened.
"""

from __future__ import annotations

import asyncio
import re
from dataclasses import asdict, dataclass
from urllib.parse import urljoin

import httpx

from arguo.config import ResearchBudget, Settings
from arguo.exceptions import UnsafeURLError
from arguo.models import utc_now_iso
from arguo.security.url_guard import URLGuard
from arguo.storage.cache import ResponseCache
from arguo.utilities.logging import get_logger

logger = get_logger("arguo.retrieval.fetcher")

_ALLOWED_TYPES = frozenset(
    {"text/html", "application/xhtml+xml", "application/json", "text/plain", "application/pdf"}
)
_REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
_MAX_REDIRECTS = 3
_DEFAULT_PER_REQUEST_BYTE_LIMIT = 2_000_000
_CHUNK_SIZE = 65_536
_CHARSET_RE = re.compile(r"charset=([A-Za-z0-9_.:\-]+)", re.IGNORECASE)


@dataclass
class FetchResult:
    """Outcome of one fetch attempt. error carries the failure, if any."""

    page_text: str | None
    title: str | None
    content_type: str | None
    status_code: int | None
    bytes_downloaded: int
    final_url: str
    retrieved_at: str
    error: str | None = None
    note: str | None = None


class Fetcher:
    """Polite, bounded HTML/JSON/text/PDF fetcher.

    Args:
        settings: Run settings; supplies the user agent.
        guard: URLGuard used for the initial URL and every redirect hop.
        cache: Optional ResponseCache; successful GETs are stored under the
            key "fetch:{url}" and replayed on later calls within the TTL.
        budget: Optional ResearchBudget supplying per_request_timeout_s and
            max_total_bytes. Defaults to a plain ResearchBudget(). The
            Settings contract does not carry a budget, so it is passed here
            (the run orchestrator owns the profile budget).
    """

    def __init__(
        self,
        settings: Settings,
        guard: URLGuard,
        cache: ResponseCache | None = None,
        budget: ResearchBudget | None = None,
    ) -> None:
        self._settings = settings
        self._guard = guard
        self._cache = cache
        self._budget = budget if budget is not None else ResearchBudget()

    @property
    def _per_request_byte_limit(self) -> int:
        """Per-request cap: 2,000,000 bytes or the run byte budget, whichever is lower."""
        budget_cap = int(self._budget.max_total_bytes)
        return max(1, min(_DEFAULT_PER_REQUEST_BYTE_LIMIT, budget_cap))

    async def fetch(self, url: str) -> FetchResult:
        """Fetch url and return a FetchResult; this method never raises.

        Redirects are followed manually for at most 3 hops, and every hop is
        revalidated by the URL guard before the next request is made. Bytes
        are streamed up to the per-request limit; anything beyond the limit
        is dropped and recorded in note as truncated.
        """
        retrieved_at = utc_now_iso()
        cache_key = f"fetch:{url}"
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            restored = self._from_cache(cached)
            if restored is not None:
                return restored
        try:
            safe_url = await asyncio.to_thread(self._guard.assert_safe, url)
        except UnsafeURLError as exc:
            return FetchResult(
                page_text=None,
                title=None,
                content_type=None,
                status_code=None,
                bytes_downloaded=0,
                final_url=url,
                retrieved_at=retrieved_at,
                error=f"URL rejected by safety guard: {exc}",
            )
        except Exception as exc:  # Defensive: fetch must never raise.
            return FetchResult(
                page_text=None,
                title=None,
                content_type=None,
                status_code=None,
                bytes_downloaded=0,
                final_url=url,
                retrieved_at=retrieved_at,
                error=f"unexpected URL guard failure: {type(exc).__name__}: {exc}",
            )

        headers = {
            "User-Agent": self._settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,text/plain;q=0.8",
            "Accept-Language": "en",
        }
        current_url = safe_url
        limit = self._per_request_byte_limit
        try:
            async with httpx.AsyncClient(
                follow_redirects=False,
                timeout=self._budget.per_request_timeout_s,
                headers=headers,
            ) as client:
                for _hop in range(_MAX_REDIRECTS + 1):
                    async with client.stream("GET", current_url) as response:
                        status = response.status_code
                        if status in _REDIRECT_STATUSES:
                            location = response.headers.get("location")
                            if not location:
                                return FetchResult(
                                    page_text=None, title=None, content_type=None,
                                    status_code=status, bytes_downloaded=0,
                                    final_url=str(response.url), retrieved_at=retrieved_at,
                                    error=f"HTTP {status} redirect without a Location header",
                                )
                            next_url = urljoin(current_url, location)
                            await asyncio.to_thread(
                                self._guard.revalidate_redirect, current_url, next_url
                            )
                            current_url = next_url
                            continue
                        base_type = (response.headers.get("content-type") or "").split(";")[0].strip().lower()
                        if base_type not in _ALLOWED_TYPES:
                            return FetchResult(
                                page_text=None, title=None, content_type=base_type or None,
                                status_code=status, bytes_downloaded=0,
                                final_url=str(response.url), retrieved_at=retrieved_at,
                                error=f"unsupported content-type: {base_type or 'missing'}",
                            )
                        chunks: list[bytes] = []
                        total = 0
                        truncated = False
                        async for chunk in response.aiter_bytes(_CHUNK_SIZE):
                            if total + len(chunk) > limit:
                                chunks.append(chunk[: max(0, limit - total)])
                                total = limit
                                truncated = True
                                break
                            chunks.append(chunk)
                            total += len(chunk)
                        if status >= 400:
                            return FetchResult(
                                page_text=None, title=None, content_type=base_type,
                                status_code=status, bytes_downloaded=total,
                                final_url=str(response.url), retrieved_at=retrieved_at,
                                error=f"HTTP {status} response",
                            )
                        raw = b"".join(chunks)
                        note: str | None = None
                        page_text: str | None
                        if base_type == "application/pdf":
                            page_text = None
                            note = "pdf not parsed"
                        else:
                            page_text = self._decode(raw, response.headers.get("content-type") or "")
                        if truncated:
                            note = (
                                f"response truncated at {limit} byte request limit"
                                if note is None
                                else f"{note}; response truncated at {limit} byte request limit"
                            )
                        result = FetchResult(
                            page_text=page_text,
                            title=None,
                            content_type=base_type,
                            status_code=status,
                            bytes_downloaded=total,
                            final_url=str(response.url),
                            retrieved_at=retrieved_at,
                            error=None,
                            note=note,
                        )
                        if self._cache is not None:
                            self._cache.put(cache_key, asdict(result))
                        return result
                return FetchResult(
                    page_text=None, title=None, content_type=None, status_code=None,
                    bytes_downloaded=0, final_url=current_url, retrieved_at=retrieved_at,
                    error=f"too many redirects (limit {_MAX_REDIRECTS})",
                )
        except httpx.HTTPError as exc:
            return FetchResult(
                page_text=None, title=None, content_type=None, status_code=None,
                bytes_downloaded=0, final_url=current_url, retrieved_at=retrieved_at,
                error=f"fetch failed: {type(exc).__name__}: {exc}",
            )
        except OSError as exc:
            return FetchResult(
                page_text=None, title=None, content_type=None, status_code=None,
                bytes_downloaded=0, final_url=current_url, retrieved_at=retrieved_at,
                error=f"network failure: {type(exc).__name__}: {exc}",
            )
        except Exception as exc:  # Defensive: fetch must never raise.
            logger.warning("unexpected fetch failure for %s: %s", url, exc)
            return FetchResult(
                page_text=None, title=None, content_type=None, status_code=None,
                bytes_downloaded=0, final_url=current_url, retrieved_at=retrieved_at,
                error=f"unexpected fetch failure: {type(exc).__name__}: {exc}",
            )

    @staticmethod
    def _decode(raw: bytes, content_type: str) -> str:
        """Decode bytes using the declared charset or utf-8 with replacement."""
        match = _CHARSET_RE.search(content_type or "")
        encoding = match.group(1) if match else "utf-8"
        try:
            return raw.decode(encoding, errors="replace")
        except (LookupError, UnicodeError):
            return raw.decode("utf-8", errors="replace")

    @staticmethod
    def _from_cache(cached: object) -> FetchResult | None:
        """Rebuild a FetchResult from a cache entry, or None on any mismatch."""
        if not isinstance(cached, dict):
            return None
        if cached.get("error"):
            return None
        try:
            return FetchResult(
                page_text=cached.get("page_text"),
                title=cached.get("title"),
                content_type=cached.get("content_type"),
                status_code=cached.get("status_code"),
                bytes_downloaded=int(cached.get("bytes_downloaded") or 0),
                final_url=str(cached.get("final_url") or ""),
                retrieved_at=str(cached.get("retrieved_at") or utc_now_iso()),
                error=None,
                note=cached.get("note"),
            )
        except (TypeError, ValueError):
            return None
