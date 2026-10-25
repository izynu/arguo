# Per-citation audit row

<!-- One block per citation. This block is the evidence behind one audit
table row: a reviewer should be able to re-run the check from it. Keep
fields in order; write unknown where the value is unknown, and never leave
a placeholder unfilled. -->

## Citation

- citation_id: {{C1}}
- Claim as written: {{CLAIM_VERBATIM_OR_TIGHT_PARAPHRASE}}
- Claim location: {{SECTION_PARAGRAPH_OR_PAGE}}
- Cited URL: {{URL}}
  <!-- if the document gives no URL: "no URL given; named source:
  {{NAMED_SOURCE}}" -->
- Citation form: {{INLINE_OR_FOOTNOTE_OR_BIBLIOGRAPHY_OR_BARE_ATTRIBUTION}}
- Passage the document quotes: {{QUOTED_PASSAGE_AND_LOCATOR_OR_NONE}}

## Fetch record

- Fetched at: {{TIMESTAMP}}
- Observed result: {{STATUS_CODE_OR_BEHAVIOR}}
  <!-- for example: HTTP 200, or "challenge page rendered", or
  "404 after one retry"; describe what you saw, not what you expect -->
- Final URL: {{FINAL_URL_OR_SAME}}
- Content observed: {{ONE_LINE_ON_WHAT_CAME_BACK}}
- Link class: {{LIVE_OR_BOT_BLOCKED_OR_DEAD_OR_REDIRECT_MOVED_OR_PAYWALLED_OR_DOMAIN_CHANGED_OR_UNREACHABLE}}

## Passage check

<!-- Skip this section only when the link class blocked it; then write
"not checkable: {{REASON}}" and go to the verdict. -->

- Passage found on page: {{VERBATIM_QUOTE_WITH_LOCATOR}}
  <!-- quote the page's text, not the document's paraphrase of it -->
- Passage verdict: {{SUPPORTS_OR_PARTIALLY_SUPPORTS_OR_CONTRADICTS_OR_NOT_FOUND_ON_PAGE}}
- Claim-strength gaps: {{DROPPED_HEDGES_SCOPE_SHIFTS_NUMBER_MISMATCHES_OR_NONE_OBSERVED}}
- Quote comparison (if the document quoted): {{MATCH_OR_DIFFERENCES_FOUND}}

## Dates

- Page date observed: {{PUBLICATION_DATE_OR_UPDATE_DATE_OR_UNKNOWN}}
- Document's stated access date, if any: {{VALUE_OR_NONE_STATED}}
- Date note: {{CONSISTENT_OR_MISMATCH_DESCRIPTION}}

## Re-grade summary

<!-- One line, ten criteria, vocabulary in references/audit-report-format.md -->

- {{AUTH}}; {{PRIMARY_SECONDARY}}; {{METH}}; {{REC}}; {{DIR}}; {{TRANS}};
  {{COI}}; {{CORR}}; lim: {{LIMITS_OR_NONE_STATED}}; prov: {{PROV}}
- Criterion driving the verdict, if any: {{CRITERION_AND_WHY}}

## Verdict

- Citation verdict: {{PASS_OR_PASS_WITH_NOTE_OR_ISSUE_OR_CANNOT_AUDIT}}
- Issue type (issue rows only):
  {{LINK_ROT_OR_PASSAGE_GAP_OR_CONTRADICTS_OR_MISATTRIBUTION_OR_DATE_PROBLEM_OR_QUALITY_BELOW_BAR}}
- Note for the table: {{ONE_LINE_NOTE}}
  <!-- the correction needed, the candidate correct source, or the
  blocking reason, in one line -->
