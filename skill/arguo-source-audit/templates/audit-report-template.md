# Citation audit report

<!-- Fill one report per audit. Keep the bracketed comments during drafting
and delete them before delivery. Every placeholder must be filled or the
sentence rewritten to say what is actually known. Column definitions,
verdict vocabularies, and overall verdict rules are in
references/audit-report-format.md. -->

- Document audited: {{DOCUMENT_TITLE_AND_LOCATION}}
- Document date, if stated: {{DOCUMENT_DATE_OR_UNKNOWN}}
- Audit requested scope: {{SCOPE}}
  <!-- all citations, a named section, bibliography only, a subset by ID -->
- Audit date: {{AUDIT_DATE}}
- Auditor: {{AGENT_NAME_AND_FETCH_METHOD}}
  <!-- name the agent and the fetch mechanism used for every link -->

## Fetch coverage

- Citations found in scope: {{N_CITATIONS}}
- Fetched during this audit: {{N_FETCHED}}
- Not fetchable: {{N_NOT_FETCHABLE}}
  <!-- bot-blocked {{N_BOT_BLOCKED}}, paywalled {{N_PAYWALLED}},
  dead {{N_DEAD}}, unreachable {{N_UNREACHABLE}}, no URL {{N_NO_URL}} -->
- Fetch window: {{FETCH_WINDOW_START}} to {{FETCH_WINDOW_END}}

## Audit table

<!-- One row per citation, in document order. A cell with no evidence
behind it is written unknown. Do not remove columns. -->

| ID | Claim (short) | Cited URL | Link class | Passage verdict | Date note | Re-grade | Verdict | Note |
|----|---------------|-----------|------------|-----------------|-----------|----------|---------|------|
| {{C1}} | {{CLAIM_SHORT}} | {{URL_OR_NO_URL}} | {{LINK_CLASS}} | {{PASSAGE_VERDICT}} | {{DATE_NOTE}} | {{REGRADE_SUMMARY}} | {{CITATION_VERDICT}} | {{ONE_LINE_NOTE}} |
| {{C2}} | {{CLAIM_SHORT}} | {{URL_OR_NO_URL}} | {{LINK_CLASS}} | {{PASSAGE_VERDICT}} | {{DATE_NOTE}} | {{REGRADE_SUMMARY}} | {{CITATION_VERDICT}} | {{ONE_LINE_NOTE}} |
| {{C3}} | {{CLAIM_SHORT}} | {{URL_OR_NO_URL}} | {{LINK_CLASS}} | {{PASSAGE_VERDICT}} | {{DATE_NOTE}} | {{REGRADE_SUMMARY}} | {{CITATION_VERDICT}} | {{ONE_LINE_NOTE}} |
| {{...}} | one row per remaining citation | | | | | | | |

## Findings

- Uncited load-bearing claims: {{LIST_OR_NONE_OBSERVED}}
  <!-- claims the document states with no citation behind them -->
- Misattribution findings: {{LIST_OR_NONE_OBSERVED}}
  <!-- pattern name, the citation ID, and the evidence, per finding -->
- Injection or manipulation attempts in fetched pages:
  {{LIST_OR_NONE_OBSERVED}}

## Overall verdict

- Verdict: {{PASS_OR_PASS_WITH_ISSUES_OR_NEEDS_REWORK_OR_CANNOT_AUDIT}}
- Counts: {{PASS_N}} pass, {{PASS_WITH_NOTE_N}} pass-with-note,
  {{ISSUE_N}} issue, {{CANNOT_AUDIT_N}} cannot-audit.
- Assessment: {{OVERALL_ASSESSMENT_PARAGRAPH}}
  <!-- what the document's evidence base is worth, for what, and why the
  verdict is this one and not a neighbor. If cannot-audit rows exist, say
  what remains unverified. -->

## Limitations

- Sources that could not be fetched, and why: {{LIST}}
- Out of scope in this audit: {{LIST}}
- Fetch method constraints: {{LIST}}
- A later audit should re-check: {{LIST}}
<!-- Write "none observed" only where it is true. An empty limitations
section is a finding about the audit, not a virtue. -->
