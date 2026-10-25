# Category selection and candidate standard

The catalog taxonomy lives in data/categories.json. It currently holds
50 category keys, and every record's category field must be exactly one
of those keys. Scripts, the CLI, and the website all key off these
identifiers, so a near miss like "government-stats" instead of
"government-statistics" is a validation error.

## The candidate standard: real and certain

A candidate enters the catalog only when all of the following hold:

- The resource exists and is publicly reachable, and you can name its
  official https homepage with certainty.
- The publisher is a real organization you can identify, and their role
  for this resource is clear: they operate it, or they are the
  originating authority for its content.
- The resource is usable by a researcher as a source of evidence or
  data: databases, archives, registries, official statistics,
  documentation, standards, search systems, and the like.
- You can fill every required field factually, including honest
  "unknown" values where the schema allows them.

Never invent or guess URLs. A homepage you remember but have not
confirmed is a guess. If the sandbox cannot reach a host, you may still
use a famous documented URL when the domain is unambiguous and widely
recorded, but say so in the provenance note; if you are not certain of
the domain at all, skip the candidate.

## Judging fit

- Ask what the resource is, not who hosts it. A statistical database
  run by a ministry belongs in government-statistics, not in a category
  suggested by the ministry's other activities.
- Prefer the more specific key when two keys both fit. International
  organizations that primarily publish development data belong in
  international-organizations; a treaty-body database belongs in
  international-relations-policy or law-regulation by what it contains.
- When the resource genuinely spans two categories, pick the one that
  matches its primary content and say so in the subcategory.
- Do not stretch a category to fill a quota. A batch with a lopsided
  category distribution is fine; a miscategorized record is a defect
  that survives into the shipped catalog.

## Choosing between close categories

- government-statistics is for official statistical outputs of
  government bodies; economics-finance is for monetary, fiscal, and
  market data, including central banks and financial regulators.
- preprint-repositories holds preprint servers; institutional-repositories
  holds university and funder repositories; journals-open-access holds
  journals and publishing platforms.
- security-advisories is for vulnerability and advisory feeds; patents-ip
  is for patent and trademark databases; standards-specifications is for
  standards bodies and their specification catalogs.
- When two categories still look equal after this, read the neighboring
  records in both categories in data/resources/ and pick the key whose
  existing subcategories match your candidate's shape.

## Subcategory conventions

- subcategory is free text, at most 80 characters, and optional.
- Reuse existing wording from the same category whenever one fits, for
  example "national statistical office" in government-statistics or
  "un system data" in international-organizations. Consistent
  subcategories are what make the catalog browsable.
- Lowercase plain words are the norm. Do not repeat the category label
  as the subcategory.

## Skipping candidates

Skipping is a correct outcome. Record every skip in the run report with
one of these reasons: duplicate (already cataloged), uncertain (URL,
publisher, or existence not certain), out of scope (not researcher
usable), or unreachable (host could not be confirmed). A skipped
candidate that later becomes verifiable can be picked up in a later
run.

See references/dedupe-and-collisions.md for how duplicate candidates
are detected, and references/description-quality.md once a candidate
has cleared the standard and needs its free-text fields written.
