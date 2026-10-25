---
title: Dates
description: Publication, event, and retrieval dates, explicit unknown handling, and why nothing is guessed.
group: core-concepts
slug: cc-dates
order: 13
---

## Four different dates

The toolkit keeps four date fields apart because conflating them is how stale evidence gets dressed as current:

| Field | Meaning |
| --- | --- |
| `published_at` | When the source was published, if the provider or page actually states it. |
| `updated_at` | When the source was last updated, when stated. |
| `event_or_observation_date` | When the underlying event or measurement occurred, which can differ greatly from publication. |
| `retrieved_at` | When this run fetched the content, always set. |

A report published in 2026 describing a 2019 survey carries a 2019 event date and a 2026 publication date. Recency judgments use the right field for the right purpose.

## Explicit "date unknown"

When no date is known, the value stays `null` in JSON and reports render the phrase "date unknown". The formatter used for reports, `format_date_or_unknown`, has no code path that invents a value. A missing date is a fact about our knowledge, and the toolkit treats it as information rather than filling it in.

## Parsing rules

The date parser is deliberately narrow. It accepts ISO 8601 dates and datetimes, RFC 2822 style dates, "Month D, YYYY" forms, and a bare four digit year, which is anchored to January 1 of that year because that is all the input states. Anything else, including ambiguous partial strings, returns None rather than a guess. If a page says "last spring", the parsed value is null and the report says the date is unknown; it does not silently become a year.

## Why this matters downstream

Recency ratings on the source quality rubric need real dates, so unknown recency stays `unknown` instead of aging by guesswork. `--since` constraints filter on stated publication dates only. And provenance stays honest: a reader of `evidence.json` can always tell the difference between "the source is undated" and "we did not check".
