"""Tests for arguo.security.url_guard.

Negative cases use literal IP addresses so that no DNS lookup (and therefore
no network activity) happens. Positive public-host cases monkeypatch the
resolver with a public address so the suite stays fully offline. Async
behavior is exercised with plain asyncio.run instead of a pytest plugin.
"""

from __future__ import annotations

import asyncio
import socket

import pytest

from arguo.exceptions import UnsafeURLError
from arguo.security.url_guard import URLGuard


def _fake_getaddrinfo(host, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]


def test_assert_safe_returns_the_url_for_a_public_host(monkeypatch) -> None:
    monkeypatch.setattr(socket, "getaddrinfo", _fake_getaddrinfo)
    guard = URLGuard()
    assert guard.assert_safe("https://example.com") == "https://example.com"


def test_assert_safe_still_works_inside_a_running_event_loop() -> None:
    guard = URLGuard(allow_private=True)

    async def check() -> str:
        return guard.assert_safe("https://example.com/page")

    assert asyncio.run(check()) == "https://example.com/page"


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.org/file",
        "data:text/html,hello",
        "javascript:alert(1)",
    ],
)
def test_guard_rejects_disallowed_schemes(url: str) -> None:
    with pytest.raises(UnsafeURLError):
        URLGuard().assert_safe(url)


def test_loopback_with_non_default_port_is_rejected_with_reason() -> None:
    with pytest.raises(UnsafeURLError) as excinfo:
        URLGuard().assert_safe("http://127.0.0.1:8080/x")
    message = str(excinfo.value)
    assert "loopback" in message or "private" in message


def test_link_local_metadata_endpoint_is_rejected() -> None:
    with pytest.raises(UnsafeURLError):
        URLGuard().assert_safe("http://169.254.169.254/latest/meta-data")


def test_ftp_scheme_is_rejected() -> None:
    with pytest.raises(UnsafeURLError):
        URLGuard().assert_safe("ftp://example.com/file")


def test_guard_rejects_embedded_credentials() -> None:
    with pytest.raises(UnsafeURLError, match="credentials"):
        URLGuard().assert_safe("https://user:pass@example.com/x")


@pytest.mark.parametrize(
    "url",
    [
        "http://10.1.2.3/x",
        "http://192.168.0.9/x",
        "http://0.0.0.0/",
        "http://[::1]/x",
    ],
)
def test_guard_blocks_other_reserved_literal_targets(url: str) -> None:
    with pytest.raises(UnsafeURLError):
        URLGuard().assert_safe(url)


def test_guard_rejects_empty_urls() -> None:
    with pytest.raises(UnsafeURLError):
        URLGuard().assert_safe("   ")


def test_allow_private_allows_localhost_for_tests() -> None:
    guard = URLGuard(allow_private=True)
    assert guard.allow_private is True
    assert guard.assert_safe("http://127.0.0.1:8080/x") == "http://127.0.0.1:8080/x"


def test_revalidate_redirect_rejects_blocked_target() -> None:
    guard = URLGuard()
    with pytest.raises(UnsafeURLError, match="redirect"):
        guard.revalidate_redirect(
            "https://example.org/start", "http://192.168.0.10/admin"
        )
    with pytest.raises(UnsafeURLError, match="redirect"):
        guard.revalidate_redirect("https://example.org/start", "ftp://example.org/x")
