# Citation standards

Citations are the audit trail of the report. A citation that cannot be
checked is decoration. This file defines what a complete citation contains
and the audit the report must pass before delivery.

## Anatomy of a citation

Every cited source in the source list carries:

- Author or issuing body, when known.
- Title of the document or page.
- Publisher or site name.
- Publication date, or "undated" when none is shown. Do not guess.
- Direct URL to the page or document actually consulted.
- Retrieval date, because content changes and links die.
- Optional but valuable: version, section, page, table number, identifier
  (DOI, statute number, filing identifier), and an archived copy reference
  when one exists.

## Claim-level rules

- Every factual claim in the report carries at least one source ID. Claims
  synthesized from several sources cite all of them.
- Quoted text appears verbatim, in quotation marks, with the locator.
- Paraphrase is the default for prose; it must stay within what the passage
  supports. When in doubt, quote.
- A claim supported only by one source, or only by sources in one
  independence group, is labeled as such in the claim-evidence table.
- Numerical claims cite the origin of the number, not the most convenient
  repetition of it.

## URL hygiene

- Cite the canonical URL: the origin's own address, not a redirector, a
  tracking-parameter link, or an aggregator frame.
- Strip tracking parameters before recording.
- For volatile pages, record an archived snapshot when available, and say in
  the report that an archived copy was used.
- If a URL was dead at retrieval time but content was reached through an
  archive, cite the archive URL as consulted and note the original.

## Fabrication is the cardinal failure

- Never cite a source you did not consult. Never invent a plausible-looking
  URL, DOI, title, date, or author. A missing citation is a gap; an invented
  one is a failure that contaminates everything downstream.
- If you cannot reconstruct a citation, say so and mark the claim
  insufficiently supported. Honesty is the recovery path; fabrication is not.
- Verify that quoted passage and cited URL agree before delivery.

## Pre-delivery audit

Run this checklist on the finished report:

- [ ] Every claim has at least one citation, or is explicitly marked as
      unverified.
- [ ] Every cited source was actually opened and read, at least in the
      relevant part.
- [ ] Every source in the source list is cited by at least one claim. Remove
      unused sources or use them.
- [ ] Every URL is well formed and was reachable when consulted, or the
      archive path is recorded.
- [ ] Quotes match the recorded passages verbatim.
- [ ] Dates and metadata are present or explicitly unknown.
- [ ] No two cited sources are the same underlying document under different
      URLs.
- [ ] Load-bearing claims rest on primaries or independent corroboration, or
      say otherwise.

The repository's audit tooling reports issues of kinds such as missing-source,
unused-source, invalid-url, fabricated-citation, unsupported-claim,
duplicate-source, and missing-metadata; the checklist above is the manual
equivalent for runs that do not use the tooling.
