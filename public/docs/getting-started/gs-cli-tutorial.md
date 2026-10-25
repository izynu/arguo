---
title: CLI Tutorial
description: A tour of every arguo command group, research flags, and the exit code table.
group: getting-started
slug: gs-cli-tutorial
order: 5
---

## Research

```bash
arguo research "Which countries index the minimum wage to inflation?" \
  --profile deep --since 2021-01-01 --max-sources 12
```

- `--profile` selects `quick`, `standard`, `deep`, or `academic` and changes subquestion counts, rounds, and budgets.
- `--since` sets a time boundary that reaches the planner as a query constraint and a plan field.
- `--max-sources` caps the source budget for this run.
- `--offline` forces fixture backed search with heuristic planning.

## Resources

The resource catalog commands consult the built catalog:

```bash
arguo resources search "census"
arguo resources list
arguo resources stats
arguo resources validate
```

`search` finds catalog records by keyword, `list` browses categories, `stats` prints catalog counts, and `validate` checks the catalog files against the schema. The catalog ships as curated seed data in `data/resources/*.jsonl`; the merge script `scripts/build_resource_catalog.py` produces `catalog/catalog.json`, `catalog.jsonl`, and `stats.json`.

## Config, doctor, and cache

```bash
arguo config check
arguo doctor
arguo cache clear
```

`config check` resolves your environment into effective settings and reports problems such as a missing `TAVILY_API_KEY` or an unknown profile. `doctor` checks package, provider, and catalog health. `cache clear` deletes every cached fetch response and reports how many entries were removed.

## Exit codes

The CLI uses a stable exit code per failure class so scripts can react precisely:

| Code | Meaning |
| --- | --- |
| 1 | General error |
| 2 | Configuration error |
| 3 | Provider error |
| 4 | Rate limit hit |
| 5 | Retrieval failure |
| 6 | Unsafe URL rejected |
| 7 | Invalid source |
| 8 | Invalid model output |
| 9 | Insufficient evidence |
| 10 | Report generation failure |
| 11 | Budget exceeded |
| 12 | Catalog error |
| 13 | Prompt injection suspected |

Every error also prints a message and, where possible, a hint. Exit code 9 deserves emphasis: it can mean the run worked correctly and the honest answer is that the evidence base is inadequate. Exit code 13 means retrieved content contained instruction like patterns and the configured policy failed closed.
