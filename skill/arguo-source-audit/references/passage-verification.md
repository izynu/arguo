# Passage verification

For every fetchable source the audit answers one question: does this page,
as fetched today, support the claim as written? The answer is one of four
verdicts, each backed by a quoted passage and a locator. Judging the claim
as written is the hard part: the audit tests what the document says, not
the friendliest version of it.

## The four verdicts

- supports
  The page states the claim at matching strength and scope: same fact, same
  numbers, same period, same geography, same population, and the same
  causal or correlational wording.

- partially supports
  The page states a weaker, narrower, or adjacent version of the claim. The
  substance overlaps but the claim outruns the page: a dropped hedge,
  a wider period, a different denominator, "suggests" turned into "shows".

- contradicts
  The page states the opposite, a materially different figure, or explicitly
  denies what the document asserts. A different number of the same size is
  a contradiction when it changes what the claim means.

- not found on page
  An honest search of the fetched text did not surface the claim or a clear
  neighbor of it. This is a finding, not a failure of effort, and it has
  several possible causes you should name rather than guess at: the page
  changed since citation, the citation is decorative, the URL was wrong
  from the start, or the content sits behind an element the fetch did not
  capture.

## Procedure

1. Restate the claim's testable parts: the fact asserted, any numbers with
   their units and periods, the scope words (all, most, some, in country X,
   since year Y), and the causal language.
2. Search the fetched text for each part. Use the page's own headings and
   wording as search anchors, not only the document's phrasing.
3. Quote the best passage verbatim, with a locator: heading, section, or
   paragraph. The quote is the evidence for the verdict; a verdict with no
   quote is an assertion.
4. If the document quoted a passage, compare it against the live text.
   Word-level differences are quote drift; record them even when small.
5. Assign the verdict. When torn between two verdicts, take the lower one
   and explain in one line why the higher one was not earned.

## Claim strength versus source strength

The common failure mode is a claim that outruns its source:

- Hedges dropped: "may contribute" becomes "drives".
- Correlation promoted to cause.
- A number whose reference period, geography, or population shifted.
- Superlatives and totals the source never states.
- A specific figure attributed to a source that gives only a range.

When the gap is a matter of scope words alone and the substance holds with
a one-word correction, that can still be partially supports; the note must
say exactly which correction the document needs.

## Edge cases

- Landing pages and press releases: if the claim is really about a study
  and the cited page only describes it, verify the description against the
  claim and note that the study itself is one step away. That step is
  misattribution work, covered in the misattribution reference.
- Data in a linked file: if the number may live in a PDF or dataset the
  page links to, and you did not fetch that file, the verdict is not found
  on page with a note naming the likely location. Do not speculate about
  what the file contains.
- Gated or partial content: verify only against what you actually received.
  A headline that matches the claim is a headline, not the article.
- Long pages: state your search coverage honestly in the per-citation
  block. If you searched headings and full text, say so; if only a partial
  fetch was captured, the verdict says so too.
- Non-English pages: quote in the original language and add your
  translation, marked as a translation.

## Recording

Per citation: verdict, the verbatim quote, the locator, and a one-line
rationale that a reviewer can check against the quote. Unknown stays
unknown: "not found on page" is a complete, honest row.
