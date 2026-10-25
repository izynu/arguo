# Report writing

The report is the deliverable, and it is read by people who did not see the
search. Its job: state the answer, show the evidence, expose the
disagreements, name the gaps, and let a reader retrace every step.

## Structure

1. Question and scope: the question as understood, the interpretation used,
   and the as-of date.
2. Bottom line: the answer in a few sentences, with overall confidence.
   Nothing in the bottom line may exceed what the findings support.
3. Claim-evidence table: one row per claim.
4. Findings: organized by subquestion, prose with citations, distinguishing
   established facts from interpretation.
5. Contradictions: what conflicted, how it was classified, what was
   resolved and how.
6. Limitations: concrete gaps and what would settle them.
7. Source list: full citations with URLs and retrieval dates.
8. Appendix: search log summary and ledger references when the run should be
   auditable end to end.

## The claim-evidence table

Columns: claim ID, claim text, source IDs, relation (supports, contradicts,
context), verification status, confidence with one-line reason. This table is
the contract between the report and the ledger: every row must map to ledger
rows that exist.

## Prose rules

- Separate fact from interpretation, at the sentence level. "Reported X" and
  "this implies Y" do not share a sentence.
- Hedge to the evidence: hedges from the sources stay in ("the study found
  an association, not a cause"); hedges reflect your evidence, not your
  comfort.
- Numbers follow references/quantitative-research.md: bases stated, units
  consistent, precision preserved or rounded once.
- Every factual sentence carries its citation. Interpretation sentences name
  the claims they rest on.

## Tone and house style

- Plain, factual, unimpressed. The evidence makes the report strong; language
  should not try to.
- No hype, no advocacy, no rhetorical certainty, no emoji, and no em or en
  dashes: use hyphens, colons, and commas. This is a standing style rule of
  this project.
- Do not editorialize in findings. If a judgment is needed, put it in a
  clearly labeled interpretation paragraph and show the claims it rests on.

## Summaries

- The bottom line is written last, after the findings are final, and checked
  against the claim-evidence table row by row.
- Confidence in the summary matches the confidence in the findings. A summary
  that quietly upgrades "moderate" to "confirmed" is the most common quality
  failure in cited reports.

## Pre-delivery checklist

- [ ] Question, interpretation, and as-of date stated.
- [ ] Bottom line matches findings, no upgrade in confidence.
- [ ] Claim-evidence table complete: every claim has a status and a reason.
- [ ] Every factual sentence cited; quotes verbatim and located.
- [ ] Contradictions section present when any conflict was found.
- [ ] Limitations concrete, with what would settle each gap.
- [ ] Source list complete: title, publisher, date, URL, retrieval date.
- [ ] Citation audit from references/citation-standards.md passed.
- [ ] Style: no em or en dashes, no emoji, no hype language.

## Anti-patterns

- The confident summary over thin findings.
- The limitation-free report; every run has limits, and a report that cannot
  name one has not looked.
- The single-source report dressed as a survey of the field.
- The citation that leads nowhere: decorative citations are worse than none,
  because they borrow credibility they did not earn.
