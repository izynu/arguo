# Claim verification

Verification is per claim, not per report. A report is verified when each of
its claims has been through this process and carries a status that matches the
evidence.

## Extract claims first

- Break the emerging answer into atomic claims: one sentence each,
  self-contained, checkable on its own.
- Tag each claim with a kind: fact, estimate, interpretation, comparison.
  The kind sets the bar:
  - Fact: directly checkable against a primary record.
  - Estimate: a number produced by some method; the method must be assessed.
  - Interpretation: an inference from evidence; the inference must be shown,
    not just the inputs.
  - Comparison: two or more things compared; both sides need evidence under
    compatible definitions.

## Verification statuses

- supported: primary or independently corroborated evidence directly backs
  the claim as worded.
- partially-supported: evidence backs part of the claim, or backs a weaker
  version of it.
- contradicted: independent evidence conflicts with the claim.
- insufficient-evidence: the search cannot find evidence that settles it.
- source-unavailable: evidence exists but could not be accessed (paywall,
  removal, archive-only fragment).
- requires-human-review: the default. Applied until passage support and
  corroboration have been checked, or when the judgment call is material and
  outside what automated checks can settle.

Statuses may change as evidence accumulates; record the change, do not
overwrite history.

## Passage support check

For each claim, against each cited row:

- Does the passage, read in full, actually assert what the claim asserts?
- Did qualifiers survive: "may", "in this sample", "as of", "among adults"?
- Is the direction right: does the passage support, or merely mention the
  topic adjacent to the claim?
- If the passage is data, does the claim match the observation period and
  population?

Overreach found here means the claim gets reworded or the status drops to
partially-supported. Common overreach patterns:

- Causation stated where the source shows correlation.
- Generalization from one instance, site, or country to everywhere.
- A percentage quoted without its denominator or base.
- "Significant" used statistically without the test being described.
- A forecast presented as an outcome.

## Negative verification

- Deliberately search for what would disprove each priority-1 claim.
- Record disconfirming evidence as contradicting rows, whatever its strength.
- A claim that survives an honest attempt at disconfirmation, with primary
  or independently corroborated support, earns "supported". A claim that was
  never attacked does not.

## Verdict recording

Per claim, the report's claim-evidence table carries: claim ID, claim text,
source IDs with relation (supports, contradicts, context), verification
status, and one line of reason. The reason is what the auditor reads first;
make it specific: "two independent primaries agree", not "well established".

## Ties to the rest of the skill

- Statuses feed the confidence language in
  references/uncertainty-and-limitations.md.
- The audit in references/citation-standards.md checks that every claim in
  the report has a status and that no unsupported claim ships unmarked.
