# Publication dates and recency

Dates are metadata people get wrong most often, because four different things
are called "the date" and they answer different questions. Using the wrong one
makes evidence look fresher or older than it is.

## The four date kinds

- Publication date: when the document was first made public. Answers "how old
  is this document".
- Event date: when the thing the document describes happened. Answers "when
  did this occur". A 2025 report can describe a 2019 event.
- Observation period: the span over which data was collected. Answers "what
  does the data cover". An annual survey published in 2025 may observe 2024,
  with a fieldwork window of months inside that year.
- Update date: when the document or record was last revised. Answers "has
  this changed since publication". A continuously updated page can have a
  publication date years old and an update date of yesterday.

A single source can carry all four, and they can differ by years. The report
should name the one it means: "published 2023, reporting 2022 data".

## Which date goes in which field

- Ledger field published_at holds the publication date, only when actually
  known.
- Observation periods belong in the passage or in a dedicated note, attached
  to the number they qualify.
- Update dates go in the limitations or notes when they change the reading,
  for example a revised statistic.

## Finding dates

- Look for an explicit date near the byline, in a citation block, or in the
  document's metadata fields. Explicit beats inferred.
- URL slugs, folder names, and copyright footers are weak signals; use them
  only as hints, never as recorded values.
- Page metadata tags can carry publication and update times; they are
  stronger than visual layout but still occasionally wrong.
- Web archives can date a page by earliest snapshot when no date is shown;
  record that you used an archive-derived lower bound, not an exact date.
- If the date is genuinely unknown, record unknown. Do not fabricate.

## Recency judgments

Recency is a property of the match between evidence and question, not of the
page alone:

- Fast-moving questions (current prices, software versions, officeholders):
  evidence must be from the observation window the question asks about.
  State the as-of date of the report.
- Slow-moving questions (history, mathematics, physical constants): an old
  publication date is fine; what matters is whether later findings superseded
  it. Check for corrections, retractions, and newer editions.
- Statistical questions: the observation period and the revision status
  matter more than the page date. Provisional figures get revised.

## Time-boundary discipline

- If the question sets a boundary ("as of March 2024"), evidence from outside
  the boundary is context, not the answer. Label it as such.
- If no boundary is set, state the as-of date of your answer and note that
  the state may have changed since.
- When a newer source contradicts an older one on a moving topic, that is
  usually a temporal difference, not an error by either party. Classify it in
  references/contradiction-analysis.md terms.

## Checklist

- [ ] Publication date recorded or unknown, never guessed.
- [ ] Event date and observation period identified for data-bearing passages.
- [ ] Update or revision status checked for pages likely to change.
- [ ] As-of date of the report's answers stated.
- [ ] Supersession checked for old load-bearing sources: corrections,
      retractions, later editions.
