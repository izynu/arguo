"""URL normalization and deduplication helpers.

Goals: stable canonical forms for duplicate detection, and honest preservation
of query strings that carry content (unlike tracking parameters, which are
stripped as known noise).
"""

from __future__ import annotations

import re
from urllib.parse import ParseResult, parse_qsl, quote, unquote, urlparse, urlunparse

_TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "mc_cid", "mc_eid", "ref", "ref_src", "igshid",
    "yclid", "_ga", "si",
}

_DEFAULT_PORTS = {"http": 80, "https": 443}


def normalize_url(url: str, *, keep_fragment: bool = False) -> str:
    """Return a canonical form of url for comparison and storage.

    Lowercases scheme and host, removes default ports and tracking params,
    percent-encodes spaces, and drops empty fragments.
    """
    if not url or not isinstance(url, str):
        raise ValueError("url must be a non-empty string")
    url = unquote(url).strip().replace(" ", "%20")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported scheme in url: {url!r}")
    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        raise ValueError(f"url missing host: {url!r}")
    port = parsed.port
    if port is not None and _DEFAULT_PORTS.get(scheme) != port:
        netloc = f"{host}:{port}"
    else:
        netloc = host
    if parsed.username:
        netloc = f"{parsed.username}@{netloc}" if not parsed.password else f"{parsed.username}:{parsed.password}@{netloc}"
    path = parsed.path or "/"
    path = re.sub(r"//+", "/", path)
    kept_query: list[tuple[str, str]] = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.lower() not in _TRACKING_PARAMS:
            kept_query.append((key, value))
    query = "&".join(f"{quote(k)}={quote(v)}" for k, v in kept_query)
    fragment = parsed.fragment if keep_fragment else ""
    return urlunparse((scheme, netloc, path, "", query, fragment))


_IDN_PREFIX = "xn--"


def _eTLD_like_suffix(host: str) -> str:
    """Approximate registrable domain without a public-suffix list dependency.

    Handles common two-level suffixes (co.uk, com.au, org.in, gov.cn and
    similar). Good enough for corroboration grouping; documented limitation.
    """
    parts = host.split(".")
    if len(parts) <= 2:
        return host
    two_level = ".".join(parts[-2:])
    two_level_tlds = {
        "co.uk", "org.uk", "ac.uk", "gov.uk", "co.jp", "or.jp", "ne.jp", "ac.jp",
        "com.au", "org.au", "net.au", "edu.au", "gov.au", "co.in", "org.in",
        "net.in", "gov.in", "ac.in", "com.cn", "org.cn", "gov.cn", "edu.cn",
        "com.br", "org.br", "gov.br", "com.mx", "org.mx", "gob.mx", "co.za",
        "org.za", "gov.za", "co.nz", "org.nz", "govt.nz", "com.sg", "org.sg",
        "gov.sg", "com.hk", "org.hk", "gov.hk", "co.kr", "or.kr", "go.kr",
        "com.tr", "org.tr", "gov.tr", "com.ru", "org.ru", "gov.ru", "co.id",
        "or.id", "go.id", "com.my", "org.my", "gov.my", "com.ph", "org.ph",
        "com.vn", "org.vn", "gov.vn", "com.ar", "org.ar", "gob.ar", "com.co",
        "org.co", "gov.co", "com.ng", "org.ng", "gov.ng", "com.eg", "org.eg",
        "gov.eg", "com.pk", "org.pk", "gov.pk", "com.bd", "org.bd", "gov.bd",
        "com.th", "or.th", "go.th", "edu.tw", "org.tw", "gov.tw", "com.tw",
        "com.ua", "org.ua", "gov.ua", "com.pl", "org.pl", "gov.pl", "com.es",
        "org.es", "gob.es", "com.it", "org.it", "gov.it", "gouv.fr",
    }
    if two_level in two_level_tlds and len(parts) >= 3:
        return ".".join(parts[-3:])
    return two_level


def get_registrable_domain(url: str) -> str:
    host = urlparse(normalize_url(url)).hostname or ""
    if host.startswith(_IDN_PREFIX) or "." not in host:
        return host
    return _eTLD_like_suffix(host)


def is_probably_same_url(a: str, b: str) -> bool:
    """True when two URLs normalize to the same canonical address."""
    try:
        return normalize_url(a) == normalize_url(b)
    except ValueError:
        return a.strip().rstrip("/") == b.strip().rstrip("/")


def safe_display_url(url: str, max_len: int = 100) -> str:
    parsed: ParseResult = urlparse(url)
    return (f"{parsed.scheme}://{parsed.netloc}{parsed.path}"[:max_len]).rstrip("/")
