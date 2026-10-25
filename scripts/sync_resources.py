#!/usr/bin/env python3
"""Sync resource records from the enabled sources in data/resource-sources.yaml.

Behavior:

- Reads data/resource-sources.yaml with a minimal built-in parser (no YAML
  dependency is added). Only sources with "enabled: true" are fetched.
- Fetches each enabled source with httpx.get (15 second timeout, user agent
  "EvidenceLedger/0.1 sync") and validates every line as a resource record
  using the same rules as scripts/validate_catalog_file.py, plus a
  cross-check against the ids and urls already present in data/resources/.
- Writes data/resources/imported-{name}.jsonl only when that source fully
  passes validation. Existing files are never deleted or truncated: on any
  failure the previous state of the repository is preserved.
- Writes catalog/last-sync.json with {"started_at", "finished_at",
  "sources": [{"name", "status", "records"}]}.

With nothing enabled the run is a clean no-op: it prints "No sources
enabled; nothing to sync.", writes the summary with an empty source list,
and exits 0. Exit code 1 means at least one enabled source failed; the
report says which.

Usage: python3 scripts/sync_resources.py [--sources PATH] [--summary PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCES = ROOT / "data" / "resource-sources.yaml"
DEFAULT_SUMMARY = ROOT / "catalog" / "last-sync.json"
RESOURCES_DIR = ROOT / "data" / "resources"
SCRIPTS_DIR = ROOT / "scripts"
FETCH_TIMEOUT_S = 15.0

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import validate_catalog_file  # noqa: E402


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def parse_scalar(value: str) -> str | bool:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def parse_sources_yaml(path: Path) -> list[dict]:
    """Parse the minimal YAML subset used by resource-sources.yaml.

    Supports one top-level "sources:" key whose value is a list of flat
    mappings introduced by "- " items. Comments and blank lines are ignored.
    Raises ValueError on obviously malformed structure.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"could not read {path}: {exc}") from exc
    sources: list[dict] = []
    current: dict | None = None
    in_sources = False
    for lineno, raw in enumerate(text.splitlines(), 1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw.startswith(" ") and not raw.startswith("-"):
            key, _, rest = stripped.partition(":")
            if key.strip() == "sources":
                in_sources = True
                continue
            in_sources = False
            if rest.strip():
                continue
            continue
        if not in_sources:
            continue
        if stripped.startswith("- "):
            current = {}
            sources.append(current)
            stripped = stripped[2:].strip()
            if not stripped:
                continue
        if current is None:
            raise ValueError(f"line {lineno}: list item outside 'sources:'")
        if ":" not in stripped:
            raise ValueError(f"line {lineno}: expected 'key: value', got '{stripped}'")
        key, _, value = stripped.partition(":")
        current[key.strip()] = parse_scalar(value)
    return sources


def existing_keys() -> tuple[set[str], set[str]]:
    """Collect ids and normalized urls from every JSONL file in data/resources."""
    ids: set[str] = set()
    urls: set[str] = set()
    if not RESOURCES_DIR.is_dir():
        return ids, urls
    for path in RESOURCES_DIR.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                if record.get("id"):
                    ids.add(str(record["id"]))
                url = str(record.get("canonical_url", ""))
                if url:
                    parsed = urlparse(url)
                    urls.add(
                        f"{(parsed.hostname or '').lower().rstrip('.')}"
                        f"{parsed.path.rstrip('/')}"
                    )
    return ids, urls


def sanitize_name(name: str) -> str:
    cleaned = re.sub(r"[^a-z0-9-]+", "-", str(name).lower()).strip("-")
    return cleaned or "source"


def fetch_source_text(source: dict) -> str:
    import httpx

    url = str(source.get("url", ""))
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"source url must be http(s), got '{url}'")
    response = httpx.get(
        url,
        timeout=FETCH_TIMEOUT_S,
        follow_redirects=True,
        headers={"User-Agent": "EvidenceLedger/0.1 sync"},
    )
    response.raise_for_status()
    return response.text


def process_source(source: dict) -> tuple[str, int, list[str]]:
    """Fetch, validate, and stage one source. Returns (status, records, errors)."""
    name = str(source.get("name", "?"))
    try:
        text = fetch_source_text(source)
    except Exception as exc:  # noqa: BLE001 - every failure mode is reported
        return f"failed: fetch error ({type(exc).__name__}: {exc})", 0, []

    if not text.strip():
        return "failed: source returned an empty document", 0, []

    with tempfile.TemporaryDirectory() as tmp_dir:
        staged = Path(tmp_dir) / "staged.jsonl"
        staged.write_text(text, encoding="utf-8")
        count, _categories, errors = validate_catalog_file.validate_file(staged)

    if errors:
        preview = "; ".join(errors[:5])
        return (
            f"failed: {len(errors)} validation error(s) in {count} record(s): {preview}",
            0,
            errors,
        )

    known_ids, known_urls = existing_keys()
    collisions: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        rid = str(record.get("id", ""))
        url = str(record.get("canonical_url", ""))
        parsed = urlparse(url)
        url_key = (
            f"{(parsed.hostname or '').lower().rstrip('.')}{parsed.path.rstrip('/')}"
        )
        if rid and rid in known_ids:
            collisions.append(f"id '{rid}' already exists in data/resources")
        if url_key and url_key in known_urls:
            collisions.append(f"url '{url}' already exists in data/resources")
    if collisions:
        preview = "; ".join(collisions[:5])
        return (
            f"failed: {len(collisions)} collision(s) with existing records: {preview}",
            0,
            collisions,
        )

    target = RESOURCES_DIR / f"imported-{sanitize_name(name)}.jsonl"
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    return f"ok: wrote {target.name}", count, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync enabled resource sources.")
    parser.add_argument("--sources", default=str(DEFAULT_SOURCES))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    args = parser.parse_args(argv)

    started_at = utc_now_iso()
    sources_path = Path(args.sources)
    summary_path = Path(args.summary)

    try:
        sources = parse_sources_yaml(sources_path)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    enabled = [s for s in sources if s.get("enabled") is True]
    print(f"Loaded {len(sources)} source(s), {len(enabled)} enabled.")
    if not enabled:
        print("No sources enabled; nothing to sync.")

    results: list[dict] = []
    failures = 0
    for source in enabled:
        name = str(source.get("name", "?"))
        status, records, errors = process_source(source)
        if status.startswith("failed"):
            failures += 1
            print(f"  {name}: {status}", file=sys.stderr)
            for error in errors[5:10]:
                print(f"    {error}", file=sys.stderr)
        else:
            print(f"  {name}: {status}")
        results.append({"name": name, "status": status, "records": records})

    finished_at = utc_now_iso()
    summary = {
        "started_at": started_at,
        "finished_at": finished_at,
        "sources": results,
    }
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    except OSError as exc:
        print(f"Error: could not write summary: {exc}", file=sys.stderr)
        return 1

    if failures:
        print(
            f"Sync finished with {failures} failed source(s). No existing files "
            f"were modified. Summary: {summary_path}"
        )
        return 1
    print(
        f"Sync finished cleanly: {len(results)} source(s) processed. "
        f"Summary: {summary_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
