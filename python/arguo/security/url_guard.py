"""SSRF protection and URL safety enforcement.

The guard is the single checkpoint every retrieved URL must pass before any
network activity happens. It enforces an http/https scheme allowlist, rejects
embedded credentials, and resolves every host so that private, loopback,
link-local, and otherwise reserved IP ranges can be blocked before a request
is made. DNS results are cached per guard instance for the duration of a run.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from arguo.exceptions import UnsafeURLError
from arguo.utilities.logging import get_logger

logger = get_logger("arguo.security.url_guard")

_ALLOWED_SCHEMES = ("http", "https")
_DEFAULT_PORTS = (80, 443)


class URLGuard:
    """Validate URLs against scheme, credential, and network-location rules.

    Construction performs no network activity. DNS lookups happen lazily on
    the first :meth:`assert_safe` call for a host and are cached for the
    lifetime of the instance (one research run).

    Args:
        allow_private: Test-only escape hatch that skips IP-range checks.
            Production code must never enable it; with it off, the guard
            blocks SSRF targets such as cloud metadata endpoints.

    Raises:
        UnsafeURLError: For every rejected URL, with a message naming the
            exact rule that failed.
    """

    def __init__(self, allow_private: bool = False) -> None:
        self._allow_private = allow_private
        self._dns_cache: dict[str, tuple[str, ...]] = {}

    @property
    def allow_private(self) -> bool:
        """Whether private network targets are (unsafely) permitted."""
        return self._allow_private

    def assert_safe(self, url: str) -> str:
        """Return the URL unchanged after verifying it is safe to request.

        Checks performed, in order: scheme allowlist (http/https only, so
        file:, ftp:, data: and friends are rejected), credentials in the
        authority (user:pass@host), host presence, port sanity (any port is
        allowed but non-default ports are logged), and, unless allow_private
        is set, resolution of the host with rejection of private, loopback,
        link-local, unspecified, multicast, and reserved addresses.
        """
        if not isinstance(url, str) or not url.strip():
            raise UnsafeURLError("URL must be a non-empty string")
        candidate = url.strip()
        parsed = urlparse(candidate)

        scheme = parsed.scheme.lower()
        if scheme not in _ALLOWED_SCHEMES:
            raise UnsafeURLError(
                f"unsafe scheme '{parsed.scheme or 'missing'}' in URL: "
                "only http and https are allowed"
            )

        netloc = parsed.netloc or ""
        if parsed.username or parsed.password or "@" in netloc:
            raise UnsafeURLError(
                "credentials in URL are not allowed (user:pass@host form)"
            )

        host = (parsed.hostname or "").lower().rstrip(".")
        if not host:
            raise UnsafeURLError(f"URL has no host: '{candidate}'")

        try:
            port = parsed.port
        except ValueError as exc:
            raise UnsafeURLError(f"invalid port in URL: '{candidate}'") from exc
        if port is not None and port not in _DEFAULT_PORTS:
            # Any port is permitted, but unusual ports are worth a log line.
            logger.warning("URLGuard: allowing non-default port %d for host %s", port, host)

        if not self._allow_private:
            self._assert_ips_safe(host)
        return candidate

    def revalidate_redirect(self, original: str, next_url: str) -> str:
        """Validate a redirect destination before following it.

        Applies the same rules as :meth:`assert_safe` to ``next_url`` and
        additionally resolves the destination host so its IP addresses are
        checked. If the destination host cannot be resolved at all the call
        fails closed: a redirect to a host that cannot be resolved would fail
        the fetch anyway, and skipping the IP check would create a bypass.

        Args:
            original: The URL that produced the redirect (kept for interface
                clarity and future referer-style checks; not interpreted).
            next_url: The redirect destination. Must already be absolute.

        Returns:
            The validated destination URL.

        Raises:
            UnsafeURLError: When the destination is unsafe, unresolvable, or
                points at a blocked address range. Messages start with
                "redirect to blocked host" or name the specific failure.
        """
        del original  # Reserved for future use; see docstring.
        if not isinstance(next_url, str) or not next_url.strip():
            raise UnsafeURLError("redirect target must be a non-empty string")
        target = next_url.strip()
        if not urlparse(target).scheme:
            raise UnsafeURLError(f"redirect target has no scheme: '{target}'")
        try:
            return self.assert_safe(target)
        except UnsafeURLError as exc:
            raise UnsafeURLError(f"redirect to blocked host or unsafe target: {exc}") from exc

    def _assert_ips_safe(self, host: str) -> None:
        """Resolve host and raise UnsafeURLError if any address is blocked."""
        for ip_str in self._resolve_ips(host):
            ip = ipaddress.ip_address(ip_str)
            reason: str | None = None
            if ip.is_unspecified:
                reason = "unspecified address (0.0.0.0 or ::)"
            elif ip.is_loopback:
                reason = "loopback address"
            elif ip.is_link_local:
                reason = "link-local address"
            elif ip.is_multicast:
                reason = "multicast address"
            elif ip.is_reserved:
                reason = "reserved address"
            elif ip.is_private:
                reason = "private address"
            if reason is not None:
                raise UnsafeURLError(
                    f"{reason} blocked for host '{host}': {ip_str} "
                    "(private address blocked by SSRF guard)"
                )

    def _resolve_ips(self, host: str) -> tuple[str, ...]:
        """Return all resolved IPs for host, using the per-run DNS cache."""
        if host in self._dns_cache:
            return self._dns_cache[host]
        try:
            ipaddress.ip_address(host)
            literal = True
        except ValueError:
            literal = False
        if literal:
            ips: tuple[str, ...] = (host,)
        else:
            try:
                infos = socket.getaddrinfo(host, None)
            except (socket.gaierror, OSError, UnicodeError) as exc:
                raise UnsafeURLError(
                    f"could not resolve host '{host}': {exc}"
                ) from exc
            ips = tuple(dict.fromkeys(str(info[4][0]) for info in infos))
            if not ips:
                raise UnsafeURLError(f"host '{host}' resolved to no addresses")
        self._dns_cache[host] = ips
        return ips
