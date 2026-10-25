# Quantitative research

Numbers carry more failure modes than any other claim type, because a number
can be copied correctly and still be wrong for the purpose: wrong unit, wrong
period, wrong denominator, wrong vintage. Every quantitative claim gets the
full capture below.

## Capture the six attributes

For every number that enters the ledger:

1. Value as stated, unrounded from the source.
2. Unit, including scale words: thousands, millions, percentage points,
   currency, per-capita.
3. Denominator or base: percentage of what, change relative to what.
4. Reference period: calendar year, fiscal year, rolling quarter, point-in-time
   date.
5. Geography and population: country, region, age range, sector, inclusion
   rules.
6. Revision status: provisional, revised, final, and the vintage date.

A number missing three of these six is not yet evidence; it is a fragment.
Either complete it from the source or mark the row limited.

## Percentages and changes

- Percentage versus percentage points: a move from 4 to 5 percent is one
  point, or a 25 percent increase. Reports that blur this mislead.
- Every percentage needs its base stated in the report, not just the ledger.
- Growth rates need their period: annual, quarterly, annualized, cumulative.
- Small bases inflate percentages; state absolute counts alongside.

## Revisions and vintages

- Statistical agencies revise. Provisional figures differ from final ones,
  sometimes materially. Record the vintage: which release of the series you
  used.
- When two sources disagree on a macro figure, check vintage before treating
  it as a contradiction; it may be the same series at different revisions.
  See references/contradiction-analysis.md.
- Prefer the originating agency's series over re-publications; the agency
  carries the revision history and the methodology.

## Units, currency, and inflation

- Nominal versus real: state whether values are inflation-adjusted and by
  which index and base year.
- Currency conversions need a date and a rate source. Fiscal years differ
  across countries and companies; never assume calendar alignment.
- Unit systems: convert deliberately, once, and state the target unit. Do not
  mix units inside one comparison.

## Precision discipline

- Do not invent precision: a source saying "about 1.2 million" cannot be
  reported as 1,200,000 exactly.
- Keep the source's significant figures unless the report's purpose requires
  rounding, and round once, at presentation.
- Derived numbers: show the arithmetic or the formula in the report or a
  footnote, so a reader can recompute.

## Cross-checks

- Find one independent series or source for load-bearing numbers. Independent
  means a different origin, not a different website reporting the same origin.
- Sanity-check magnitudes against known anchors where they exist.
- For sums and shares, check internal consistency: parts sum to the stated
  whole; shares sum to 100 percent within rounding.

## Checklist per quantitative claim

- [ ] All six attributes captured or explicitly unknown.
- [ ] Percentage bases and change periods stated in the report.
- [ ] Vintage and revision status recorded.
- [ ] Units, currency, and inflation treatment consistent across the report.
- [ ] At least one independent cross-check, or its absence noted in
      limitations.
- [ ] No invented precision anywhere.
