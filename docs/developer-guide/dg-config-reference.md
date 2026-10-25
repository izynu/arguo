---
title: Configuration Reference
description: Settings fields, environment variables, budgets, and the built-in research profiles.
group: developer-guide
slug: dg-config-reference
order: 8
---

Settings is a Pydantic model in arguo.config, resolved from environment variables by Settings.from_env. get_settings(env=None, reload=False) caches one module-level instance and re-reads the environment when reload is True or an env mapping is passed.

| Setting | Default | Environment variable |
| --- | --- | --- |
| search_provider | tavily | ARGUO_SEARCH_PROVIDER (tavily or offline) |
| tavily_api_key | None | TAVILY_API_KEY |
| model_provider | openai-compatible | ARGUO_MODEL_PROVIDER (openai-compatible or null) |
| model_base_url | None | ARGUO_MODEL_BASE_URL |
| model_api_key | None | ARGUO_MODEL_API_KEY |
| model_name | None | ARGUO_MODEL_NAME |
| model_temperature | 0.2 | ARGUO_MODEL_TEMPERATURE |
| max_model_calls | 24 | ARGUO_MAX_MODEL_CALLS |
| output_dir | ./runs | ARGUO_OUTPUT_DIR |
| cache_dir | ./.arguo-cache | ARGUO_CACHE_DIR |
| cache_ttl_s | 86400 | not read from the environment |
| user_agent | Arguo/0.1 (+repo URL) | not read from the environment |
| profile | standard | ARGUO_PROFILE (quick, standard, deep, academic) |

Invalid provider names or a non-integer max model call count raise ConfigurationError. validate_for_research(offline) raises ConfigurationError when the tavily provider lacks TAVILY_API_KEY, or when the openai-compatible model provider lacks a base URL or model name, and returns warnings otherwise, for example an empty model API key.

ProfileConfig carries name, description, subquestion_target, budget, report_length (concise, standard, detailed), scholarly_mode, and contradiction_focus. ResearchBudget defaults are: max_search_rounds 2, results_per_query 6, max_sources 15, max_total_bytes 8000000, per_request_timeout_s 20.0, concurrency 4, max_model_output_tokens 2000, max_retries 2, max_runtime_s 300.0, max_model_calls 24, max_cost_usd None (best effort only), followup_rounds 1.

| Profile | Subquestions | Rounds | Results per query | Sources | Model calls | Followups | Runtime s | Concurrency | Extras |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quick | 3 | 1 | 4 | 8 | 8 | 0 | 120 | 4 | concise report |
| standard | 5 | 2 | 6 | 15 | 18 | 1 | 300 | 4 | baseline |
| deep | 8 | 3 | 8 | 30 | 30 | 2 | 600 | 6 | detailed report, contradiction focus |
| academic | 6 | 2 | 8 | 20 | 24 | 1 | 480 | 4 | detailed report, scholarly mode |

BudgetTracker enforces these limits during a run: record_search, record_model_call, record_bytes, and record_source raise BudgetExceededError when a limit is exceeded, and snapshot returns spent counters plus the limits.
