# Validation workflow

Validation is a gate, not a suggestion. No record leaves your session
unvalidated, and no run report may claim success without the two
validator commands having been run and having exited 0.

## The command sequence

Run from the repo root, in this order:

1. python3 scripts/validate_catalog_file.py data/resources/<file>.jsonl

   Validates one authoring file: schema conformance against a built-in
   mirror of data/schemas/resource.schema.json, duplicate ids and
   duplicate canonical_urls inside the file, the style rules (no em
   dashes, en dashes, or emoji in name, description, and publisher),
   and that verified records carry last_checked. Prints the record
   count and per-category counts. Exit 0 on pass, 1 on any error, 2 on
   usage errors or a missing file.

2. python3 scripts/validate_resources.py

   Runs the same per-file checks on every data/resources/*.jsonl file,
   then adds cross-file uniqueness of ids and canonical_urls and a
   sanity check of the schema document itself. Cross-file duplicates
   are warnings by default; --strict turns them into errors. Exit 0 on
   pass, 1 when any error was found.

If your session appended to a file that already existed, step 1 must be
run against the whole resulting file, not just your lines: the
validator sees one file.

## Before the validators: quick self-checks

- JSON parse sweep: every line of the target file must parse as JSON.
  A short python3 loop over the file catches trailing commas and
  unescaped quotes before the validator does.
- ASCII sweep: the whole file must decode as ASCII, with no U+2013, no
  U+2014, and no emoji codepoints. One python3 line does it; the exact
  one-liner is in the README's verification section.
- Line ending check: the file ends with exactly one trailing newline.

## Reading validator output

- "PASS: schema, uniqueness, and style checks OK" from the first
  validator means the file is structurally clean.
- Per-category counts let you confirm the category distribution you
  intended before you write it into the run report.
- Error lines are prefixed with the line number. Fix records at the
  line the validator names, rerun, and repeat until exit 0.

## Common failures and fixes

- "unknown category": the category key is misspelled or stale. Check
  data/categories.json; there are 50 valid keys.
- "bad id": the id pattern is ^[a-z0-9][a-z0-9-]{2,79}$. Uppercase
  letters, underscores, leading hyphens, and ids shorter than three
  characters all fail.
- "canonical_url must be an https URL": http or a bare domain was used.
- "description length ... outside 40-320": trim or expand the prose.
- "'verified' records need last_checked": a promotion set
  verification_status without a last_checked date, or the date field
  was left null.
- "unexpected fields": an optional field was misspelled, or an extra
  key was invented. Only the 18 required and 6 optional fields exist.
- Duplicate id or url: go back to the dedupe step; do not delete the
  other record.

## What you must never do to pass

- Never edit data/schemas/resource.schema.json or
  data/categories.json. They are contracts.
- Never edit or delete records authored by other tasks to make a
  duplicate or style error disappear. Report the collision to the
  maintainer instead.
- Never mark a record verified to silence a warning. Verification
  comes only from the link-checking workflow.

## Recording the results

The run report quotes both commands with their exit codes and includes
the per-category counts printed by the first validator. If
scripts/validate_resources.py printed pre-existing warnings on files
your run did not touch, copy them into the anomalies section verbatim
so the maintainer can compare against later runs.

See references/dedupe-and-collisions.md for resolving the duplicate
errors the validators report, and references/link-checking.md for what
comes after validation passes.
