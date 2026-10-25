"""Tests for arguo.utilities.urls."""

from __future__ import annotations

import pytest

from arguo.utilities.urls import (
    get_registrable_domain,
    is_probably_same_url,
    normalize_url,
    safe_display_url,
)


def test_normalize_url_lowercases_host_and_strips_tracking_params() -> None:
    normalized = normalize_url("HTTPS://Example.ORG/path?utm_source=tw&id=5")
    assert normalized == "https://example.org/path?id=5"


def test_normalize_url_keeps_meaningful_query() -> None:
    assert (
        normalize_url("https://example.org/search?q=tree&page=2")
        == "https://example.org/search?q=tree&page=2"
    )
    # A plus in the query is treated as an encoded space and re-encoded.
    assert (
        normalize_url("https://example.org/search?q=tree+cover")
        == "https://example.org/search?q=tree%20cover"
    )


def test_normalize_url_removes_default_port_keeps_custom_port() -> None:
    assert normalize_url("https://example.org:443/a") == "https://example.org/a"
    assert normalize_url("http://example.org:8080/a") == "http://example.org:8080/a"


@pytest.mark.parametrize("bad", ["ftp://example.org", "file:///etc/passwd", "https:///only-path", ""])
def test_normalize_url_raises_on_non_http_schemes_and_garbage(bad: str) -> None:
    with pytest.raises(ValueError):
        normalize_url(bad)


def test_registrable_domain_handles_co_uk_style_suffixes() -> None:
    assert get_registrable_domain("https://www.nature.co.uk/x") == "nature.co.uk"
    assert get_registrable_domain("https://a.b.example.gov.uk/y") == "example.gov.uk"
    assert get_registrable_domain("https://example.org") == "example.org"


def test_is_probably_same_url_true_cases() -> None:
    assert is_probably_same_url("https://example.org/a#x", "https://example.org/a")
    assert is_probably_same_url(
        "https://example.org/a?utm_source=tw", "https://example.org/a"
    )
    assert is_probably_same_url("https://Example.ORG/a", "https://example.org/a")


def test_is_probably_same_url_false_cases() -> None:
    assert not is_probably_same_url("https://example.org/a", "https://example.org/b")
    assert not is_probably_same_url("https://example.org/a", "https://example.net/a")


def test_safe_display_url_drops_query_and_truncates() -> None:
    display = safe_display_url("https://example.org/a/b?q=1", max_len=100)
    assert display == "https://example.org/a/b"
    long = safe_display_url("https://example.org/" + "x" * 200, max_len=30)
    assert len(long) <= 30
