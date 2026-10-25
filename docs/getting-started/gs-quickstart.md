---
title: Quickstart
description: A five minute path from install to a complete run, offline first, then a live run with real providers.
group: getting-started
slug: gs-quickstart
order: 3
---

## Step 1: check the environment

```bash
arguo doctor
```

`doctor` reports package health, provider configuration, and catalog availability without any network activity. Fix what it flags before continuing.

## Step 2: run the offline demo

```bash
arguo research "What do fixture sources say about evidence based research?" --offline
```

Offline mode runs all ten pipeline stages against built in fixture results. Titles start with "Example fixture result" so the output can never be mistaken for live research. Planning is heuristic and no model calls are made, which is why an offline run is fast and free.

## Step 3: a live run

Export your keys, then run without `--offline`:

```bash
export TAVILY_API_KEY=tvly-...
export ARGUO_MODEL_BASE_URL=https://your-endpoint/v1
export ARGUO_MODEL_API_KEY=...
export ARGUO_MODEL_NAME=your-model-name
arguo research "What do primary sources report about urban heat island mitigation costs?" --profile standard --since 2022-01-01
```

The model adapter is any OpenAI compatible chat completions endpoint. If a required variable is missing, the CLI fails with a configuration error and a hint instead of half running.

## The six output artifacts

Every run writes one directory per run under `runs/{run_id}/` (configurable with `ARGUO_OUTPUT_DIR`):

| Artifact | Contents |
| --- | --- |
| `report.md` | The human readable report with citations such as `[S3]` and `[C2]`. |
| `sources.json` | Every source considered, including failed fetches with an access note. |
| `evidence.json` | The evidence ledger: sources, evidentiary passages, and claims with links. |
| `research_plan.json` | The stage B plan: subquestions, queries, evidence requirements, limitations. |
| `audit.json` | Citation audit results: issues found, verdict counts, and the automation limitation note. |
| `manifest.json` | Stage timings, provider names, budget snapshot, counts, warnings, and offline mode flag. |

## Where to look first

Open `report.md` for the narrative, then `audit.json` for issues, then `manifest.json` for stage status and how much of the budget was spent. If anything looks wrong, the ledger in `evidence.json` lets you trace any claim back to its exact passages and source URLs.
