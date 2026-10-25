"""Offline fixture search provider for demos, tests, and air-gapped runs.

Fixture results are clearly labelled so that an offline run can never be
mistaken for live research: built-in defaults use example.org, example.edu,
and example.gov placeholder URLs only, and titles always start with
"Example fixture result".
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from arguo.models import NormalizedResult
from arguo.providers.base import SearchProvider
from arguo.utilities.logging import get_logger

logger = get_logger("arguo.search.offline")

_FIXTURE_PATH = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "offline_search.json"

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _default_fixture_results() -> list[dict[str, Any]]:
    """Build-in fallback: six clearly labelled placeholder results."""
    return [
        {
            "title": "Example fixture result 1",
            "url": "https://example.org/evidence-based-research",
            "snippet": "Fixture content describing evidence based research workflows for offline demonstration runs.",
            "published_at": None,
        },
        {
            "title": "Example fixture result 2",
            "url": "https://example.edu/methods/evidence-based-research",
            "snippet": "Fixture content outlining how evidence based research questions are decomposed into subquestions.",
            "published_at": None,
        },
        {
            "title": "Example fixture result 3",
            "url": "https://example.gov/data/evidence-based-research",
            "snippet": "Fixture content with placeholder statistics used to exercise numeric provenance handling.",
            "published_at": None,
        },
        {
            "title": "Example fixture result 4",
            "url": "https://example.org/standards/citation-auditing",
            "snippet": "Fixture content describing citation auditing checks such as unsupported claims and duplicate sources.",
            "published_at": None,
        },
        {
            "title": "Example fixture result 5",
            "url": "https://example.edu/evaluation/source-quality",
            "snippet": "Fixture content describing a transparent source quality rubric covering authority and recency.",
            "published_at": None,
        },
        {
            "title": "Example fixture result 6",
            "url": "https://example.gov/reports/contradictions",
            "snippet": "Fixture content with two placeholder passages that disagree, used to test contradiction handling.",
            "published_at": None,
        },
    ]


class OfflineSearchProvider(SearchProvider):
    """SearchProvider that returns deterministic fixture data, never network.

    Args:
        fixtures: Mapping of lowercase query substrings to lists of result
            dicts with keys title, url, snippet, published_at. When None, the
            provider loads tests/fixtures/offline_search.json if that file
            exists; otherwise it uses the built-in default fixture set.
    """

    def __init__(self, fixtures: dict[str, list[dict]] | None = None) -> None:
        if fixtures is not None:
            self._fixtures: dict[str, list[dict]] = {
                str(key).lower(): list(items) for key, items in fixtures.items()
            }
            self._fixture_origin = "caller-supplied"
        else:
            loaded = self._load_fixture_file(_FIXTURE_PATH)
            if loaded is not None:
                self._fixtures = loaded
                self._fixture_origin = "tests/fixtures/offline_search.json"
            else:
                self._fixtures = {}
                self._fixture_origin = "built-in defaults"

    @staticmethod
    def _load_fixture_file(path: Path) -> dict[str, list[dict]] | None:
        """Load the fixture JSON file, returning None when absent or broken."""
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if not isinstance(raw, dict):
            return None
        fixtures: dict[str, list[dict]] = {}
        for key, items in raw.items():
            if isinstance(items, list):
                fixtures[str(key).lower()] = [item for item in items if isinstance(item, dict)]
        return fixtures

    @property
    def name(self) -> str:
        return "offline-fixture"

    @property
    def fixture_origin(self) -> str:
        """Where the fixture data came from: caller, file, or built-in."""
        return self._fixture_origin

    def _match_key(self, key: str, query_lower: str, query_tokens: set[str]) -> bool:
        """Substring or full token-set match between a fixture key and query."""
        if key in query_lower:
            return True
        key_tokens = set(_TOKEN_RE.findall(key))
        if not key_tokens:
            return False
        return key_tokens.issubset(query_tokens)

    async def search(self, query: str, max_results: int) -> list[NormalizedResult]:
        """Return fixture results matching the query tokens, or the defaults."""
        query_lower = (query or "").lower()
        query_tokens = set(_TOKEN_RE.findall(query_lower))
        matched_items: list[dict] | None = None
        note: str
        for key, items in self._fixtures.items():
            if self._match_key(key, query_lower, query_tokens):
                matched_items = items
                note = (
                    f"fixture data: matched fixture key '{key}' from {self._fixture_origin}"
                )
                break
        if matched_items is None:
            matched_items = _default_fixture_results()
            note = (
                "fixture data: no fixture matched the query, "
                "returning built-in default results"
            )
            logger.info("OfflineSearchProvider returned built-in defaults for: %s", query[:80])
        results: list[NormalizedResult] = []
        for item in matched_items:
            url = item.get("url")
            if not isinstance(url, str) or not url:
                continue
            title = item.get("title")
            snippet = item.get("snippet")
            published_at = item.get("published_at")
            results.append(
                NormalizedResult(
                    title=title if isinstance(title, str) else None,
                    url=url,
                    snippet=snippet if isinstance(snippet, str) else None,
                    published_at=published_at if isinstance(published_at, str) else None,
                    score=None,
                    provider=self.name,
                    raw_metadata={"note": note},
                )
            )
            if len(results) >= max(1, int(max_results)):
                break
        return results
