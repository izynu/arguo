---
title: Caching
description: The ResponseCache file format, TTL, the cache clear command, fetch cache keys, and reproducibility notes.
group: core-concepts
slug: cc-caching
order: 16
---

## File format

`ResponseCache` is a content addressed JSON cache: one file per key, named `{sha256}.json` inside `ARGUO_CACHE_DIR` (default `./.arguo-cache`). Each entry holds two fields:

```json
{
  "stored_at": "2026-01-15T10:30:00+00:00",
  "value": { }
}
```

Writes are atomic: the payload goes to a `.tmp` file that is then replaced into place. Storage failures are logged and never raised. Reads are equally forgiving: corrupt JSON, missing fields, and unparsable timestamps are all treated as cache misses, so a damaged cache directory can never break a research run. `stats()` reports entry counts plus the oldest and newest timestamps, counting unreadable files as entries so damage stays visible.

## TTL

A cached value counts as fresh for `ttl_s` seconds, 86,400 by default (24 hours). The TTL is set in code when the cache is constructed; there is no environment variable for it. Expired entries are simply treated as misses, not proactively deleted, except by `clear()`.

## Fetch caching

The fetcher caches successful GET responses under the key `fetch:{url}`, storing the full FetchResult as the value: page text, final URL, status, content type, byte counts, and notes. On a later call within the TTL, the cached result is replayed without network activity. Failures are not cached, so a transient fetch error is retried on the next run.

## The cache clear command

```bash
arguo cache clear
```

Deletes every `*.json` entry in the cache directory and prints how many were removed. Use it when you deliberately want a fresh fetch of everything, for example after a site you know changed.

## Reproducibility notes

Caching trades freshness for stability: within the TTL, repeated runs see identical page text for the same URLs, which makes comparisons and debugging easier. It is not a reproducibility guarantee; after expiry a run may see newer content, and live search results are not cached at all. For fully deterministic behavior, offline mode is the contract: fixture data, heuristic planning, no network, and no cache dependence.
