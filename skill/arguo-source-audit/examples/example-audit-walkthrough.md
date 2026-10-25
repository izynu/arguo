# Example: auditing a short cited report

> Illustrative example with representative domains, not a live run. The
> document under audit, the fetch results, the quotes, and the dates below
> were written to teach the method and its report format. Nothing in this
> file was observed during an actual audit, and the citations point to
> organizations' sites at domain level rather than to specific pages.
> Do not quote this file as evidence for anything.

## The document under audit

A fictional two-page brief, "Community solar: three facts for the council
meeting", carries three citations. Its relevant excerpt:

"Utility-scale solar costs have fallen by roughly 80 percent since 2010,
and the shift is now driven by economics rather than subsidy [1]. As the
World Bank put it, distributed renewables are now the cheapest source of
new electricity for most of the world [2]. Industry bodies project that
community programs will double installed capacity by 2030 [3]."

## Step 1: inventory

| ID | Claim as written | Cited URL | Quoted passage in document |
|----|------------------|-----------|----------------------------|
| C1 | Utility-scale solar costs fell roughly 80 percent since 2010; the shift is now driven by economics rather than subsidy | https://www.iea.org/ | none (paraphrase) |
| C2 | The World Bank said distributed renewables are now the cheapest source of new electricity for most of the world | https://www.worldbank.org/ | the quoted sentence above |
| C3 | Industry bodies project community programs will double installed capacity by 2030 | https://www.irena.org/ | none (paraphrase) |

Note on the inventory: each claim takes one citation, so no cluster
splitting is needed. All three are bare organizational homepages, which
is itself worth a flag later.

## Step 2: link classification (illustrative fetch results)

- C1: HTTP 200 at the cited URL, no redirect, expected organization site
  returned. Class: live.
- C2: HTTP 301 followed to a locale-prefixed variant of the same
  homepage. Class: live would fit a same-document redirect; here the
  audit records live with the final URL in the note, since the document
  is unchanged. (If the redirect had landed on a different document, the
  class would be redirect-moved.)
- C3: the fetch returned a scripted challenge page with no article
  content after one retry. Class: bot-blocked.

## Step 3: passage verification

- C1: the fetched homepage text (illustrative) states a large cost
  decline for solar over the 2010s but over the period 2010 to 2022 and
  without the "roughly 80 percent" figure. Verdict: partially supports.
  Gap: the document's period and magnitude are tighter than the page's.
- C2: the quote was not found anywhere in the fetched text. The homepage
  is a landing page; the sentence is the kind that lives in a specific
  report or press release. Verdict: not found on page, with the
  misattribution question escalated to step 4.
- C3: not checkable. The link class blocked any passage work.

## Step 4: misattribution

- C1: no pattern observed; the page is a plausible holder for a general
  cost-trend claim, though a specific report would be the right citation.
- C2: matches the "landing page cited for a data point" pattern: a
  specific attributed quote cited to an organization's root URL. The
  candidate correct source (a specific report page) was not identified in
  this audit's trace budget of one step, and is recorded as a candidate,
  not a fact.
- C3: not checkable.

## Step 5: dates

- C1: page shows a recent update line; the claim's "since 2010" period is
  consistent with the page's stated series. Note: consistent.
- C2: homepage carries no publication date (normal for a landing page);
  the document's citation carries no date either. Note: unknown, and the
  quote's provenance is unverified.
- C3: no date observable; audit timestamp recorded. Note: unknown.

## Step 6: re-grade summaries (illustrative)

- C1: auth: high; prim: secondary; meth: n/a; rec: current; dir: direct;
  trans: partial; coi: none known; corr: single-source; lim: none stated;
  prov: checked.
- C2: auth: high; prim: unknown; meth: unknown; rec: unknown; dir:
  indirect; trans: opaque; coi: none known; corr: single-source; lim:
  none stated; prov: checked. The unknowns trace to the quote being
  unverifiable at the cited page.
- C3: not gradable; the source could not be fetched, and no criterion is
  recorded beyond provenance: unknown.

## Step 7: audit table

| ID | Claim (short) | Cited URL | Link class | Passage verdict | Date note | Re-grade | Verdict | Note |
|----|---------------|-----------|------------|-----------------|-----------|----------|---------|------|
| C1 | solar costs down about 80 percent since 2010, economics-driven | https://www.iea.org/ | live | partially supports | consistent | auth: high; prim: secondary; meth: n/a; rec: current; dir: direct; trans: partial; coi: none known; corr: single-source; lim: none stated; prov: checked | pass-with-note | page states the trend with a wider period; tighten the figure or cite the specific report |
| C2 | World Bank: distributed renewables cheapest new power for most of the world | https://www.worldbank.org/ | live | not found on page | unknown | auth: high; prim: unknown; meth: unknown; rec: unknown; dir: indirect; trans: opaque; coi: none known; corr: single-source; lim: none stated; prov: checked | issue | misattribution: quote cited to a landing page; find the specific report and cite it |
| C3 | community programs to double capacity by 2030 | https://www.irena.org/ | bot-blocked | not checkable | unknown | not gradable; prov: unknown | cannot-audit | automated access blocked; no verdict possible this run |

## Step 8: overall assessment

- Counts: 3 citations found; 2 fetched; 1 not fetchable (bot-blocked).
  Verdicts: 0 pass, 1 pass-with-note, 1 issue, 1 cannot-audit.
- Overall verdict: pass-with-issues.
- Assessment: the one fully auditable claim (C1) holds in substance with a
  period correction, so the brief's central fact is intact but needs its
  figure tightened and a specific report cited. C2 is a real defect: a
  verbatim quote is attributed through a homepage and cannot be verified
  as written; the fix is to locate and cite the actual report, and the
  verdict would rise to needs-rework if the quote turned out to be wrong
  rather than merely misplaced. C3 could not be checked at all; it is a
  secondary projection, so the audit can still describe what was verified,
  but the brief is not fully certified. Re-running the audit with access
  to the blocked source, or with an archive copy of the cited page, would
  close the remaining gap.

## Limitations

- C3 could not be fetched (bot-blocked after one retry); no verdict on its
  claim, and no inference drawn from the block.
- C2's trace stopped at one step without identifying the original report;
  the candidate source is unverified.
- Homepage-level citations limit what any audit can confirm; the report
  should cite specific documents.
- All fetch results in this example are illustrative and were not
  observed in a live run.
