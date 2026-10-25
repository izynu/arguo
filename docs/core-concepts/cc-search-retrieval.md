---
title: Search and Retrieval
description: The provider interface, normalized results, deduplication rules, retry behavior, and fetch caching.
group: core-concepts
slug: cc-search-retrieval
order: 5
---

## The provider interface

Every search provider implements `SearchProvider` from `arguo.providers.base`: a `name` property plus an async `search(query, max_results)` returning `NormalizedResult` items. Construction must not touch the network, and failures must raise the typed exceptions, never SDK specific errors. Two implementations ship: `TavilySearchProvider` and `OfflineSearchProvider`.

## NormalizedResult

Providers map their raw hits into one shape: `title`, `url`, `snippet`, `published_at`, `score`, `provider`, and `raw_metadata`. Missing fields stay None. The Tavily adapter is deliberately tolerant: one mistyped optional field never discards a whole result, while a URL that fails validation is filtered later by dedupe.

## Deduplication rules

Dedupe is conservative, applied in result order:

1. Results whose URL cannot be normalized or validated are skipped.
2. Exact duplicates (same normalized URL) are dropped, keeping the first. Normalization lowercases scheme and host, removes default ports, and strips known tracking parameters while preserving query strings that carry content.
3. Near duplicates (identical title AND identical registrable domain) are dropped, keeping the first.

Repetition of one story across different domains is not collapsed here. That is syndication, and stage G handles it with passage similarity rather than URL tricks.

## Budgets and retries

Search spends the profile's budget: `max_search_rounds`, `results_per_query`, and `max_sources` all bound how much search can consume, and the BudgetTracker records every request. The Tavily adapter retries HTTP 429 and 5xx plus transport errors with exponential backoff (0.5s, 1s, 2s, capped at 4s, two retries by default), then maps 429 to `RateLimitError` (exit code 4) and other failures to `ProviderError` (exit code 3).

## Fetching and caching

Retrieval goes through the fetcher behind the URL guard: at most 3 redirect hops, each revalidated; a per request byte cap (2 MB or the run's byte budget, whichever is lower); an allowlist of html, xhtml, json, plain text, and pdf content types, with PDFs recorded but not parsed; and a `FetchResult` that never raises, so failures become visible access notes in the ledger. Successful fetches are cached under the key `fetch:{url}` in the ResponseCache and replayed within the TTL, which makes repeat runs faster and cheaper without hiding that a later run may see newer content.
