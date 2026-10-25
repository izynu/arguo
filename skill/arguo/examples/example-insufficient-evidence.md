# Example: insufficient evidence, handled honestly

> Illustrative example with representative sources, not a live run. The city,
> figures, and dates are constructed for teaching the method, and no URLs are
> cited because none were consulted. This file shows what an honest
> insufficiency verdict looks like, not how to research a real budget.

## Question

"What percentage of the city of Rivermont's 2024 municipal budget was
allocated to road maintenance?"

## Why this question is likely to end in insufficiency

Municipal budget documents exist for most cities, but the phrase "road
maintenance" rarely matches a budget line exactly. Questions like this one are
where padding happens: an agent finds a roads-adjacent number and quietly
presents it as the answer. The method forbids that, and this example shows
the honest alternative.

## Plan

- Claim type: fact with a definitional hazard.
- Scope: city of Rivermont (fictional), fiscal year 2024, in local currency.
- Subquestions:
  - SQ1: What does Rivermont's adopted 2024 budget list under road
    maintenance or equivalent lines?
  - SQ2: What was total 2024 budgeted expenditure?
  - SQ3: How does the city define the road maintenance line (resurfacing
    only, or including sweeping, lighting, drainage)?
- Evidence requirement: the adopted budget document itself, with both
  numerator and denominator visible and the definition stated.
- Stopping rule: budget, five search rounds.

## What the searches found

Queries tried (illustrative log, summarized):

1. "Rivermont" 2024 budget road maintenance: news coverage of the budget
   adoption, which mentions "roads spending" once, without figures.
2. site-restricted search on the city's domain: a 2024 budget in brief PDF
   with total expenditure but no road maintenance line.
3. "Rivermont" public works budget PDF: a 2023 document, not 2024.
4. Verification queries for any figure attributed to "road maintenance" in
   2024: one local news story attributes "about 8 percent" to an unnamed
   official in a paragraph about potholes.

## What could not be established

- SQ1: The line-item breakdown for 2024 was not found in any accessible
  public document. The "budget in brief" omits departmental detail. The
  story's "about 8 percent" is an oral attribution with no document behind
  it, and no published denominator.
- SQ2: Total 2024 budgeted expenditure: found in the budget in brief,
  which is sufficient for the denominator alone.
- SQ3: The definition of the road maintenance line: not established. Without
  SQ3, even a found numerator could not be matched to the question's words.

## Why the tempting shortcut is wrong

The "about 8 percent" figure is exactly the kind of number that gets reported
when a run is tired of searching. It fails the method: unattributed, no
document, no denominator, not traceable to the adopted budget. Carrying it
with a hedge would still launder it into the report. The correct handling is
a status of insufficient-evidence for the headline claim, with the 8 percent
recorded in the ledger as context only.

## The report, as delivered

### Report: Rivermont 2024 road maintenance share

- As-of date: the run date (illustrative).

**Bottom line.** This could not be established from accessible public
documents. The adopted 2024 budget's line-item breakdown was not found; the
only circulating figure is an unattributed "about 8 percent" in local press
coverage, which cannot be verified against the budget document. Confidence:
insufficient. Reasons: the primary document was not reachable in its detailed
form, and the sole secondary figure fails attribution and denominator checks.

**Claim-evidence table.**

| Claim ID | Claim text | Source IDs | Relation | Status | Confidence and reason |
|----------|------------|------------|----------|--------|-----------------------|
| CL1 | Road maintenance was X percent of Rivermont's 2024 budget. | none | (no evidence found) | insufficient-evidence | insufficient: primary line-item document not located |
| CL2 | Total 2024 budgeted expenditure was T (as stated in the budget in brief). | S1 | supports | supported | moderate: single primary source, denominator only |
| CL3 | An unnamed official said road maintenance is "about 8 percent" of the 2024 budget. | S2 | context | partially-supported | low: oral attribution in press, no document, no denominator |

**Contradictions.** None found, because no competing documented figures
exist. The absence of documented figures is itself recorded as the central
limitation.

**Limitations.**

- The 2024 line-item budget was not accessible; the published "budget in
  brief" omits departmental detail. What would settle it: the adopted
  budget's expenditure appendix, or the finance department's detail tables.
- The "about 8 percent" figure has no published source and no denominator.
  What would settle it: the same line-item document, with the road
  maintenance definition.
- The city's definition of the road maintenance line was not established,
  so even a found numerator would need its definition checked before
  matching the question.

**Proposed next searches.**

- Contact or check the city finance department's document library for the
  adopted 2024 budget appendix.
- Check the city council minutes from the budget adoption session, which may
  attach the full expenditure schedule.
- Check the 2024 audited annual financial statement when published; actuals
  may be broken out by function.
- If the question allows, restate it against 2023, for which a public works
  budget document was found.

**Sources.** S1: Rivermont 2024 budget in brief (city publication, retrieved
during the run, illustrative). S2: local press story (illustrative, cited as
context only). No URLs are listed because this example is fictional.

## What this example teaches

- Insufficient evidence is a completed run, not a failed one, when the
  searches and the gap are documented.
- Context rows with low statuses are allowed in the ledger; they are not
  allowed to become the headline.
- Naming what would settle the question is part of the deliverable: it turns
  a dead end into a next step the requester can act on.
