---
title: Troubleshooting
description: Common failure symptoms, their causes, and the exact fix for each.
group: getting-started
slug: gs-troubleshooting
order: 9
---

## TAVILY_API_KEY is not set

Symptom: exit code 2 with "TAVILY_API_KEY is not set but the search provider is 'tavily'."

Cause: live search is selected but the key is missing from the environment. Cause: an exported `.env` file was never sourced, or the variable was set in a different shell.

Fix: `export TAVILY_API_KEY=tvly-...` (and source your `.env` with `set -a; source .env; set +a` if you use one), or run with `--offline`.

## Model endpoint returns 401

Symptom: exit code 3, provider error mentioning HTTP 401.

Cause: the endpoint rejected the credentials, so `ARGUO_MODEL_API_KEY` is wrong, expired, or unset on an endpoint that requires it.

Fix: verify the key and base URL out of band with a single curl style request, then re-export. Note that an empty key only produces a warning, not a blocking error, because some local endpoints allow unauthenticated access.

## Rate limited

Symptom: exit code 4, "rate limited the request (HTTP 429) after 3 attempts."

Cause: the provider rejected requests until the built in backoff (0.5s, 1s, 2s, capped at 4s) was exhausted.

Fix: wait and retry, lower `max_search_rounds` by choosing the quick profile, or reduce results per query in a custom profile.

## Budget exceeded

Symptom: exit code 11 with a message naming runtime, bytes, sources, or model calls.

Cause: the profile's hard limit was reached. This is enforcement working as designed.

Fix: switch to a profile with a larger budget, raise the relevant limit in a custom `ProfileConfig`, or narrow the question.

## Unsafe URL rejected

Symptom: exit code 6.

Cause: the SSRF guard blocked a URL: a non http(s) scheme, embedded credentials, a private or loopback address, or an unresolvable redirect target. A search result on a private host is a common trigger.

Fix: none needed if the target is genuinely internal; that block is intentional. If a public site is blocked, check whether it redirects to an internal address.

## Empty catalog

Symptom: exit code 12, catalog missing or unreadable.

Cause: `catalog/catalog.json` has not been built from the seed files yet.

Fix: run the build script:

```bash
python scripts/build_resource_catalog.py
arguo resources validate
```

## Offline mode behaves differently than expected

Offline runs use six built in fixture results at `example.org`, `example.edu`, and `example.gov`, with heuristic planning and no model calls. Low passage counts and generic content are expected. Offline mode exists to verify the pipeline end to end without keys or network, not to simulate live research. For real output, configure Tavily and a model endpoint.
