# Evidence ledger

<!-- Working record: one row per relevant passage. Fields are defined in
references/evidence-ledger.md. Rules: append rows, never rewrite history;
unknown dates stay unknown; snippets are not passages. Delete these comment
blocks before delivering the ledger as an appendix. -->

- Run ID: {{RUN_ID}}
- Research question: {{RESEARCH_QUESTION}}
- Ledger started: {{DATE}}

## Source register

<!-- One row per distinct source. Same underlying text at many URLs is one
source. IDs must never be reused for a different source. -->

| source_id | title | publisher | canonical URL | published_at | retrieved_at | independence_group |
|-----------|-------|-----------|---------------|--------------|--------------|--------------------|
| {{S1}} | {{TITLE}} | {{PUBLISHER}} | {{CANONICAL_URL}} | {{PUBLISHED_AT_OR_UNKNOWN}} | {{RETRIEVED_AT}} | {{REGISTRABLE_DOMAIN_OR_GROUP}} |

## Evidence records

<!-- supports_or_contradicts: supports, contradicts, context.
verification_status: supported, partially-supported, contradicted,
insufficient-evidence, source-unavailable, requires-human-review. New rows
default to requires-human-review. -->

| claim_text | source_id | source_url | relevant_passage | published_at | retrieved_at | supports_or_contradicts | independence_group | verification_status | limitations |
|------------|-----------|------------|------------------|--------------|--------------|-------------------------|--------------------|---------------------|-------------|
| {{CLAIM_TEXT}} | {{S1}} | {{SOURCE_URL}} | "{{VERBATIM_QUOTE_OR_TIGHT_PARAPHRASE}} ({{LOCATOR}})" | {{PUBLISHED_AT_OR_UNKNOWN}} | {{RETRIEVED_AT}} | {{RELATION}} | {{INDEPENDENCE_GROUP}} | requires-human-review | {{LIMITATIONS_OR_EMPTY}} |

<!-- Passage rules: verbatim quotes in quotation marks, exactly as written;
paraphrases labeled as paraphrase; always include a locator (section, page,
table, timestamp). Keep contradicting rows: they are evidence too. -->

## JSONL variant (for tooling)

<!-- When the run feeds the Python toolkit, emit the same records as JSONL
objects with these field names, one object per line:
claim_text, source_id, source_url, relevant_passage, published_at,
retrieved_at, supports_or_contradicts, independence_group,
verification_status, limitations. Unknown values are null, never invented. -->

## Ledger notes

- {{LEDGER_NOTE}}

<!-- Record status changes, superseded rows, injection attempts flagged per
references/prompt-injection-defense.md, and anything an auditor needs to
understand the table above. -->
