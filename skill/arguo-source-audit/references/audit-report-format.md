# Audit report format

The audit's deliverables are fixed: an audit table with one row per
citation, per-citation verdicts from a closed vocabulary, one overall
verdict, and a limitations section. Fixed formats are what make two audits
comparable and keep honesty from eroding under time pressure.

## Audit table columns

One row per citation, in document order:

| Column | Content |
|---|---|
| ID | The citation ID from the inventory (C1, C2, ...). |
| Claim (short) | The claim compressed to its testable core, strength intact. |
| Cited URL | The URL as cited, or "no URL" for bare attributions. |
| Link class | live, bot-blocked, dead, redirect-moved, paywalled, domain-changed, unreachable. |
| Passage verdict | supports, partially supports, contradicts, not found on page, not checkable. |
| Date note | The observed date facts, or "consistent", or "unknown". |
| Re-grade | The compact rubric summary line (format below). |
| Verdict | pass, pass-with-note, issue, cannot-audit. |
| Note | One line: the issue type, the key evidence, or the correction needed. |

"Not checkable" in the passage column is reserved for rows whose link
class blocked the check: bot-blocked, paywalled beyond the visible part,
dead, unreachable. It pairs with cannot-audit in the verdict column.

## Per-citation verdict vocabulary

- pass
  Link live, passage supports, dates consistent, and the re-grade holds up
  for the claim. The citation did its job.

- pass-with-note
  The citation works and the claim stands, with a minor recorded defect: a
  same-domain redirect, a paraphrase slightly looser than the page, a date
  ambiguity, a scope word needing correction. The note says the defect and
  the fix in one line.

- issue
  A material problem. The row names exactly one primary issue type:
  - link-rot: dead, unreachable, redirect-moved to a different document,
    or domain-changed with the document not findable at the new home.
  - passage-gap: partially supports or not found on page.
  - contradicts: the fetched page states otherwise.
  - misattribution: one of the patterns from the misattribution reference.
  - date-problem: a citation date the page does not support, or currency
    the claim needs and the observation period does not provide.
  - quality-below-bar: the re-grade falls short of what the claim requires,
    for example single-source for a load-bearing number.

- cannot-audit
  The check could not be performed: bot-blocked, paywalled past anything
  usable, dead with no auditable copy, unreachable, or no URL given and
  the source not identifiable. The row states the reason. A cannot-audit
  row is never upgraded to pass because other rows went well.

## Overall verdicts

Read the table, then pick exactly one:

- pass
  Every row is pass or pass-with-note. No issue rows, no cannot-audit rows.

- pass-with-issues
  Issue or cannot-audit rows exist, but every load-bearing claim still
  rests on at least one audited supporting citation, and the defects are
  correctable without re-research: a dead link with the document findable
  elsewhere, a scope correction, a secondary citation needing the primary
  attached. The assessment names the defects and the unaudited remainder.

- needs-rework
  One or more load-bearing claims rest solely on issue rows: contradicted,
  misattributed, dead with no replacement, or quality below what the claim
  requires. The document should be revised before it is relied on.

- cannot-audit
  The audit cannot reach a verdict at all because the load-bearing
  citations are bot-blocked, paywalled, or unreachable, or fetch coverage
  was too thin to judge the evidence base. Say precisely which citations
  blocked the audit and what access would unblock it.

Constraint: if any load-bearing citation is cannot-audit, the best possible
overall verdict is pass-with-issues, with the gap named in limitations.
cannot-audit overall is for when the blocked citations leave the evidence
base unjudgeable.

## The re-grade summary

One compact line per citation, using the ten-criterion rubric vocabulary:
authority, primary versus secondary, methodological quality, recency,
directness, transparency, conflicts of interest, independent corroboration,
limitations, and publisher provenance. Level vocabularies:

- authority: high, medium, low, unknown.
- primary/secondary: primary, secondary, tertiary, unknown.
- methodology: strong, adequate, weak, not applicable, unknown.
- recency: current, aging, outdated, unknown.
- directness: direct, indirect, inferred.
- transparency: documented, partial, opaque, unknown.
- conflicts of interest: none known, possible, declared, unknown.
- corroboration: independent, syndicated, single-source, unknown.
- limitations: the source's stated limits, or "none stated".
- provenance: checked, problem, unknown.

Summary line format: "auth: medium; prim: secondary; meth: n/a; rec:
current; dir: direct; trans: partial; coi: none known; corr: single-source;
lim: none stated; prov: checked".

The full criterion definitions live in the arguo skill's source quality
rubric at skill/arguo/references/source-quality.md. The vocabulary above is
sufficient to re-grade standalone; read the arguo reference when the
criteria themselves need interpretation.

## Counts and limitations

- Counts: citations found, fetched, not fetchable (by class), and verdicts
  (pass, pass-with-note, issue, cannot-audit). The counts and the verdict
  must agree with the table.
- Limitations section, mandatory: sources that could not be fetched and
  why; anything out of scope; the fetch method and its constraints; what
  a later audit should re-check. Write "none observed" only when true.

## Honesty rules for the report

- No cell without evidence behind it, or the word unknown.
- No verdict implied by tone: a blocked link is a blocked link, not
  "appears reliable".
- Examples inside reports are labeled illustrative; nothing from a
  walkthrough is quoted as an observed result.
