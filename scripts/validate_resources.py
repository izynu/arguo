#!/usr/bin/env python3
"""Validate every resource JSONL file in data/resources/.

Per-file checks are imported from scripts/validate_catalog_file.py so
this script and the single-file validator can never drift apart. On top
of them this script checks cross-file uniqueness of ids and
canonical_urls, and verifies that data/schemas/resource.schema.json
exists, parses as JSON, and carries a "$schema" key, "type": "object",
and a non-empty "required" list.

Cross-file duplicates: files in data/resources/ are authoring inputs and
the shipped catalog is deduplicated by scripts/build_resource_catalog.py
with a printed audit trail, so cross-file duplicate ids and urls are
reported as warnings by default. Pass --strict to treat them as errors,
for example before a release cut or a data cleanup.

Usage: python3 scripts/validate_resources.py [--strict]
Exit codes: 0 when every check passes, 1 when any error was found.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))

from validate_catalog_file import load_categories, validate_file  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
RESOURCES_DIR = ROOT / "data" / "resources"
SCHEMA_PATH = ROOT / "data" / "schemas" / "resource.schema.json"


def normalized_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower().rstrip(".")
    return f"{host}{parsed.path.rstrip('/')}"


def check_schema_document() -> list[str]:
    """Verify resource.schema.json exists, parses, and has the core keys."""
    errors: list[str] = []
    if not SCHEMA_PATH.is_file():
        return [f"schema file missing: {SCHEMA_PATH}"]
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"schema file is not readable JSON: {exc}"]
    if not isinstance(schema, dict):
        return ["schema root must be a JSON object"]
    if not schema.get("$schema"):
        errors.append('schema is missing "$schema"')
    if schema.get("type") != "object":
        errors.append('schema "type" must be "object"')
    required = schema.get("required")
    if not isinstance(required, list) or not required:
        errors.append('schema "required" must be a non-empty list')
    return errors


def cross_file_duplicates(paths: list[Path]) -> tuple[list[str], list[str]]:
    """Find ids and normalized urls that appear in more than one file."""
    id_owner: dict[str, str] = {}
    url_owner: dict[str, str] = {}
    dup_ids: list[str] = []
    dup_urls: list[str] = []
    for path in paths:
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue  # per-file validation already reported this
            if not isinstance(record, dict):
                continue
            rid = str(record.get("id", ""))
            url = str(record.get("canonical_url", ""))
            if rid:
                owner = id_owner.get(rid)
                if owner is not None and owner != path.name:
                    dup_ids.append(f"id '{rid}' in {owner} and {path.name}:{lineno}")
                else:
                    id_owner.setdefault(rid, path.name)
            if url:
                key = normalized_url(url)
                owner = url_owner.get(key)
                if owner is not None and owner != path.name:
                    dup_urls.append(f"url '{url}' in {owner} and {path.name}:{lineno}")
                else:
                    url_owner.setdefault(key, path.name)
    return dup_ids, dup_urls


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate all resource JSONL files.")
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat cross-file duplicate ids and urls as errors instead of warnings.",
    )
    args = parser.parse_args(argv)

    if not RESOURCES_DIR.is_dir():
        print(f"Error: resources directory not found: {RESOURCES_DIR}", file=sys.stderr)
        return 1
    paths = sorted(RESOURCES_DIR.glob("*.jsonl"))
    if not paths:
        print("Error: no JSONL files found in data/resources/.", file=sys.stderr)
        return 1

    defined_categories = load_categories()

    failed = False
    rows: list[tuple[str, int, int, str]] = []
    error_details: list[str] = []
    total_records = 0
    total_errors = 0
    found_categories: set[str] = set()

    for path in paths:
        count, cat_counts, errors = validate_file(path)
        total_records += count
        total_errors += len(errors)
        found_categories.update(cat_counts)
        status = "PASS" if not errors else "FAIL"
        rows.append((path.name, count, len(errors), status))
        if errors:
            failed = True
            for error in errors[:10]:
                error_details.append(f"{path.name}: {error}")
            if len(errors) > 10:
                error_details.append(f"{path.name}: ... and {len(errors) - 10} more")

    name_width = max(len("File"), *(len(row[0]) for row in rows))
    print("Summary table:")
    print(f"  {'File':<{name_width}}  {'Records':>7}  {'Errors':>6}  Status")
    for name, count, n_errors, status in rows:
        print(f"  {name:<{name_width}}  {count:>7}  {n_errors:>6}  {status}")

    if error_details:
        print("")
        print("Per-file error details (first 10 per file):")
        for detail in error_details[:40]:
            print(f"  {detail}")
        if len(error_details) > 40:
            print(f"  ... and {len(error_details) - 40} more")

    dup_ids, dup_urls = cross_file_duplicates(paths)
    cross_errors = 0
    if dup_ids or dup_urls:
        label = "ERROR" if args.strict else "WARN"
        print("")
        print(
            f"Cross-file duplicates: {len(dup_ids)} id(s), {len(dup_urls)} url(s) "
            f"reported as {label}"
            + (
                ""
                if args.strict
                else " (the build deduplicates these with an audit trail)"
            )
        )
        for line in (dup_ids + dup_urls)[:20]:
            print(f"  {label}: {line}")
        if len(dup_ids) + len(dup_urls) > 20:
            print(f"  ... and {len(dup_ids) + len(dup_urls) - 20} more")
        if args.strict:
            cross_errors = len(dup_ids) + len(dup_urls)

    schema_errors = check_schema_document()
    print("")
    print(
        "Schema document (data/schemas/resource.schema.json): "
        + ("FAIL" if schema_errors else "PASS")
    )
    for error in schema_errors:
        print(f"  SCHEMA ERROR: {error}")

    print("")
    print("Overall counts:")
    print(f"  Files: {len(paths)}")
    print(f"  Records: {total_records}")
    print(f"  Per-file errors: {total_errors}")
    print(f"  Cross-file duplicate ids: {len(dup_ids)}")
    print(f"  Cross-file duplicate urls: {len(dup_urls)}")
    print(
        f"  Categories covered: {len(found_categories)} of "
        f"{len(defined_categories)} defined"
    )

    if failed or schema_errors or cross_errors:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
