---
name: arguo-curator
description: Curator method for the Arguo resource catalog. Use when curating resource catalogs, extending the JSONL resource lists under data/resources/, writing or reviewing resource records, validating resource entries, running dedupe checks on ids and urls, or executing the link verification workflow that promotes documented records to verified. Enforces honest metadata, real and certain candidates only, no invented URLs, and unknown licenses that stay unknown.
---

# Arguo curator

A method for extending the Arguo resource catalog: the JSONL authoring
files under data/resources/ that scripts/build_resource_catalog.py
compiles into the shipped catalog (catalog/catalog.json, catalog/
catalog.jsonl, and catalog/stats.json, also published to public/data/).
The skill is text only: it has no code dependencies and works with any
agent that can read files, check facts about public resources, and write
JSONL.

Core principle: a catalog record is factual metadata about a real,
publicly reachable resource. Every value must be observed on the
resource itself or officially stated by its publisher. Never invent a
URL, a license, an API claim, or a date. When a candidate cannot be
pinned down with certainty, skip it and say so in the run report.

## Method overview

1. Pick candidates that are real and certain
2. Choose the category and write the record
3. Describe the resource honestly
4. Dedupe against existing ids and urls
5. Validate with the repo scripts
6. Live check, then promote documented records to verified
7. Report the run

Work through every run with templates/record-authoring-checklist-template.md
so each step is checked off and nothing is asserted from memory.

## 1. Pick candidates that are real and certain

- A candidate must be a resource you can name, locate at its official
  https homepage, and attribute to a real publisher with a stated role.
  A URL you have not confirmed is a fabrication risk, not a placeholder
  to fix later.
- Prefer the official homepage or primary entry point over mirrors,
  wrappers, and third-party reviews of the resource.
- Judge fit before writing: the resource must be usable by a researcher
  as a source of evidence or data, not a blog post, a landing page, or a
  product sheet.
- Skip uncertain candidates and list them in the run report with the
  reason. Skipping is a correct outcome, not a failure.
- Read references/category-selection.md for the candidate standard, the
  50-key taxonomy, and how to choose between close categories.

## 2. Choose the category and write the record

- Records are JSON objects, one per line, appended to a data/resources/
  JSONL file. Write exactly one object per line with a single trailing
  newline at the end of the file and no pretty printing.
- The record has 18 required fields and 6 optional fields. Field names,
  constraints, enums, and formatting rules are in
  references/schema-fields.md. Read it before writing your first record
  and again whenever a field is ambiguous.
- ids are lowercase kebab-case, stable, and descriptive of the resource,
  not of the run. Tags are lowercase and hyphenated.
- New records enter as verification_status "documented" with
  last_checked null. Only a live check in section 6 changes that.

## 3. Describe the resource honestly

- The description is 40 to 320 characters of factual prose: what the
  resource is, who publishes it, and what a researcher gets from it. No
  hype, no marketing adjectives, no claims you cannot support.
- best_for lists 1 to 4 concrete uses, each under 60 characters. Tags
  are 1 to 8 lowercase hyphenated keywords.
- License fields are the most abused: use a real SPDX identifier only
  when the resource states one, "varies-by-item" for aggregations, and
  "unknown" whenever you did not determine it. An honest unknown beats a
  confident guess.
- Read references/description-quality.md for wording rules, worked
  phrasing, and the tags conventions used across the catalog.

## 4. Dedupe before you write

- Three collision classes matter, because scripts/build_resource_catalog.py
  drops them with an audit trail: identical normalized urls, identical
  ids, and the same resource name on the same registrable domain.
- Normalize before comparing: lowercase the host, strip the trailing dot
  from the host, strip trailing slashes from the path, then compare host
  plus path. https://Example.org/ and https://example.org collide.
- Check both the ids and the normalized urls of every candidate against
  all files in data/resources/, not only the file you are writing.
- Read references/dedupe-and-collisions.md for the check recipe, the
  resolution rules, and how warnings differ from errors.

## 5. Validate

- Validate the file you touched, then the whole catalog, in this order:
    python3 scripts/validate_catalog_file.py data/resources/<file>.jsonl
    python3 scripts/validate_resources.py
- The first script checks one file: schema conformance, duplicate ids
  and urls, style rules, and prints per-category counts. The second runs
  those checks on every data/resources/*.jsonl file, adds cross-file
  uniqueness checks, and verifies the schema document itself.
- A validator exit code of 0 is required before anything else happens.
  Fix records at the source; never weaken a validator expectation by
  editing the schema, the categories, or another task's records.
- Read references/validation-workflow.md for what each check covers,
  common failures and their fixes, and the ASCII sweep one-liners.

## 6. Live check and promote

- The repo's link checker is scripts/check_links.py. Its offline mode is
  purely syntactic and its --live mode makes real requests: HEAD first
  with a GET fallback on 405, concurrency 4, a 10 second timeout, and a
  0.5 second pause per request, capped at --max urls per run.
- The checker reads the built catalog (catalog/catalog.json) by default,
  so records become link-checkable after a catalog build; a --catalog
  flag can point it at another file.
- A record is promoted from "documented" to "verified" only after a live
  check of its canonical_url succeeded in this session. Promotion means
  setting verification_status to "verified" and last_checked to the date
  of the successful check. The validator enforces last_checked on every
  verified record.
- Read references/link-checking.md for the promotion workflow, the
  transient versus permanent classification, and the politeness budget.

## Style rules

- Pure ASCII in everything you author: skill files, records, and
  reports. No em dashes, no en dashes, no emoji, no smart quotes.
- No invented URLs, no fake metrics, no invented test results, no
  guessed licenses, no claimed API availability without documentation.
- Honest unknowns stay unknown: license "unknown", api_available false,
  last_checked null, access_requirements omitted unless factual.
- The verification vocabulary is fixed: records are "documented" until a
  live check promotes them to "verified". Never write "confirmed" or
  "working" in place of these two states.
- See examples/example-mini-curation-run.md for every rule applied to a
  small three-record batch, including a skipped-candidates list.

## Output contract

A finished curation run reports, in this order:

- What was written: target file, record counts, and per-category
  distribution for the new records.
- Skipped candidates, each with a reason (duplicate, uncertain, out of
  scope, unreachable).
- Validator outputs: both commands with their exit codes and the printed
  category counts from scripts/validate_catalog_file.py.
- Link verification outcome: what was checked, what was promoted to
  verified with last_checked dates, and what stayed documented.
- Any anomalies for the maintainer, such as pre-existing warnings
  observed while validating.

Use templates/curation-run-report-template.md as the fixed report
format so runs are comparable across sessions and agents.
