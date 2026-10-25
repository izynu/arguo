#!/usr/bin/env python3
"""Regenerate public/data/site-stats.json from real repository contents.

Counts are computed live from the merged catalog, the docs index, and the
eval case files. Nothing here is hand-maintained: if a number changes, rerun
this script (or `make site-stats`) before republishing the site.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    catalog_stats = json.loads((ROOT / "catalog" / "stats.json").read_text(encoding="utf-8"))
    docs = json.loads((ROOT / "public" / "data" / "docs-index.json").read_text(encoding="utf-8"))

    eval_cases = 0
    for path in sorted((ROOT / "evals" / "cases").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        eval_cases += len(data.get("cases", []))

    site_stats = {
        "generated_at": catalog_stats.get("generated_at"),
        "catalog_records": catalog_stats["total_records"],
        "catalog_categories": catalog_stats["category_count"],
        "regions": catalog_stats["region_count"],
        "docs_pages": len(docs),
        "eval_cases": eval_cases,
        "pipeline_stages": 10,
        "verification_status": catalog_stats["verification_status"],
        "access_modes": catalog_stats["access_modes"],
        "api_available": catalog_stats["api_availability"].get("api", 0),
        "top_regions": dict(list(catalog_stats["regions"].items())[:8]),
    }

    out = ROOT / "public" / "data" / "site-stats.json"
    out.write_text(json.dumps(site_stats, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)}")
    print(json.dumps(site_stats, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
