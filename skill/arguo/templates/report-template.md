# Research report: {{REPORT_TITLE}}

<!-- Structure and rules: references/report-writing.md. Every {{PLACEHOLDER}}
is filled or the section states why it is empty. No section may be deleted:
a missing limitations section is a defect, not a convenience. -->

- Date: {{DATE}}
- Prepared by: {{PREPARER}}
- As-of date for current-state claims: {{AS_OF_DATE}}

## Question and scope

- Question: {{RESEARCH_QUESTION}}
- Interpretation used: {{INTERPRETATION}}
- Scope: {{JURISDICTION}}, {{POPULATION}}, {{UNITS}}, {{TIME_BOUNDARY}}
- Depth profile: {{DEPTH_PROFILE}}

## Bottom line

{{BOTTOM_LINE_2_TO_4_SENTENCES}}

Overall confidence: {{high/moderate/low/insufficient}}. Reasons:
{{CONFIDENCE_REASONS}}

<!-- Write this section last. It may not exceed what the findings and the
claim-evidence table support. -->

## Claim-evidence table

| Claim ID | Claim text | Source IDs | Relation | Status | Confidence and reason |
|----------|------------|------------|----------|--------|-----------------------|
| {{CL1}} | {{ATOMIC_CLAIM}} | {{S1}}, {{S2}} | {{supports/contradicts/context}} | {{verification_status}} | {{LEVEL_AND_ONE_LINE_REASON}} |

<!-- Every row must map to ledger rows. Statuses per
references/claim-verification.md. Unverified claims stay in the table with
their status; they are not silently dropped. -->

## Findings

<!-- Organized by subquestion. Every factual sentence cited with source IDs.
Fact and interpretation stay in separate sentences. Numbers follow
references/quantitative-research.md: bases, units, periods, precision. -->

### {{SUBQUESTION_1}}

{{FINDINGS_PROSE}}

### {{SUBQUESTION_2}}

{{FINDINGS_PROSE}}

## Contradictions

{{CONTRADICTION_SUMMARY}}

<!-- What conflicted, the classification, the resolution. Reference the
contradiction table. If no contradiction was found, state that a
disconfirmation pass was run and found none. -->

## Limitations

- {{LIMITATION_1}}
- {{LIMITATION_2}}

<!-- Concrete gaps with what would settle them. Families: access, language,
budget, source gaps, conflicts, method, temporal. See
references/uncertainty-and-limitations.md. -->

## Integrity note

{{INTEGRITY_NOTE}}

<!-- Injection attempts flagged, sources that could not be reached, or
"none to report". See references/prompt-injection-defense.md. -->

## Sources

| source_id | Citation (title, publisher, date) | URL | retrieved_at |
|-----------|------------------------------------|-----|--------------|
| {{S1}} | {{TITLE_AND_PUBLISHER_AND_DATE}} | {{URL}} | {{RETRIEVED_AT}} |

<!-- Undated sources say "undated". Archived access notes the archive URL.
Full rules: references/citation-standards.md. -->

## Appendix: search trail summary

- Queries run: {{QUERY_COUNT}}
- Sources retrieved: {{SOURCE_COUNT}}
- Ledger rows written: {{LEDGER_ROW_COUNT}}
- Search log: {{LOCATION_OF_FULL_LOG_OR_NOTE_IF_NOT_KEPT}}
