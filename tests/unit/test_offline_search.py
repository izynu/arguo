"""Tests for arguo.search.offline: fixtures only, never network."""

from __future__ import annotations

import asyncio

from arguo.search.offline import OfflineSearchProvider


def search(provider: OfflineSearchProvider, query: str, max_results: int):
    return asyncio.run(provider.search(query, max_results))


def test_caller_fixture_dict_returns_matching_results() -> None:
    provider = OfflineSearchProvider(
        {
            "refugee": [
                {
                    "title": "Example fixture: displacement overview",
                    "url": "https://example.org/refugee-data",
                    "snippet": "Fixture content about refugee statistics.",
                    "published_at": "2024-06-01",
                }
            ]
        }
    )
    results = search(provider, "refugee population", 5)
    assert len(results) == 1
    assert results[0].url == "https://example.org/refugee-data"
    assert results[0].provider == "offline-fixture"
    assert results[0].published_at == "2024-06-01"


def test_fixture_key_matches_by_token_set() -> None:
    provider = OfflineSearchProvider(
        {"urban heat": [{"title": "Example fixture: heat", "url": "https://example.gov/heat"}]}
    )
    results = search(provider, "How is urban heat measured?", 5)
    assert results and results[0].url == "https://example.gov/heat"


def test_default_provider_returns_example_fixture_results() -> None:
    provider = OfflineSearchProvider()
    results = search(provider, "refugee population", 5)
    assert len(results) >= 1
    for result in results:
        assert result.url.startswith("https://example.")
        assert "Example fixture" in (result.title or "")


def test_raw_metadata_note_mentions_fixture() -> None:
    provider = OfflineSearchProvider(
        {"refugee": [{"title": "Example fixture: note check", "url": "https://example.org/note"}]}
    )
    results = search(provider, "refugee population", 5)
    note = results[0].raw_metadata.get("note", "")
    assert "fixture" in note


def test_unmatched_query_returns_builtin_defaults() -> None:
    provider = OfflineSearchProvider({"zzz": []})
    results = search(provider, "something unrelated entirely", 6)
    assert len(results) == 6
    assert all(r.title and r.title.startswith("Example fixture result") for r in results)
    assert all(
        r.raw_metadata.get("note", "").startswith("fixture data: no fixture matched")
        for r in results
    )


def test_max_results_is_respected() -> None:
    provider = OfflineSearchProvider(
        {
            "tree": [
                {"title": f"Example fixture {i}", "url": f"https://example.org/{i}"}
                for i in range(5)
            ]
        }
    )
    results = search(provider, "tree", 2)
    assert len(results) == 2


def test_fixture_origin_reporting() -> None:
    assert OfflineSearchProvider({}).fixture_origin == "caller-supplied"
    # In the repository checkout the fixture file exists; in a stripped
    # install it may be absent, in which case built-in defaults are used.
    origin = OfflineSearchProvider().fixture_origin
    assert origin in {"tests/fixtures/offline_search.json", "built-in defaults"}
