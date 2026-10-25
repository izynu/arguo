---
title: Browsing the resource catalog
description: How to search, list, and inspect the resource catalog with the resources commands and the website explorer.
group: resource-library
slug: browsing-the-catalog
order: 1
---

## What you are browsing

The catalog holds 1,570 records across 50 categories and 82 regions in the 2026-10-25 build. The seeds live in data/resources/*.jsonl and are merged into catalog/catalog.jsonl and catalog/catalog.json, with aggregate counts in catalog/stats.json.

## The resources commands

The catalog CLI groups its operations under resources:

- resources search <terms>: finds records by a case-insensitive substring match over the resource name, the description, and the tags. It is a plain match, not a ranked relevance search, so short distinctive terms work better than long phrases.
- resources list: prints records, optionally narrowed by a category key from data/categories.json or by catalog fields such as resource_type, resource_access, region, language, api_available, or official_source.
- resources stats: prints the same aggregate counts the build emits into catalog/stats.json, for example 1,570 total records, 50 categories, and the per-category and per-status breakdowns.

## Filters

Filters map directly onto record fields, so they combine: a category key plus "open" access plus api_available true narrows to the open programmatic slice of that category. Because the enums are fixed in the schema, filter output is predictable.

## The website explorer

The site's resource explorer presents the same built catalog files, so a count shown in the browser and a count from the commands describe the same build. Filters in the explorer mirror the same fields, which keeps the two interfaces consistent by construction rather than by coincidence.

## Without any tooling

Every catalog file is plain JSONL and the schema is published at data/schemas/resource.schema.json, so grep, jq, or a short script can reproduce anything the commands do. The handbook includes a worked one line example of verifying a per-category count this way before citing it.
