# Source assessment

<!-- One filled assessment per load-bearing source. Rubric and levels are
defined in references/source-quality.md. Rationale lines matter more than
the level words: a reviewer reads those first. Delete this comment block
before delivery. -->

- source_id: {{S1}}
- Assessed for subquestion: {{SQ_ID}}
- Title: {{TITLE}}
- Publisher and registrable domain: {{PUBLISHER_AND_DOMAIN}}
- URL consulted: {{URL}}
- retrieved_at: {{RETRIEVED_AT}}

## Rubric

| Criterion | Level | Rationale |
|-----------|-------|-----------|
| 1. Authority for the question | {{high/medium/low/unknown}} | {{WHY_THIS_PUBLISHER_COUNTS_HERE}} |
| 2. Primary vs secondary | {{primary/secondary/tertiary/unknown}} | {{WHAT_THE_DOCUMENT_IS}} |
| 3. Methodological quality | {{strong/adequate/weak/not-applicable/unknown}} | {{METHODS_PRESENT_AND_SUITABLE_OR_NA}} |
| 4. Recency | {{current/aging/outdated/unknown}} | {{OBSERVATION_PERIOD_VS_QUESTION_BOUNDARY}} |
| 5. Directness | {{direct/indirect/inferred}} | {{SPEAKS_TO_THE_QUESTION_ITSELF_OR_A_NEIGHBOR}} |
| 6. Transparency | {{documented/partial/opaque/unknown}} | {{METHODS_DATA_FUNDING_VISIBILITY}} |
| 7. Conflicts of interest | {{none-known/possible/declared/unknown}} | {{FUNDING_izynuSHIP_STAKES}} |
| 8. Independent corroboration | {{independent/syndicated/single-source/unknown}} | {{WHICH_OTHER_GROUPS_AGREE_OR_NOT}} |
| 9. Limitations | (list) | {{WHAT_THE_SOURCE_ITSELF_CANNOT_SHOW}} |
| 10. Publisher provenance | {{checked/problem/unknown}} | {{WHO_REALLY_PUBLISHES_THIS}} |

<!-- Criterion 10 records whether the apparent publisher is the actual
publisher: check the registrable domain and the imprint. -->

## Notes

- Access path: {{HOW_CONTENT_WAS_REACHED}}
  <!-- direct, archive snapshot, official mirror, abstract only -->
- Integrity flags: {{INTEGRITY_FLAGS}}
  <!-- injection attempts, stripped attribution, inconsistent metadata,
  per references/prompt-injection-defense.md. Write "none observed" when
  empty. -->

## Effect on claims

- This source may support: {{CLAIM_IDS}}
- It may not be used alone for: {{CLAIM_IDS}}
  <!-- e.g. claims needing independent corroboration -->
