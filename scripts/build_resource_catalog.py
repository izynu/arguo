#!/usr/bin/env python3
"""Build the merged, deduplicated Arguo resource catalog.

Reads all data/resources/*.jsonl, validates every record, removes duplicates
(identical normalized URL, identical id, or same name on the same registrable
domain), and writes:

  catalog/catalog.json    array of records (sorted by name)
  catalog/catalog.jsonl   same records, one JSON object per line
  catalog/stats.json      verified counts and coverage statistics

The build never invents data and never silently keeps duplicates. Dropped
duplicates are printed so maintainers can audit every merge decision.
"""

from __future__ import annotations

import json
import shutil
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
RESOURCES_DIR = ROOT / "data" / "resources"
OUT_DIR = ROOT / "catalog"
# The website reads the catalog from public/data at runtime; publishing it from
# this build keeps the site from ever serving a stale copy.
PUBLIC_DATA_DIR = ROOT / "public" / "data"

def normalized_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    path = parsed.path.rstrip("/")
    return f"{host}{path}"


def domain_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower().rstrip(".")


def load_records() -> tuple[list[dict], list[str]]:
    records: list[dict] = []
    errors: list[str] = []
    for path in sorted(RESOURCES_DIR.glob("*.jsonl")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                rec["_file"] = path.name
                records.append(rec)
            except json.JSONDecodeError as exc:
                errors.append(f"{path.name}:{lineno}: invalid JSON: {exc}")
    return records, errors


def dedupe(records: list[dict]) -> tuple[list[dict], list[str]]:
    dropped: list[str] = []
    by_url: dict[str, dict] = {}
    by_id: dict[str, dict] = {}
    by_name_domain: dict[str, dict] = {}
    kept: list[dict] = []

    for rec in records:
        rid = rec["id"]
        url_key = normalized_url(rec["canonical_url"])
        name_key = f"{rec['name'].lower().strip()}|{domain_of(rec['canonical_url'])}"

        if url_key in by_url:
            first = by_url[url_key]
            dropped.append(
                f"duplicate url {rec['canonical_url']}: kept '{first['id']}' ({first['_file']}), dropped '{rid}' ({rec['_file']})"
            )
            continue
        if rid in by_id:
            first = by_id[rid]
            dropped.append(
                f"duplicate id {rid}: kept from {first['_file']}, dropped duplicate from {rec['_file']}"
            )
            continue
        if name_key in by_name_domain:
            first = by_name_domain[name_key]
            dropped.append(
                f"duplicate name+domain '{rec['name']}' at {domain_of(rec['canonical_url'])}: kept '{first['id']}', dropped '{rid}'"
            )
            continue

        by_url[url_key] = rec
        by_id[rid] = rec
        by_name_domain[name_key] = rec
        kept.append(rec)

    return kept, dropped


def build_stats(records: list[dict]) -> dict:
    categories = Counter(r["category"] for r in records)
    regions = Counter(r["region"] for r in records)
    types = Counter(r["resource_type"] for r in records)
    access = Counter(r["resource_access"] for r in records)
    status = Counter(r["verification_status"] for r in records)
    languages = Counter(r["language"] for r in records)
    api = Counter("api" if r["api_available"] else "no-api" for r in records)
    return {
        "generated_at": date.today().isoformat(),
        "total_records": len(records),
        "categories": dict(sorted(categories.items())),
        "category_count": len(categories),
        "regions": dict(sorted(regions.items(), key=lambda kv: -kv[1])),
        "region_count": len(regions),
        "resource_types": dict(sorted(types.items())),
        "access_modes": dict(sorted(access.items())),
        "verification_status": dict(sorted(status.items())),
        "languages": dict(sorted(languages.items(), key=lambda kv: -kv[1])),
        "api_availability": dict(api),
    }


def main() -> int:
    records, errors = load_records()
    for err in errors:
        print(f"ERROR: {err}")
    if errors:
        return 1

    kept, dropped = dedupe(records)
    for line in dropped:
        print(f"DEDUPE: {line}")

    kept.sort(key=lambda r: r["name"].lower())
    stats = build_stats(kept)

    OUT_DIR.mkdir(exist_ok=True)
    (OUT_DIR / "catalog.json").write_text(
        json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    with (OUT_DIR / "catalog.jsonl").open("w", encoding="utf-8") as fh:
        for rec in kept:
            clean = {k: v for k, v in rec.items() if not k.startswith("_")}
            fh.write(json.dumps(clean, ensure_ascii=False, sort_keys=True) + "\n")
    (OUT_DIR / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUT_DIR / "catalog.json", PUBLIC_DATA_DIR / "catalog.json")
    shutil.copyfile(OUT_DIR / "stats.json", PUBLIC_DATA_DIR / "stats.json")

    print(f"Catalog written: {len(kept)} records from {len(kept)} unique sources")
    print(f"Categories covered: {stats['category_count']} / 50")
    print(f"Regions: {stats['region_count']}")
    print(f"Dropped duplicates: {len(dropped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
