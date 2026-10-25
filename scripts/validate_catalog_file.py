#!/usr/bin/env python3
"""Validate one JSONL catalog file against data/schemas/resource.schema.json.

Usage: python3 scripts/validate_catalog_file.py data/resources/<file>.jsonl

Checks schema conformance (via a lightweight built-in mirror of the JSON
Schema rules), duplicate ids and urls, style rules (no em dashes, en dashes,
or emoji), and prints per-category counts. Exit code 0 on success.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "id", "name", "canonical_url", "category", "description", "best_for",
    "resource_type", "publisher", "region", "language", "resource_access",
    "api_available", "official_source", "license", "date_added",
    "verification_status", "provenance", "tags",
]

RESOURCE_TYPES = {
    "database", "portal", "api", "archive", "repository", "library",
    "search-engine", "tool", "documentation", "dataset-registry",
    "journal", "registry", "standard", "preprint-server", "agency",
    "organization", "program",
}

ACCESS_MODES = {"open", "free-registration", "partial-open", "paid", "mixed"}
STATUSES = {"verified", "documented", "community-submitted", "deprecated"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,79}$")
URL_RE = re.compile(r"^https://\S+$")
DASH_RE = re.compile(r"[\u2014\u2013]")
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F000-\U0001F02F"
    "\U00002600-\U000026FF\U0001F900-\U0001F9FF\U00002B00-\U00002BFF]"
)


def load_categories() -> set[str]:
    data = json.loads((ROOT / "data" / "categories.json").read_text(encoding="utf-8"))
    return {c["key"] for c in data["categories"]}


def validate_file(path: Path) -> tuple[int, Counter, list[str]]:
    categories = load_categories()
    errors: list[str] = []
    ids: dict[str, int] = {}
    urls: dict[str, int] = {}
    cat_counts: Counter = Counter()
    count = 0

    text = path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        where = f"line {lineno}"
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{where}: invalid JSON ({exc})")
            continue
        count += 1
        for field in REQUIRED:
            if field not in rec:
                errors.append(f"{where}: missing required field '{field}'")
        unexpected = set(rec) - set(REQUIRED) - {"subcategory", "documentation_url", "attribution_requirements", "access_requirements", "last_checked", "status_notes"}
        if unexpected:
            errors.append(f"{where}: unexpected fields {sorted(unexpected)}")
        rid = rec.get("id", "")
        if not ID_RE.match(rid):
            errors.append(f"{where}: bad id '{rid}'")
        elif rid in ids:
            errors.append(f"{where}: duplicate id '{rid}' (first at line {ids[rid]})")
        else:
            ids[rid] = lineno
        url = rec.get("canonical_url", "")
        if not URL_RE.match(url):
            errors.append(f"{where}: canonical_url must be an https URL, got '{url}'")
        elif url.rstrip("/") in {u.rstrip("/") for u in urls}:
            errors.append(f"{where}: duplicate canonical_url '{url}'")
        else:
            urls[url] = lineno
        if rec.get("category") not in categories:
            errors.append(f"{where}: unknown category '{rec.get('category')}'")
        desc = rec.get("description", "")
        if not (40 <= len(desc) <= 320):
            errors.append(f"{where}: description length {len(desc)} outside 40-320")
        for field in ("name", "description", "publisher"):
            value = str(rec.get(field, ""))
            if DASH_RE.search(value) or EMOJI_RE.search(value):
                errors.append(f"{where}: em dash, en dash, or emoji in '{field}'")
        if rec.get("resource_type") not in RESOURCE_TYPES:
            errors.append(f"{where}: bad resource_type '{rec.get('resource_type')}'")
        if rec.get("resource_access") not in ACCESS_MODES:
            errors.append(f"{where}: bad resource_access '{rec.get('resource_access')}'")
        if rec.get("verification_status") not in STATUSES:
            errors.append(f"{where}: bad verification_status '{rec.get('verification_status')}'")
        best_for = rec.get("best_for")
        if not isinstance(best_for, list) or not (1 <= len(best_for) <= 4):
            errors.append(f"{where}: best_for must be a list of 1-4 items")
        tags = rec.get("tags")
        if not isinstance(tags, list) or not (1 <= len(tags) <= 8):
            errors.append(f"{where}: tags must be a list of 1-8 items")
        prov = rec.get("provenance")
        if not isinstance(prov, dict) or "source" not in prov:
            errors.append(f"{where}: provenance must be an object with a 'source' key")
        if rec.get("verification_status") == "verified" and not rec.get("last_checked"):
            errors.append(f"{where}: 'verified' records need last_checked")
        cat_counts[rec.get("category", "?")] += 1

    return count, cat_counts, errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 2
    count, cat_counts, errors = validate_file(path)
    print(f"File: {path}")
    print(f"Records: {count}")
    print("Category counts:")
    for cat in sorted(cat_counts):
        print(f"  {cat}: {cat_counts[cat]}")
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for err in errors[:40]:
            print(f"  {err}")
        if len(errors) > 40:
            print(f"  ... and {len(errors) - 40} more")
        return 1
    print("PASS: schema, uniqueness, and style checks OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
