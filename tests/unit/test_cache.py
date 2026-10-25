"""Tests for arguo.storage.cache."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from arguo.storage.cache import ResponseCache, cache_key


def make_cache(tmp_path: Path, ttl_s: int = 3600) -> ResponseCache:
    return ResponseCache(tmp_path / "cache", ttl_s=ttl_s)


def test_put_and_get_roundtrip(tmp_path: Path) -> None:
    cache = make_cache(tmp_path)
    cache.put("fetch:https://example.org", {"body": "text", "n": 3})
    assert cache.get("fetch:https://example.org") == {"body": "text", "n": 3}


def test_get_missing_key_returns_none(tmp_path: Path) -> None:
    cache = make_cache(tmp_path)
    assert cache.get("nope") is None


def test_ttl_zero_entry_is_an_expired_miss(tmp_path: Path) -> None:
    cache = make_cache(tmp_path, ttl_s=0)
    cache.put("instant-expiry", {"v": 1})
    entry_path = cache.dir / f"{cache_key('instant-expiry')}.json"
    payload = json.loads(entry_path.read_text(encoding="utf-8"))
    payload["stored_at"] = (
        datetime.now(UTC) - timedelta(seconds=1)
    ).isoformat(timespec="seconds")
    entry_path.write_text(json.dumps(payload), encoding="utf-8")
    assert cache.get("instant-expiry") is None


def test_backdated_entry_is_an_expired_miss(tmp_path: Path) -> None:
    cache = make_cache(tmp_path, ttl_s=3600)
    cache.put("old", {"v": 1})
    entry_path = cache.dir / f"{cache_key('old')}.json"
    payload = json.loads(entry_path.read_text(encoding="utf-8"))
    payload["stored_at"] = (
        datetime.now(UTC) - timedelta(hours=2)
    ).isoformat(timespec="seconds")
    entry_path.write_text(json.dumps(payload), encoding="utf-8")
    assert cache.get("old") is None


def test_corrupt_json_file_is_treated_as_a_miss(tmp_path: Path) -> None:
    cache = make_cache(tmp_path)
    cache.dir.mkdir(parents=True, exist_ok=True)
    entry_path = cache.dir / f"{cache_key('broken')}.json"
    entry_path.write_text("this is not json{", encoding="utf-8")
    assert cache.get("broken") is None


def test_clear_removes_all_entries(tmp_path: Path) -> None:
    cache = make_cache(tmp_path)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.clear() == 2
    assert cache.clear() == 0
    assert cache.get("a") is None
    assert cache.get("b") is None


def test_stats_counts_entries(tmp_path: Path) -> None:
    cache = make_cache(tmp_path)
    assert cache.stats() == {"entries": 0, "oldest": None, "newest": None}
    cache.put("a", 1)
    cache.put("b", 2)
    stats = cache.stats()
    assert stats["entries"] == 2
    assert stats["oldest"] is not None
    assert stats["newest"] is not None
    assert stats["oldest"] <= stats["newest"]


def test_cache_key_never_contains_plaintext() -> None:
    digest = cache_key("fetch:TAVILY_API_KEY=sk-example-secret-value")
    assert "sk-example-secret-value" not in digest
    assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)
