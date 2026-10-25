"""Tests for arguo.search.dedupe."""

from __future__ import annotations

from arguo.models import NormalizedResult
from arguo.search.dedupe import dedupe_results


def make(url: str, title: str | None = None) -> NormalizedResult:
    return NormalizedResult(
        title=title, url=url, snippet=None, provider="offline-fixture"
    )


def test_identical_urls_with_utm_param_collapse_to_one() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/a?utm_source=news", "Tracked"),
            make("https://example.org/a", "Clean"),
        ]
    )
    assert len(kept) == 1
    assert kept[0].url == "https://example.org/a?utm_source=news"


def test_exact_url_duplicates_keep_first() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/a", "First"),
            make("HTTPS://EXAMPLE.ORG/a", "Second"),
        ]
    )
    assert [r.title for r in kept] == ["First"]


def test_same_title_same_domain_collapse() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/one", "Same Title"),
            make("https://example.org/two", "Same Title"),
        ]
    )
    assert len(kept) == 1


def test_same_title_different_domain_is_kept() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/one", "Same Title"),
            make("https://example.net/one", "Same Title"),
        ]
    )
    assert len(kept) == 2


def test_different_url_same_domain_different_title_kept() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/one", "Title One"),
            make("https://example.org/two", "Title Two"),
        ]
    )
    assert len(kept) == 2


def test_invalid_urls_are_dropped() -> None:
    kept = dedupe_results([make("ftp://example.org/x"), make("https://example.org/ok")])
    assert [r.url for r in kept] == ["https://example.org/ok"]


def test_order_is_preserved() -> None:
    kept = dedupe_results(
        [
            make("https://example.org/c", "C"),
            make("https://example.org/a", "A"),
            make("https://example.org/c", "C dup"),
        ]
    )
    assert [r.title for r in kept] == ["C", "A"]
