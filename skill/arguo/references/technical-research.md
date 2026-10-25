# Technical research

Technical questions have a specific authority order, and most technical
misinformation comes from answering from the wrong layer: a forum answer
cited where the specification was needed.

## Authority order

1. Official documentation and specifications from the vendor or standards
   body: product docs, API references, RFCs, formal standards.
2. Source code and changelogs: the repository, release notes, commit history.
   Code is the ground truth for behavior when docs and code disagree.
3. Registry metadata: package registries, advisory databases, version
   listings.
4. Conference talks and engineering blogs: useful for rationale and history;
   not authoritative for current behavior.
5. Q and A sites and forums: leads for debugging, never citations for
   behavior claims. Trace anything useful back to documentation or code.

## Version discipline

- Behavior is version-specific. Record the exact version, release, or commit
  under discussion. "The library returns X" is meaningless without it.
- Pin versions when reproducing behavior: package version, runtime version,
  and relevant configuration.
- Check the deprecation and support lifecycle: a documented behavior may be
  scheduled for removal; an advisory may be superseded.

## Primary technical artifacts

- Standards: cite by document number and section, for example an RFC by its
  number, a standard by edition and clause.
- APIs: cite the endpoint reference and, where possible, the observed
  response you actually captured.
- Code: cite the repository, tag or commit, and the file path. A line link
  that can rot should be paired with the tag or commit reference.
- Release notes and changelogs: primary sources for what changed when.
  Cite the release entry, not a summary of it.

## Benchmarks and performance claims

- A benchmark claim without its methodology is marketing, not evidence:
  hardware, versions, dataset, measurement procedure, and who ran it all
  matter.
- Vendor benchmarks favor vendor products. Note the conflict of interest and
  look for independent replications before carrying the number.
- Reproduce when feasible: run the benchmark or the behavior yourself and
  record the environment. Your own run is a primary observation, and belongs
  in the ledger with its conditions.

## Behavioral verification

- When feasible, verify behavior by running it: a minimal script against the
  documented interface settles more than five blog posts.
- Record what you ran, the environment, and the observed output. Distinguish
  "the documentation says" from "the observed behavior was" in the report.
- Where verification is impossible, mark the claim as documentation-based
  and note it.

## Security advisories

- Prefer the advisory databases and the vendor's own notices over summaries.
- Record identifiers (CVE-style IDs and vendor IDs), affected version ranges,
  and fixed versions as stated by the maintainer.
- Beware of aggregators that inflate or misstate affected ranges.

## Recording specifics

- For every technical ledger row: source URL, version or commit, and
  retrieved_at. Documentation pages change silently; the retrieval date and
  archived snapshot are what keep the citation meaningful.
- Distinguish documented behavior, observed behavior, and inferred behavior
  in the claim text itself, not just in limitations.

## Checklist

- [ ] Authority layer identified for each technical claim.
- [ ] Version, release, or commit recorded.
- [ ] Changelog and deprecation status checked.
- [ ] Benchmarks carry methodology and interest disclosures.
- [ ] Behavior verified by execution where feasible, otherwise labeled.
- [ ] Forum-derived leads traced to primaries before use.
