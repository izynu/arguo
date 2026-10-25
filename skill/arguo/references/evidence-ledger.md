# The evidence ledger

The ledger is the working record of the research. One row per relevant
passage. Every claim in the final report must map to one or more ledger rows,
and every ledger row must come from a passage you actually read. The ledger is
what makes the report auditable.

## Record fields

These are the canonical fields used by the Arguo toolkit. The typed
versions live in the Python package under python/arguo; in the skill
they are written as markdown table rows or JSONL objects.

- claim_text
  The claim the passage bears on, phrased as one atomic, self-contained
  sentence. Write the claim before judging the passage, so the passage is not
  bent to fit a vague memory of it.

- source_id
  A stable short identifier such as S1, S2, used consistently in the ledger,
  the source list, and the report. Never reuse an ID for a different source.

- source_url
  The canonical URL you actually consulted. Use the origin's URL, not a
  redirect wrapper, tracking link, or mirror. Record the URL after redirects
  settle, when the tooling exposes that.

- relevant_passage
  A verbatim quote in quotation marks, or a tight paraphrase labeled as
  paraphrase. Include a locator: section, heading, page, table, or timestamp.
  A passage long enough to carry context but short enough to check.

- published_at
  The publication date, only when actually known. Unknown stays unknown.
  Never infer a date from a URL slug alone. See references/publication-dates.md
  for the four date kinds and which one belongs here.

- retrieved_at
  When you fetched the content. Required for every row. This is what makes
  later link rot diagnosable.

- supports_or_contradicts
  One of: supports, contradicts, context. Contradicting rows are first-class
  records; never delete them to clean up.

- independence_group
  The registrable domain or syndication group behind the text. Two URLs with
  the same group do not corroborate each other. Assign it consciously:
  a press release and every outlet reprinting it share one group.

- verification_status
  One of: supported, partially-supported, contradicted, insufficient-evidence,
  source-unavailable, requires-human-review. New rows default to
  requires-human-review until passage support and corroboration have been
  checked. See references/claim-verification.md for what changes a status.

- limitations
  What limits this row's evidential weight: translated, snippet-only, single
  source, paywalled abstract, provisional data, declared conflict of interest.
  An empty list is a claim that the row is unqualified; make it honestly.

## Working format

Markdown table for human review, JSONL for tooling. Templates/
evidence-ledger-template.md contains both. Keep IDs stable across rewrites;
append rather than edit rows, and mark superseded rows instead of deleting.

## Rules for passages

- Quote exactly, including awkward wording; do not silently correct.
- Paraphrases must not smuggle in certainty the passage lacks: if the source
  says "suggests", the paraphrase says "suggests".
- Snippets from search results are not passages. Open the source.
- If only a snippet was available, record the row with the limitation
  "snippet-only" and a verification status that reflects that.

## Rules for dates and unknowns

- Never fabricate any metadata. Unknown is a value.
- Record the observation period when the passage presents data, because the
  observation period, not the page date, determines what the number describes.

## Minimal viable example

Illustrative only, with placeholder URLs:

| field | value |
|---|---|
| claim_text | The device's 2024 firmware update requires a 64-bit processor. |
| source_id | S3 |
| source_url | https://example.org/release-notes |
| relevant_passage | "Starting with release 12.0, installation requires a 64-bit processor." (Release notes, Requirements section) |
| published_at | unknown |
| retrieved_at | 2025-01-15 |
| supports_or_contradicts | supports |
| independence_group | example.org |
| verification_status | requires-human-review |
| limitations | [] |

The report may only cite S3 for that claim after the row has been through the
verification steps in references/claim-verification.md.
