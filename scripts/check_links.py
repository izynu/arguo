#!/usr/bin/env python3
"""Check canonical URLs in the resource catalog. Offline by default.

Offline mode (default) uses the standard library only and is purely
syntactic. Every canonical_url must parse as an absolute URL, use https,
have a host that contains a dot, and contain no spaces. Obvious
placeholder hosts (example.com, example.org, example.net, and friends)
are flagged as "placeholder" issues with "info" severity because
legitimate fixtures use them. Suspicious hosts such as common TLD typos
(".cm" for ".com") and doubled TLDs ("com.com") are flagged with
"warning" severity. The catalog files are never modified in any mode.

Results are written to catalog/link-check-report.json:

  {"generated_at": ..., "checked": N,
   "issues": [{"id", "url", "kind", "severity", "detail"}, ...]}

Live mode (--live) is opt-in and performs real requests with httpx: HEAD
first with a GET fallback on 405, concurrency 4, a 10 second timeout, and
a 0.5 second pause per request. Each requested URL is recorded as
{"url", "status", "classification", "checked_at"}; 5xx responses,
timeouts, and connection errors are classified "transient", 4xx
responses "permanent", and everything below 400 "ok". Live runs request
at most --max URLs (default 200) to stay polite. Offline mode has no cap
because it never touches the network.

Usage:
    python3 scripts/check_links.py [--live] [--max N] [--catalog PATH] [--report PATH]

Exit codes: 0 on success (including offline runs that report issues); 1
when the catalog is missing or unreadable or the report cannot be written.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import httpx
except ModuleNotFoundError:  # offline mode uses the standard library only
    httpx = None

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = ROOT / "catalog" / "catalog.json"
DEFAULT_REPORT = ROOT / "catalog" / "link-check-report.json"

PLACEHOLDER_HOSTS = {
    "example.com", "example.org", "example.net", "example.edu",
    "example.gov", "example.int", "example.io", "example.dev",
}
DOUBLE_TLD_RE = re.compile(
    r"\.(com|org|net|gov|edu)\.(com|org|net|gov|edu)$", re.IGNORECASE
)
REPEATED_PORT_RE = re.compile(r":\d+:\d+")

LIVE_CONCURRENCY = 4
LIVE_TIMEOUT_S = 10.0
LIVE_PAUSE_S = 0.5
DEFAULT_MAX_URLS = 200

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def load_catalog(path: Path) -> list[dict]:
    if not path.is_file():
        print(f"Error: resource catalog not found at {path}", file=sys.stderr)
        print(
            "Hint: build it first with: python3 scripts/build_resource_catalog.py",
            file=sys.stderr,
        )
        raise SystemExit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"Error: catalog unreadable: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not isinstance(data, list):
        print("Error: catalog must be a JSON array of records.", file=sys.stderr)
        raise SystemExit(1)
    return [record for record in data if isinstance(record, dict)]


def static_issue(record: dict) -> dict | None:
    """Return one issue dict for the first rule the URL breaks, or None."""
    url = str(record.get("canonical_url", ""))
    rid = str(record.get("id", "?"))
    parsed = urlparse(url)
    if not url.startswith("https://"):
        return {
            "id": rid, "url": url, "kind": "not-https", "severity": SEVERITY_ERROR,
            "detail": "canonical_url must use the https scheme",
        }
    if " " in url:
        return {
            "id": rid, "url": url, "kind": "invalid-url", "severity": SEVERITY_ERROR,
            "detail": "canonical_url contains spaces",
        }
    host = (parsed.hostname or "").lower().rstrip(".")
    if not host:
        return {
            "id": rid, "url": url, "kind": "invalid-url", "severity": SEVERITY_ERROR,
            "detail": "canonical_url does not parse as an absolute URL with a host",
        }
    if "." not in host:
        return {
            "id": rid, "url": url, "kind": "invalid-host", "severity": SEVERITY_ERROR,
            "detail": f"host '{host}' must contain a dot",
        }
    if REPEATED_PORT_RE.search(parsed.netloc):
        return {
            "id": rid, "url": url, "kind": "repeated-port", "severity": SEVERITY_ERROR,
            "detail": f"authority '{parsed.netloc}' contains a repeated port",
        }
    if host in PLACEHOLDER_HOSTS:
        return {
            "id": rid, "url": url, "kind": "placeholder", "severity": SEVERITY_INFO,
            "detail": (
                f"placeholder host '{host}' (severity info because legitimate "
                "fixtures use these domains)"
            ),
        }
    if host.endswith(".cm") or DOUBLE_TLD_RE.search(host):
        return {
            "id": rid, "url": url, "kind": "suspicious-domain",
            "severity": SEVERITY_WARNING,
            "detail": f"host '{host}' looks like a TLD typo or doubled TLD",
        }
    return None


def check_offline(records: list[dict]) -> tuple[int, list[dict]]:
    issues: list[dict] = []
    checked = 0
    for record in records:
        if not str(record.get("canonical_url", "")).strip():
            issues.append({
                "id": str(record.get("id", "?")), "url": "", "kind": "missing-url",
                "severity": SEVERITY_ERROR,
                "detail": "record has no canonical_url field",
            })
            continue
        checked += 1
        issue = static_issue(record)
        if issue is not None:
            issues.append(issue)
    return checked, issues


async def check_live_url(
    client: httpx.AsyncClient, rid: str, url: str, semaphore: asyncio.Semaphore
) -> dict:
    """Request one URL and return a result record; never raises."""
    if httpx is None:  # pragma: no cover - only reachable without httpx installed
        return {
            "id": rid, "url": url, "method": "none", "status": None,
            "classification": "skipped", "error": "httpx is not installed",
            "checked_at": utc_now_iso(),
        }
    async with semaphore:
        await asyncio.sleep(LIVE_PAUSE_S)
        started = time.monotonic()
        result: dict = {
            "id": rid, "url": url, "method": "HEAD", "status": None,
            "classification": "transient", "error": None, "checked_at": utc_now_iso(),
        }
        try:
            response = await client.head(url)
            if response.status_code == 405:
                result["method"] = "GET"
                response = await client.get(url)
            result["status"] = response.status_code
            if response.status_code < 400:
                result["classification"] = "ok"
            elif response.status_code < 500:
                result["classification"] = "permanent"
            else:
                result["classification"] = "transient"
        except httpx.TimeoutException as exc:
            result["error"] = f"timeout: {type(exc).__name__}"
        except (httpx.HTTPError, OSError) as exc:
            result["error"] = f"network error: {type(exc).__name__}: {exc}"
        result["elapsed_ms"] = int((time.monotonic() - started) * 1000)
        return result


async def check_live(records: list[dict], max_urls: int) -> dict:
    """Request catalog URLs live, subject to the politeness cap."""
    if httpx is None:
        print("live mode requires httpx: install it with pip install httpx")
        raise SystemExit(1)

    issues: list[dict] = []
    eligible: list[tuple[str, str]] = []
    for record in records:
        issue = static_issue(record)
        if issue is not None:
            issues.append(issue)
        url = str(record.get("canonical_url", ""))
        if url.startswith("https://") and " " not in url and (urlparse(url).hostname or ""):
            eligible.append((str(record.get("id", "?")), url))
    requested = eligible[:max_urls]
    semaphore = asyncio.Semaphore(LIVE_CONCURRENCY)
    headers = {"User-Agent": "Arguo-link-check/0.1 (+https://github.com/izynu/arguo)"}
    async with httpx.AsyncClient(
        timeout=LIVE_TIMEOUT_S, follow_redirects=True, headers=headers
    ) as client:
        results = list(await asyncio.gather(
            *(check_live_url(client, rid, url, semaphore) for rid, url in requested)
        ))
    return {
        "checked": len(requested),
        "issues": issues,
        "results": results,
        "eligible": len(eligible),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check resource catalog links.")
    parser.add_argument("--live", action="store_true",
                        help="Perform real network checks (default is offline syntax checks).")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX_URLS, metavar="N",
                        help="Live mode: request at most N URLs per run (default 200).")
    parser.add_argument("--catalog", default=str(DEFAULT_CATALOG), help="Catalog JSON path.")
    parser.add_argument("--report", default=str(DEFAULT_REPORT), help="Report JSON path.")
    args = parser.parse_args(argv)
    if args.max < 1:
        parser.error("--max must be at least 1")

    catalog_path = Path(args.catalog)
    report_path = Path(args.report)
    try:
        records = load_catalog(catalog_path)
        if args.live:
            live = asyncio.run(check_live(records, args.max))
            checked = live["checked"]
            issues = live["issues"]
            results = live["results"]
            eligible = live["eligible"]
        else:
            checked, issues = check_offline(records)
            results = []
            eligible = checked
    except SystemExit as exc:
        return int(exc.code or 0)
    except (OSError, ValueError) as exc:
        print(f"Error: link check failed internally: {exc}", file=sys.stderr)
        return 1

    report: dict = {
        "generated_at": utc_now_iso(),
        "checked": checked,
        "issues": issues,
        "mode": "live" if args.live else "offline",
    }
    if args.live:
        report["results"] = results
        report["max_urls"] = args.max
        report["eligible_urls"] = eligible
    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except OSError as exc:
        print(f"Error: could not write report: {exc}", file=sys.stderr)
        return 1

    print(f"Checked {checked} URL(s) in {'live' if args.live else 'offline'} mode.")
    if args.live and eligible > checked:
        print(
            f"Politeness cap: requested {checked} of {eligible} eligible URL(s) "
            f"(--max {args.max}). Re-run with a higher --max to check the rest."
        )
    if issues:
        print(f"Issues: {len(issues)}")
        for issue in issues[:20]:
            print(f"  [{issue['severity']}] {issue['kind']} {issue['id']}: {issue['url']}")
        if len(issues) > 20:
            print(f"  ... and {len(issues) - 20} more")
    else:
        print("Issues: 0")
    if args.live:
        ok = sum(1 for r in results if r["classification"] == "ok")
        transient = sum(1 for r in results if r["classification"] == "transient")
        permanent = sum(1 for r in results if r["classification"] == "permanent")
        print(
            f"Live results: {ok} ok, {transient} transient, {permanent} permanent. "
            "No catalog files were modified."
        )
    else:
        print("No catalog files were modified.")
    print(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
