---
title: Configuration
description: How settings resolve from environment variables, what each ARGUO variable does, and what each profile changes.
group: getting-started
slug: gs-configuration
order: 7
---

## Settings precedence

Settings come from environment variables. Precedence, highest first:

1. Values passed explicitly in code, such as `get_settings(env={...})`, which replaces the environment entirely for that call.
2. Process environment variables, including variables exported from your `.env` file.
3. Built-in defaults in `config.py`.

`get_settings()` caches the resolved object for the process. Call `get_settings(reload=True)` after changing the environment. The CLI's own flags apply on top of the resolved settings; for example `--profile deep` and `--max-sources 12` override `ARGUO_PROFILE` and the profile's source budget for that run. Invalid values raise `ConfigurationError` with a hint rather than falling back silently. Empty strings count as unset.

## ARGUO variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `ARGUO_SEARCH_PROVIDER` | `tavily` | `tavily` or `offline` fixture provider. |
| `ARGUO_MODEL_PROVIDER` | `openai-compatible` | `openai-compatible`, or `null` for no model. |
| `ARGUO_MODEL_BASE_URL` | unset | OpenAI compatible chat completions endpoint. |
| `ARGUO_MODEL_API_KEY` | unset | Bearer key for that endpoint. |
| `ARGUO_MODEL_NAME` | unset | Model identifier the endpoint expects. |
| `ARGUO_MODEL_TEMPERATURE` | `0.2` | Sampling temperature for model calls. |
| `ARGUO_MAX_MODEL_CALLS` | `24` | Hard cap on model calls per run. |
| `ARGUO_OUTPUT_DIR` | `./runs` | Directory for run artifacts. |
| `ARGUO_CACHE_DIR` | `./.arguo-cache` | Directory for cached fetch responses. |
| `ARGUO_PROFILE` | `standard` | Default profile when `--profile` is absent. |

`TAVILY_API_KEY` is required when the search provider is `tavily`.

## Profiles

| Profile | Subquestions | Rounds | Results per query | Max sources | Model calls | Followup rounds | Runtime cap | Concurrency | Report |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quick | 3 | 1 | 4 | 8 | 8 | 0 | 120 s | 4 | concise |
| standard | 5 | 2 | 6 | 15 | 18 | 1 | 300 s | 4 | standard |
| deep | 8 | 3 | 8 | 30 | 30 | 2 | 600 s | 6 | detailed |
| academic | 6 | 2 | 8 | 20 | 24 | 1 | 480 s | 4 | detailed |

Profiles change behavior, not just numbers. `deep` turns on `contradiction_focus`, which raises the priority of evidence for and against competing claims. `academic` turns on `scholarly_mode`, which prefers study oriented query variants and adds methods, limitations, and gap structure to planning and reports. Report length controls synthesis verbosity.

Run `arguo config check` to print the effective settings for your shell.
