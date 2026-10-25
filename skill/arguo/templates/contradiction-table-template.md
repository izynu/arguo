# Contradiction table

<!-- Fill when sources disagree on a value, fact, or interpretation. Method:
references/contradiction-analysis.md. Rules: normalize before comparing,
never average across definitions, never silently drop a variant. Delete
these comment blocks before delivery. -->

- Run ID: {{RUN_ID}}
- Topic: {{CONTESTED_TOPIC}}
- Normalization applied: {{UNITS_CURRENCY_BASE_YEAR_DEFINITIONS_ALIGNED}}

## Contradictions

| ID | Values found (with units and periods) | Source IDs | Difference type | Resolution status | Rationale |
|----|----------------------------------------|------------|-----------------|-------------------|-----------|
| {{C1}} | {{VALUE_A}} ({{SOURCE_A}}, {{PERIOD_A}}) vs {{VALUE_B}} ({{SOURCE_B}}, {{PERIOD_B}}) | {{S1}}, {{S2}} | {{measurement/definitional/temporal/scope/error-or-fabrication/genuine-uncertainty}} | {{explained/measurement-difference/one-source-weaker/unresolved}} | {{WHY_THIS_RESOLUTION}} |

<!-- Difference types and resolution statuses are defined in
references/contradiction-analysis.md. one-source-weaker requires the rubric
outcomes that favor a side, from templates/source-assessment-template.md. -->

## Ledger links

- Contradicting rows: {{LEDGER_ROW_REFERENCES}}
- Resolving passages: {{LEDGER_ROW_REFERENCES}}

## What would settle it

<!-- For every unresolved row, name the record, dataset, archive, or query
that would resolve it. This feeds the report's limitations section. -->

- {{C1}}: {{SETTLING_EVIDENCE}}
- {{C2}}: {{SETTLING_EVIDENCE}}

## Report phrasing

<!-- How the report will state this: the spread, the cause if known, and the
confidence effect. No silent picks. Example phrasing: "Sources report X and
Y for {{TOPIC}}; the difference tracks the definition used ({{DEF_A}} vs
{{DEF_B}}); both are recorded here." -->

- {{RESOLUTION_STATEMENT}}
