---
title: The sync pipeline
description: How resource-sources.yaml and sync_resources.py keep catalog changes deliberate, safe, and reproducible.
group: resource-library
slug: sync-pipeline
order: 11
---

## What sync is for

The sync pipeline pulls resource metadata from configured upstream sources instead of relying only on hand maintained seeds. It is disabled by default: catalog changes happen deliberately, not as a side effect of running other commands. When you want upstream refresh, you enable it in configuration and run it explicitly.

## Configuration

data/resource-sources.yaml lists the upstream sources, each with its location and the scope of what it may update. Treat the file like any other change to the catalog: it goes through review, because it determines what the pipeline is allowed to touch.

## Behavior of scripts/sync_resources.py

The pipeline is built around three rules. First, validate on import: records pulled from upstream are checked against the resource schema when they come in, and records that fail validation are rejected rather than written. Second, never overwrite on failure: if a run cannot complete, the existing catalog files are left untouched, so a partial or failed sync cannot damage the catalog. Third, write a summary: a completed run produces a summary of what was added, updated, or skipped, so every change is reviewable after the fact.

## Rate limits and robots compliance

The sync fetches politely. It respects rate limits on upstream hosts, honors robots directives, and identifies itself with the project user agent. A source that cannot be fetched within those limits is skipped and reported in the summary rather than hammered.

## Reproducibility

The same configuration against the same upstream state produces the same catalog output. Because summaries record what changed and the merge step keeps an audit trail of dropped duplicates, a catalog build can be traced back to the seeds and sync runs that produced it. The verification statuses of synced records follow the same rules as every other record: verified only after a real live check, never by assumption.
