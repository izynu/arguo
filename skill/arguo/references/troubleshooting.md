# Troubleshooting

Symptoms, causes, and fixes for the failure modes that recur in
arguo runs. When a fix works, log it; recurring issues on one topic
usually mean the search strategy needs redesign, not more retries.

## Zero useful results

- Causes: query too narrow, wrong vocabulary, the material is not on the open
  web, or the framing is off.
- Fixes: rewrite with specialist vocabulary; drop quote marks; search
  institution and agency sites directly; consult the repo catalog at
  data/resources/ for a category that maps to the question; try the original
  language of the topic.
- After a genuine effort with no results, that is a finding: record the
  queries tried and move the subquestion toward insufficient-evidence.

## Too many irrelevant or duplicated results

- Causes: syndication, content farms, and SEO pages crowding out primaries.
- Fixes: add the origin's likely domains with site targeting; exclude known
  aggregator patterns; sort by date sparingly (recency bias hides stable
  primaries); move to registries and archives instead of the general web.

## Paywalled or removed sources

- Fixes: check whether an archived snapshot exists; check whether the
  publisher offers the document elsewhere openly (repositories, preprint
  servers, official copies); check for an official mirror.
- Never bypass the paywall. Record source-unavailable or use the legitimately
  accessible version; note the limitation.

## Dead links

- Fixes: search the exact title; look in web archives; find the document in
  an institutional repository.
- Record the original URL plus the archive URL used, per
  references/citation-standards.md.

## Numbers that will not reconcile

- Causes: different definitions, different periods, different vintages,
  transcription errors, or one side is wrong.
- Fixes: normalize units, currency, and base years first; check vintage and
  revision status; read the primaries' own qualifications; then classify per
  references/contradiction-analysis.md.
- If still unreconciled, the contradiction table carries both values and the
  report says so. Do not average across definitions.

## Suspected fabricated citation

- If a citation cannot be verified (no page, no record, no registry entry),
  treat it as fabricated until shown otherwise: remove the citation, mark the
  claim insufficiently supported, and record the check in the run notes.
- Self-check your own draft the same way: every URL and identifier must have
  been produced by a real retrieval during the run, never reconstructed from
  memory.

## Circular reporting

- Symptom: many sources, one origin. A claim repeated across outlets, all
  tracing to one press release or one newsroom.
- Fix: trace to the earliest or originating text, treat the rest as one
  source, and seek genuinely independent confirmation. Until then the claim
  stays single-source in the ledger.

## Poor-quality scans and OCR text

- Symptom: garbled text, impossible numbers, broken tables.
- Fixes: prefer facsimile views over extracted text; cross-read numbers
  against the tables or images; mark rows limited where the text layer is
  unreliable.

## Non-English material

- Fixes: search in the original language; machine-translate for reading and
  mark every translated passage as such; for load-bearing quotes, verify
  wording against the original or a second translation.

## Budget exhaustion

- Fixes: none that extend the budget. Deliver: the claim-evidence table with
  current statuses, the limitations naming what was not covered, and the
  proposed next searches. examples/example-insufficient-evidence.md shows the
  shape of an honest partial report.

## When to stop

- Stop when saturation is reached, the budget is gone, safety rules require
  narrowing, or remaining gaps need materials an agent cannot access. Stopping
  with an accurate insufficiency verdict is a completed run, not a failed one.
