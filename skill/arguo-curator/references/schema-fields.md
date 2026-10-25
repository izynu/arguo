# Schema fields for resource records

One catalog record is one JSON object on one line of a data/resources/
JSONL file. The authoritative definition is data/schemas/resource.schema.json;
scripts/validate_catalog_file.py enforces a built-in mirror of it. When
this reference and the schema ever disagree, the schema wins and the
maintainer should be told.

## Required fields (18)

- id: string matching ^[a-z0-9][a-z0-9-]{2,79}$. Lowercase kebab-case,
  3 to 80 characters, starts with a letter or digit. Stable across runs;
  never rename an id that other records or tasks may reference.
- name: string, 2 to 120 characters by schema. Use the official name,
  with the common abbreviation in parentheses when helpful.
- canonical_url: string starting with https://. The official homepage or
  primary entry point. Never a mirror, a DOI resolver, or a URL you did
  not confirm.
- category: string, exactly one of the 50 keys in data/categories.json.
- description: string, 40 to 320 characters, factual prose.
- best_for: array of 1 to 4 strings, each at most 60 characters.
- resource_type: string, one of: database, portal, api, archive,
  repository, library, search-engine, tool, documentation,
  dataset-registry, journal, registry, standard, preprint-server,
  agency, organization, program.
- publisher: string, 2 to 120 characters. The organization actually
  responsible for the resource.
- region: string. "global" or a specific country or region name in
  English, matching the resource's scope, not its hosting.
- language: string. Primary interface language as an ISO 639-1 code,
  for example "en", "fr", "zh".
- resource_access: string, one of: open, free-registration,
  partial-open, paid, mixed.
- api_available: boolean. True only when a public API exists and is
  documented. When in doubt, false.
- official_source: boolean. True when the publisher is the originating
  authority for the data or content; false for aggregators and mirrors.
- license: string. An SPDX identifier when the resource states one, a
  short license name otherwise, "varies-by-item" for aggregations, and
  the literal string "unknown" when you did not determine it.
- date_added: string, ISO date YYYY-MM-DD, the date the record was
  written.
- verification_status: string, one of: verified, documented,
  community-submitted, deprecated. New curation writes "documented".
- provenance: object with required key "source" (string, at most 80
  characters) and optional key "note" (string or null, at most 300
  characters). No other keys. Existing repo values for source are
  "curated-seed" and "curated-expansion"; use "curated-expansion" for
  agent curation runs unless the maintainer says otherwise.
- tags: array of 1 to 8 strings, each at most 30 characters, lowercase
  and hyphenated.

## Optional fields (6)

- subcategory: string or null, at most 80 characters. Free text; reuse
  the wording already used in the same category when one fits.
- documentation_url: https string or null. Only when a real
  documentation page exists.
- attribution_requirements: string or null, at most 200 characters.
- access_requirements: string or null, at most 200 characters. Include
  only when factual, for example registration or eligibility rules.
- last_checked: ISO date string or null. Null until a successful live
  check; then the date of that check.
- status_notes: string or null, at most 300 characters.

No other keys are allowed. The schema sets additionalProperties to
false, and the validator rejects unexpected field names.

## JSONL formatting rules

- Exactly one JSON object per line, serialized compactly, one line per
  record. Never pretty print records across multiple lines.
- Key order is not enforced, but existing files follow the schema order;
  matching it keeps diffs readable.
- End the file with a single trailing newline. Do not append blank
  lines, comments, or a second newline.
- Blank lines inside the file are skipped by the validator but should
  not be there; write clean files.
- Pure ASCII throughout. Escape or avoid any character outside ASCII;
  em dashes, en dashes, and emoji are validator errors in name,
  description, and publisher, and style violations everywhere else.
- Numbers are booleans or strings exactly as specified: no integers
  where strings are required, no nulls where booleans are required.

## Honest value rules

- Never invent values to satisfy the schema. If you cannot determine a
  value, use the honest representation: "unknown" for license, false
  for api_available and official_source when unconfirmed, null for the
  optional text fields, and omit optional fields you have no facts for.
- Dates are real dates: date_added is the day you wrote the record;
  last_checked is the day the live check ran. Do not backdate.
- Region "global" is for resources with worldwide scope; a national
  statistical office is its country, even if its site is in English.

See references/description-quality.md for how to phrase the free-text
fields, and templates/record-authoring-checklist-template.md for the
per-record checklist that walks these fields in order.
