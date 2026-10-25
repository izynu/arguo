# Link checking and promotion to verified

The repo's rule is fixed: records are "documented" until a live check
promotes them to "verified". This reference is the promotion workflow.

## What scripts/check_links.py does

Usage:

    python3 scripts/check_links.py [--live] [--max N] [--catalog PATH] [--report PATH]

- Offline mode (default) is purely syntactic and uses the standard
  library only. Every canonical_url must parse as an absolute URL, use
  https, have a host containing a dot, and contain no spaces.
  Placeholder hosts (example.com and friends) are flagged as "info"
  issues because fixtures legitimately use them; likely TLD typos and
  doubled TLDs are flagged as "warning" issues. The catalog files are
  never modified in any mode.
- Live mode (--live) makes real requests with httpx: HEAD first with a
  GET fallback when a server answers 405, concurrency 4, a 10 second
  timeout per request, and a 0.5 second pause between requests. At most
  --max URLs are requested per run (default 200) to stay polite.
- Results are written to catalog/link-check-report.json with
  generated_at, the number checked, and a list of issues carrying id,
  url, kind, severity, and detail. Live runs record status and
  classification per URL.

## Classification of live results

- Below 400: ok.
- 4xx: permanent. A 404 on a canonical homepage is a real defect in the
  record and should be reported to the maintainer, not papered over.
- 5xx, timeouts, and connection errors: transient. Transient failures
  are not evidence that a resource is gone; rerun later or note them.
- Exit code 0 on success, including offline runs that report issues;
  exit code 1 only when the catalog is missing or the report cannot be
  written.

## Which URLs are checked

The checker reads the built catalog, catalog/catalog.json by default,
not the authoring files in data/resources/. Consequences:

- New records become link-checkable once a catalog build has merged
  them in (scripts/build_resource_catalog.py writes catalog/catalog.json
  and catalog/catalog.jsonl).
- You can point --catalog at a specific JSON file when the maintainer
  asks you to check a subset without a full build. The file must be the
  built-catalog format, a JSON array of records.
- Do not confuse the checker's report file with the catalog itself:
  catalog/link-check-report.json is evidence, never an input.

## The promotion workflow

1. Validation has passed for your file (exit 0 from both validators).
2. The record's canonical_url was requested by a live run in this
   session and classified ok.
3. Promote by editing your record in the authoring JSONL: set
   verification_status to "verified" and last_checked to the date of
   the successful check, in ISO YYYY-MM-DD form.
4. Rerun both validators. The first one errors on any verified record
   whose last_checked is missing, so a promotion that skips the date
   will not pass.
5. Record the promotion in the run report: which ids, which URLs, which
   date.

## What does not count as a live check

- The offline syntactic check. It never touches the network.
- Someone else's earlier report found in the repo, including a fresh
  catalog/link-check-report.json you did not run yourself this session.
- A memory, a search result snippet, or the URL appearing in another
  catalog.
- A redirect target that succeeded while the canonical URL itself
  failed: the record's canonical_url is what must classify ok.

If the network is unavailable, the honest outcome is a batch that stays
documented and a run report that says the live check could not run.
Never fabricate a last_checked date; a fake date defeats the one thing
the verified status promises.

## Politeness and budget

- Live runs default to at most 200 URLs. For bigger batches, split the
  promotion across runs or raise --max only when the maintainer asks.
- The checker already spaces requests by 0.5 seconds; do not add
  parallel load of your own on top of it.
- A transient failure today is a promotion deferred, not a lost record.

See references/validation-workflow.md for the validation gate that must
pass before any promotion, and templates/curation-run-report-template.md
for how the link-check outcome is reported.
