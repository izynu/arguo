# Record authoring checklist: {{RUN_NAME}}

Fill in every {{PLACEHOLDER}} before ticking a box. One copy of this
checklist per curation run; the per-record section repeats once per
candidate. If a box cannot be ticked, the record is not written.

## Run header

- Agent task ID: {{TASK_ID}}
- Date of run: {{YYYY-MM-DD}}
- Target authoring file: data/resources/{{TARGET_FILE}}.jsonl
- Assigned categories: {{CATEGORY_KEYS}}
- Planned batch size: {{N}}
- Maintainer instruction or constraint: {{CONSTRAINT_OR_NONE}}

## Run-level checks (once per run)

- [ ] Read references/schema-fields.md in this session.
- [ ] Read data/categories.json and confirmed every assigned key is exact.
- [ ] Collected existing ids and normalized urls from ALL data/resources/*.jsonl files.
- [ ] Target file does not already contain a record for any candidate.
- [ ] Network status noted: {{AVAILABLE_OR_UNAVAILABLE}}

## Per-record checks (repeat for each candidate)

Candidate name: {{CANDIDATE_NAME}}

### Candidate standard

- [ ] Resource is real and publicly reachable.
- [ ] Official homepage confirmed: {{CANONICAL_URL}}
- [ ] Publisher identified: {{PUBLISHER}}
- [ ] Researcher-usable as evidence or data: {{YES_OR_SKIP}}
- [ ] Uncertainty checked; if any field is a guess, candidate is SKIPPED with reason: {{REASON_OR_NONE}}

### Dedupe checks

- [ ] id {{PROPOSED_ID}} not present in any catalog file.
- [ ] Normalized url {{HOST_AND_PATH}} not present in any catalog file.
- [ ] No same name on the same registrable domain: {{DOMAIN}}
- [ ] Not a subpage of an already cataloged homepage: {{CONFIRMED_OR_FLAGGED}}

### Field facts (references/schema-fields.md)

- [ ] id: {{PROPOSED_ID}} matches ^[a-z0-9][a-z0-9-]{2,79}$
- [ ] name: {{NAME}}
- [ ] category: {{CATEGORY_KEY}} is one of the 50 keys
- [ ] subcategory: {{SUBCATEGORY_OR_OMITTED}}
- [ ] description drafted: {{CHAR_COUNT}} characters, target 40 to 320
- [ ] best_for: {{N}} items, each under 60 characters
- [ ] resource_type: {{RESOURCE_TYPE}}
- [ ] region: {{REGION}}; language: {{ISO_639_1}}
- [ ] resource_access: {{OPEN_OR_OTHER}}
- [ ] api_available: {{TRUE_OR_FALSE}}; basis: {{DOCUMENTED_API_OR_NONE}}
- [ ] official_source: {{TRUE_OR_FALSE}}
- [ ] license: {{SPDX_OR_VARIES_BY_ITEM_OR_UNKNOWN}}
- [ ] access_requirements: {{FACTUAL_OR_OMITTED}}
- [ ] date_added: {{YYYY-MM-DD}}; last_checked: null
- [ ] verification_status: documented
- [ ] provenance source: {{SOURCE}}; note: {{NOTE_OR_NULL}}
- [ ] tags: {{TAG_LIST}}, 1 to 8 items, lowercase hyphenated, each under 30 characters

### Style

- [ ] Record is pure ASCII; no em dashes, en dashes, or emoji.
- [ ] Written as exactly one compact JSON object on one line.
- [ ] File ends with a single trailing newline.

### After writing

- [ ] python3 scripts/validate_catalog_file.py data/resources/{{TARGET_FILE}}.jsonl exit code: {{0}}
- [ ] python3 scripts/validate_resources.py exit code: {{0}}
- [ ] No new cross-file warnings introduced by this record.

## Promotion (only after a live check this session)

- [ ] canonical_url requested live and classified ok: {{URL}}
- [ ] verification_status set to verified and last_checked set to {{YYYY-MM-DD}}: {{IDS}}
- [ ] Validators rerun and exit 0 after promotion: {{CONFIRMED}}
