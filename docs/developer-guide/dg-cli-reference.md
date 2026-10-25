---
title: CLI Reference
description: Every arguo command, option, default, and exit code, taken from the Typer application in cli.py.
group: developer-guide
slug: dg-cli-reference
order: 2
---

The console script is arguo (pyproject [project.scripts] points it at arguo.cli:app). The app is Typer based, named arguo, and shows help when invoked without arguments. Errors print "Error: ..." to stderr and exit with the matching EvidenceLedgerError exit code.

## Commands

research QUESTION. Runs the full pipeline. Options: --profile TEXT (default standard, one of academic, deep, quick, standard), --since [%Y-%m-%d], --until [%Y-%m-%d], --max-sources INT (min 1, capped by the profile limit), --offline (fixture providers, no network, default off), --output-dir TEXT (directory for run artifacts), --json (print the run manifest as JSON to stdout). Human output lists run id, profile, per-stage status and duration, counters, warnings, and the artifacts directory.

resources search QUERY. Case-insensitive substring match over name, description, and tags in catalog/catalog.json. Options: --category TEXT (filter by category key), --limit INT (default 20, min 1). Prints the match count and id, name, category, and URL per record.

resources list. Lists catalog records. Options: --category TEXT, --limit INT (default 50, min 1). Prints "(more records omitted, raise --limit to see them)" when truncated.

resources validate FILE. Validates one resource JSONL file, or every file in data/resources when the argument is omitted, using scripts/validate_catalog_file.py imported at run time. Prints per-file PASS or FAIL, up to 10 errors each. Exits 1 if any file fails or no files are found.

resources stats. Prints record, category, top region, and verification status counts from catalog/stats.json when present, otherwise computed from catalog.json.

config check. Resolves Settings from the environment and prints which values are set as booleans, never secret values, plus the output and cache directories and whether tests/fixtures/offline_search.json is present.

doctor. Installation checks: Python 3.11 or newer, settings load, TAVILY_API_KEY presence, model endpoint configuration, cache directory writability, catalog presence, offline fixture readiness. --ping also GETs https://example.org with a 5 second timeout and reports the HTTP status. Exits 1 when any check fails.

cache clear. Deletes every {sha256}.json entry in the configured cache directory and prints the count removed.

eval run. Runs the evaluation harness by importing run_evals from the evals directory. Options: --offline / --live (default offline), --cases-dir TEXT (default evals/cases), --output-dir TEXT, --limit INT (first N cases). Prints the report path on success.

## Exit codes

| Code | Raised by |
| --- | --- |
| 0 | Success |
| 1 | EvidenceLedgerError base, resources validate failures, doctor check failures |
| 2 | ConfigurationError, for example unknown profile or missing required env vars |
| 3 | ProviderError |
| 4 | RateLimitError |
| 5 | RetrievalError |
| 6 | UnsafeURLError |
| 7 | InvalidSourceError |
| 8 | ModelOutputError |
| 9 | InsufficientEvidenceError |
| 10 | ReportGenerationError |
| 11 | BudgetExceededError |
| 12 | ResourceCatalogError, for example a missing or unreadable catalog with a hint to run scripts/build_resource_catalog.py |
| 13 | PromptInjectionSuspectedError |
