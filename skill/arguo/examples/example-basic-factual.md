# Example: a basic factual question

> Illustrative example with representative sources, not a live run. The
> passages below are representative summaries written for teaching the
> method, the retrieval dates are illustrative, and the citations point to
> the organizations' sites at domain level rather than to specific pages.
> Do not quote this file as evidence for anything.

## Question

"How many chromosomes are in a typical human somatic cell?"

## Step 1 and 2: understand and plan

- Claim type: fact.
- Scope: humans; typical (not syndrome cases); somatic cells, so not gametes.
- Subquestions (quick profile, so one):
  - SQ1: What number do authoritative medical-genetics sources state for the
    chromosome count of a normal human somatic cell?
- Evidence requirement: at least two independent institutional sources in
  agreement; one may be an authoritative educational secondary.
- Stopping rule: verdict reached, or three search rounds used.

## Step 3: search

Queries (illustrative round log):

1. "how many chromosomes do humans have": general orientation.
2. site targeting at a national health agency's genetics portal.
3. "46 chromosomes" "23 pairs" somatic cells: verification phrasing.

## Steps 4 and 5: primary-leaning sources, ledger

Three sources were selected. Note the independence groups: three different
registrable domains, no syndication, and the two agency pages are from
different agencies.

### Source register

| source_id | title | publisher | URL (illustrative, domain level) | published_at | retrieved_at | independence_group |
|-----------|-------|-----------|----------------------------------|--------------|--------------|--------------------|
| S1 | Help me understand genetics: chromosome count | U.S. National Library of Medicine, MedlinePlus Genetics | https://medlineplus.gov/ | 2021-04-12 | 2025-01-15 | medlineplus.gov |
| S2 | Chromosomes fact sheet | National Human Genome Research Institute | https://www.genome.gov/ | unknown | 2025-01-15 | genome.gov |
| S3 | Biology for majors I: chromosome structure | OpenStax, Rice University | https://openstax.org/ | 2016-05-18 | 2025-01-15 | openstax.org |

### Evidence records

| claim_text | source_id | source_url | relevant_passage | published_at | retrieved_at | supports_or_contradicts | independence_group | verification_status | limitations |
|------------|-----------|------------|------------------|--------------|--------------|-------------------------|--------------------|---------------------|-------------|
| A typical human somatic cell contains 46 chromosomes. | S1 | https://medlineplus.gov/ | In humans, most cells contain 46 chromosomes, arranged in 23 pairs. (Genetics FAQ, chromosome section) | 2021-04-12 | 2025-01-15 | supports | medlineplus.gov | requires-human-review | [] |
| A typical human somatic cell contains 46 chromosomes. | S2 | https://www.genome.gov/ | Human somatic cells hold 46 chromosomes in 23 pairs; gametes carry 23. (Fact sheet, overview) | unknown | 2025-01-15 | supports | genome.gov | requires-human-review | [publication date not shown] |
| A typical human somatic cell contains 46 chromosomes. | S3 | https://openstax.org/ | Human body cells are diploid with 46 chromosomes, half inherited from each parent. (Textbook chapter on cell reproduction) | 2016-05-18 | 2025-01-15 | supports | openstax.org | requires-human-review | [educational secondary] |

## Steps 6 and 7: corroboration and contradictions

- Independence: three distinct groups (medlineplus.gov, genome.gov,
  openstax.org). No syndication paths identified among them.
- Disconfirmation pass: a verification query was run looking for contradicting
  counts. No source states a different typical count; the only variants found
  concerned gametes (23) and aneuploidy cases, which are out of scope by the
  question's "typical somatic cell" framing.
- Contradiction table: empty. All three rows support the claim.

## Steps 8 to 10: dates, quality, numbers

- Dates: S1 published 2021; S2 undated (a stable fact page; update date not
  shown, recorded as unknown); S3 is a 2016 textbook edition. The fact is
  stable, so an older textbook is acceptable; recency judged per
  references/publication-dates.md.
- Quality: S1 and S2 are government health institutions, direct on the
  question; S3 is an educational secondary, adequate for a stable fact.
  Assessments recorded with templates/source-assessment-template.md.
- Numbers: the count 46 is a discrete fact; the pairing into 23 is part of
  the same claim. No denominators or periods apply.

## Step 11: citation audit

- Every claim cited; every source used; URLs recorded at domain level here
  because this example is illustrative; in a real run the exact pages would
  be recorded. Quotes are labeled as representative summaries, not verbatim,
  per the banner at the top of this file. Audit passed for the example's
  purposes.

## Step 12: report

### Report: chromosome count in human somatic cells

- As-of date: 2025-01-15 (illustrative).

**Bottom line.** A typical human somatic cell contains 46 chromosomes,
organized in 23 pairs. Confidence: high. Reasons: three sources from
independent domains agree, two of them government health institutions
speaking directly to the question, and a deliberate disconfirmation search
found no contradicting count.

**Claim-evidence table.**

| Claim ID | Claim text | Source IDs | Relation | Status | Confidence and reason |
|----------|------------|------------|----------|--------|-----------------------|
| CL1 | A typical human somatic cell contains 46 chromosomes in 23 pairs. | S1, S2, S3 | supports | supported | high: independent institutional agreement, direct question match |

**Limitations.** None material for the claim. In a real run, the limitations
section would record the exact pages consulted and any undated sources.

**Sources.** As registered above: MedlinePlus Genetics (U.S. National Library
of Medicine), NHGRI Chromosomes fact sheet, OpenStax Biology. Retrieval dates
2025-01-15 (illustrative).
