---
title: Environment Variables
description: Complete reference for every environment variable Arguo reads and how secrets are protected.
group: getting-started
slug: gs-environment-variables
order: 8
---

## Reference table

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `ARGUO_SEARCH_PROVIDER` | no | `tavily` | `tavily` for live web search, `offline` for fixture backed runs. |
| `TAVILY_API_KEY` | when provider is `tavily` | unset | Tavily API key. Required for live search. |
| `ARGUO_MODEL_PROVIDER` | no | `openai-compatible` | `openai-compatible` for any OpenAI style chat completions endpoint, or `null` to run without a model. |
| `ARGUO_MODEL_BASE_URL` | for live runs | unset | Base URL of the model endpoint, for example an OpenAI compatible `/v1` URL. |
| `ARGUO_MODEL_API_KEY` | depends on endpoint | unset | API key for the model endpoint. A warning is emitted when empty. |
| `ARGUO_MODEL_NAME` | for live runs | unset | Model identifier your endpoint expects, such as `glm-4-flash`. |
| `ARGUO_MODEL_TEMPERATURE` | no | `0.2` | Sampling temperature. |
| `ARGUO_MAX_MODEL_CALLS` | no | `24` | Cap on model calls per run. Exceeding it raises exit code 11. |
| `ARGUO_OUTPUT_DIR` | no | `./runs` | Where run directories are written. |
| `ARGUO_CACHE_DIR` | no | `./.arguo-cache` | Where cached fetch responses are stored. |
| `ARGUO_PROFILE` | no | `standard` | One of `quick`, `standard`, `deep`, `academic`. |

Unsupported values fail fast with `ConfigurationError` and a hint listing the accepted options. The cache TTL is 24 hours by default and is set in code, not by an environment variable.

## Minimal setups

Offline, no keys at all:

```bash
arguo research "any question" --offline
```

Live search, no model (heuristic planning, template synthesis):

```bash
export ARGUO_SEARCH_PROVIDER=tavily
export TAVILY_API_KEY=tvly-...
arguo research "any question"
```

Live search plus model: also set `ARGUO_MODEL_BASE_URL`, `ARGUO_MODEL_NAME`, and usually `ARGUO_MODEL_API_KEY`.

## Security notes

- API keys are registered with the logging layer at startup. Every log record passes through a redaction filter that replaces registered secret values with `[REDACTED]`.
- Keys are never written into run artifacts. `sources.json`, `evidence.json`, `audit.json`, `research_plan.json`, and `manifest.json` contain research data only.
- Tavily errors never echo the key. Provider errors carry HTTP status and response snippets, not credentials.
- Never commit `.env`. The example file `.env.example` documents the shape without values.
