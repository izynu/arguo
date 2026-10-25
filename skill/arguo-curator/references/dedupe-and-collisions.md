# Dedupe and collision checks

Duplicate records are the catalog's most expensive defect, because they
survive authoring, ship to the website, and waste every future curation
run that rediscovers them. The repo already deduplicates at build time,
but that is a safety net, not an excuse: dedupe at authoring time, per
candidate, before anything is written.

## What the tooling actually does

- scripts/validate_catalog_file.py errors on duplicate ids and duplicate
  canonical_urls within one file. Exit code 1.
- scripts/validate_resources.py runs those per-file checks everywhere and
  additionally reports ids and normalized urls that appear in more than
  one file. Cross-file duplicates are warnings by default; pass --strict
  to turn them into errors, as a maintainer would before a release.
- scripts/build_resource_catalog.py drops, with a printed audit trail,
  every record that has an identical normalized URL, an identical id, or
  the same name on the same registrable domain as a record already in
  the build.

## Normalization recipe

Compare URLs the way the scripts do:

- Lowercase the host.
- Strip one trailing dot from the host if present.
- Strip trailing slashes from the path.
- Compare the resulting host plus path.

So https://Example.org/, https://example.org, and https://example.org/
all normalize to example.org and collide. A fragment difference does not
rescue a collision, and neither does a trailing slash. Query strings are
part of the URL, but a canonical homepage should not have one; if your
candidate URL needs a query string to reach the homepage, you probably
have the wrong entry point.

## The three collision classes

1. Same normalized URL: the same resource is already cataloged, possibly
   under a different id or name. Do not add it again.
2. Same id: a different resource claims your id. Choose a more specific
   id, usually by adding the organization or country qualifier, and
   re-check the new id too.
3. Same name on the same registrable domain: the builder treats this as
   a duplicate even when the paths differ. Two different products under
   one domain must be disambiguated by name or one of them must be
   reconsidered.

## How to check before writing

- Collect ids and normalized urls from all data/resources/*.jsonl files
  with a short python3 snippet, then test each candidate against both
  sets. Checking only the file you are about to edit is not enough,
  because cross-file duplicates are what the build collapses.
- Check the candidate's registrable domain against the names of records
  on the same domain. Same domain plus same or nearly same name means
  stop.
- When a candidate's URL is a subpage of a domain that is already
  cataloged at its homepage, treat it as a likely duplicate of the
  homepage record and skip with reason duplicate unless the subpage is
  a genuinely separate research resource, in which case flag it for the
  maintainer instead of deciding silently.

## Resolution rules

- Already cataloged: skip. Record the existing id that collided in the
  run report so the maintainer can audit the decision.
- Id taken by a different resource: pick a more specific id and rerun
  every check for the new id.
- Name collision on one domain: disambiguate the names factually, or
  skip. Do not rename existing records to make room; that is a
  maintainer edit, not a curation decision.
- Never edit records written by other tasks to resolve a collision you
  caused. Report it.

## Warnings versus errors

Cross-file duplicate warnings from scripts/validate_resources.py are
pre-existing conditions of the repo's authoring files, not something a
curation run may ignore into its own file. Your run must leave the
warning list no worse than it found it: no new duplicate ids, no new
duplicate urls, and no new same-domain name twins.

See references/validation-workflow.md for the command sequence that
surfaces all of these, and templates/record-authoring-checklist-template.md
for the dedupe checkboxes in the per-record checklist.
