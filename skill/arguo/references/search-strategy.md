# Search strategy

Search is iterative and logged. The goal is not to find any source that
agrees with a tentative answer; it is to find the strongest sources that bear
on the question, including the ones that disagree.

## Query design

- Build queries from entities, not vibes: names of organizations, laws, programs, products, places.
- For each subquestion write at least three formulations: lay phrasing,
  specialist phrasing, and a quoted exact phrase likely to appear in primary
  documents.
- Include vocabulary variation: synonyms, abbreviations, British and American
  spellings, and translations when the topic is not English-first.
- Use exclusion terms to cut noise, for example adding a year to exclude
  out-of-scope eras, or a jurisdiction name to exclude other regions.

## Operators and targeting

- Use site: targeting on likely primary domains once you know them, for
  example a statistics agency, a legislature, a company's investor-relations
  host.
- Use file type targeting where useful: PDFs often hold reports, filings, and
  working papers that never appear as web pages.
- Search within a domain's own site search when it exists; site search often
  reaches material external engines rank poorly.

## Search rounds

- Round 1, exploratory: broad formulations to learn the vocabulary of the
  topic, who publishes on it, and what the obvious sources are.
- Round 2, targeted: queries aimed at specific primary sources identified in
  round 1, plus site-restricted queries.
- Round 3, verification: queries written to disprove the emerging answer, to
  find contradicting values, and to check whether better primaries exist.

Every query and its outcome goes into the run log. An auditor should be able
to repeat the search trail.

## Catalog consultation

The repo ships a curated catalog at data/resources/, categorized by the keys
in data/categories.json. When a subquestion maps to a category, for example
government-statistics or law-regulation, consult the catalog on demand and try
the listed resources before falling back to general web search. The catalog is
a starting-point index, not evidence; sources found through it still go through
the same quality rubric.

## Syndication awareness

Early rounds often return the same underlying text at many domains: wire
stories, press-release reposts, scraped aggregators. Treat repeated identical
or near-identical text as one source. Note the earliest or the originating
publisher and move on.

## Non-English and multilingual topics

- Search in the original language of the primary material; machine-translated
  queries miss locally phrased sources.
- Names transliterate: record the original-script name in the ledger so the
  trail is repeatable.
- Machine-translate retrieved passages, and note in the ledger row that the
  passage was translated and by what means.

## Saturation and stopping

- Stop a subquestion when two consecutive rounds add no new load-bearing
  evidence, only rephrasing.
- Also stop when you have reached the budget set in the plan, and say so in
  the report limitations.

## Common mistakes

- Searching only for confirmation of the first plausible answer found.
- Treating a paywalled snippet as having read the source.
- Staying on general web search when a registry, archive, or agency holds the
  primary.
- Logging queries nowhere, which makes the search unauditable.
- Ignoring non-English sources because the question was asked in English.
