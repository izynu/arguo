# data/: catalog authoring files and policy

This directory holds the catalog authoring inputs. The built outputs live in `catalog/` at the repository root.

## Contents

| Path | What it is |
| --- | --- |
| `categories.json` | The 50 catalog category keys with display metadata |
| `schemas/resource.schema.json` | The JSON schema rule set every record must satisfy |
| `resources/*.jsonl` | 19 authoring files, one JSON record per line (1,594 raw records) |
| `resource-sources.yaml` | External import sources for `scripts/sync_resources.py`; ships with 2 example entries, both disabled |
| `source-policy.yaml` | The 7 ingestion rules: official APIs first, robots, polite rate limits, provenance, metadata only, licenses recorded or `unknown`, no fabrication |

## Authoring files and their origins

`resources/` holds three authoring tracks:

- `academic-1.jsonl`, `academic-2.jsonl`, `academic-3.jsonl`: academic search, bibliographic metadata, biomedical literature, preprints, journals, patents, and dataset registries
- `general-1a.jsonl`, `general-1b.jsonl`, `general-2.jsonl`, `general-3a.jsonl`, `general-3b.jsonl`: general reference, archives, journalism, software registries, security advisories, and cross-cutting discovery tools
- `gov-1.jsonl`, `gov-2.jsonl`, `gov-3.jsonl`: government statistics, law and regulation, economics, elections, procurement, and international organizations

Provenance: the tracks were authored by parallel catalog agents. Two segments, `general-1a` and `general-3a`, were authored directly by the project orchestrator after their assigned agents timed out repeatedly. That history is recorded in `worklog.md` (Task 0b).

## Rebuilding the merged catalog

```bash
python3 scripts/build_resource_catalog.py
```

The build reads every `resources/*.jsonl` file, validates each record, drops cross-file duplicates (first record wins, by id and by canonical URL), and writes:

- `catalog/catalog.json` and `catalog/catalog.jsonl`: the merged catalog
- `catalog/stats.json`: category, region, type, access, language, and API counts
- a dedupe audit trail printed to the build output

## Current counts

- 1,594 raw records across the 19 authoring files
- 24 cross-file duplicates dropped during the build, each with a printed audit line
- 1,570 unique records in the merged catalog, covering all 50 categories and 82 regions

Known authoring-file state: `scripts/validate_resources.py` reports 2 cross-file duplicate ids and 24 duplicate canonical URLs across the authoring files. These are warnings by default because the build dedupes them; `--strict` treats them as errors. A future data cleanup should use `--strict` as its gate.

## Verification status: documented vs verified

Every record carries `verification_status`. The two honest levels are:

- `documented`: the canonical URL and metadata were recorded from the resource's own documentation. 820 merged records currently have this status, and 150 are `verified` from the 2026-10-25 live check.
- `verified`: the URL was actually live-checked and behaved as documented. No record currently holds this status; `scripts/check_links.py --live --max N` is the polite, rate-capped tool for that work.

Do not set `verified` on a record you have not live-checked.
