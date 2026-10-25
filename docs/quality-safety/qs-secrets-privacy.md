---
title: Secrets and Privacy
description: How Arguo handles credentials, what it stores locally, and why it sends nothing anywhere except provider calls.
group: quality-safety
slug: qs-secrets-privacy
order: 6
---

Secret handling. All credentials enter through environment variables: TAVILY_API_KEY for search, ARGUO_MODEL_API_KEY and ARGUO_MODEL_BASE_URL for the model endpoint, plus behavior switches such as ARGUO_PROFILE, ARGUO_OUTPUT_DIR, and ARGUO_CACHE_DIR. Settings never write secret values to disk or into reports.

Never logged. utilities/logging.py registers secret values in a SecretRegistry at startup. A logging filter scrubs every emitted record, message and arguments, replacing registered values with [REDACTED]. The structured JSON formatter goes through the same filter, so log output carries no key material. Scrubbing applies to registered values of six characters or more; short or unregistered values are not covered, which is one more reason keys belong only in the environment.

Never in artifacts. Run artifacts live in the output directory, default ./runs, overridable with ARGUO_OUTPUT_DIR, as run manifests, plans, evidence ledgers, and reports. These contain research questions, sources, passages, budgets, and timings. They should not contain credentials, and reports must never quote them.

What is stored locally. Two directories: runs/ for artifacts, and the response cache, default ./.arguo-cache, overridable with ARGUO_CACHE_DIR, whose entries expire after a TTL of one day by default. The cache holds fetched pages and search results keyed by URL. Deleting both directories removes everything the toolkit persisted.

No telemetry. The package contains no analytics, phone-home, or crash reporting code. Its runtime dependencies are pydantic, typer, and httpx.

Research questions. A question is sensitive: it can reveal what a person or organization is investigating. Questions are stored only in local run artifacts; nothing is transmitted except the search and model provider calls needed to answer them.
