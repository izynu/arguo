# Contradiction analysis

Sources disagree. That is expected and useful: contradictions locate the
interesting part of a question. The failure mode is not having conflicts; it
is resolving them silently, by preference, and reporting one number as if the
ground had never been contested.

## Collect before resolving

- Search for disagreement on purpose: run verification queries aimed at
  values that would differ from the emerging answer.
- Record every variant value in the ledger, including the ones that look
  obviously wrong. A contradicting row is evidence about the question even
  when the source is weak.
- Note who agrees with whom and whether the agreeing sources are actually
  independent. Agreement among syndicated copies is not corroboration.

## Classify the contradiction

- Measurement difference: different instruments, methods, or sampling frames
  produced different numbers. Common in surveys, prices, and environmental
  readings.
- Definitional difference: the sources use different definitions, for example
  of "unemployment", "market size", or "urban population". The numbers can
  both be right under their own definitions.
- Temporal difference: the sources describe different dates or periods.
  Frequently mistaken for disagreement.
- Scope or population difference: different geographies, age ranges, sectors,
  or inclusion rules.
- Error or fabrication: one source is simply wrong, outdated, or invented.
  Weaker sourcing, missing methods, and no corroboration point here.
- Genuine uncertainty: the underlying question is not settled, and the
  sources reflect a real distribution of expert judgment.

## Resolution workflow

1. Normalize: convert to common units, currencies, and base years; align
   definitions and periods where possible.
2. Re-read the primaries: many apparent conflicts dissolve when the original
   text's qualifications are restored.
3. Assess the sources: apply the rubric in references/source-quality.md to
   each side. Weight follows assessment, not volume.
4. Decide the resolution status:
   - explained: the difference has a cause (definition, period, scope) and
     the report can state it.
   - measurement-difference: both are honest measures of different things or
     methods; report both with their provenance.
   - one-source-weaker: rubric results clearly favor one side; report the
     favored value with the dissent noted.
   - unresolved: none of the above establishes a winner.
5. Record the resolution in the contradiction table, with links to ledger
   rows.

## Hard rules

- Never silently pick a number. Every dropped variant is either explained in
  the report or listed in limitations.
- Unresolved contradictions on load-bearing claims downgrade the claim's
  confidence and are stated in the report body, not buried.
- Do not average across definitions. An average of numbers that measure
  different things is a new error, not a synthesis.
- When the contradiction is material and unresolved, say what evidence would
  settle it, and stop there.

## The contradiction table

Fill templates/contradiction-table-template.md. Columns: topic, values found
with units and periods, source IDs, difference type, resolution status,
rationale. The table is part of the deliverable when the question involves
competing figures.
