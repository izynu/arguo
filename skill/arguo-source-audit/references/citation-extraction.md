# Citation extraction

The inventory comes first. Before any fetch, extract every citation from
the document and write down what the document claims, what it cites, and
where. The inventory defines the audit's scope: what is not inventoried
does not get audited, so extraction mistakes are audit mistakes.

## What counts as a citation

Extract all of these:

- Inline citations: bracketed numbers, author-year mentions, or hyperlinks
  attached to a claim in the body text.
- Footnotes and endnotes, including ones that only carry a URL.
- Bibliography or reference list entries, when the audit's scope includes
  them. State the scope choice in the report.
- Bare attributions with no URL: "according to the ministry", "a 2023
  study found". These get entries too, with the URL marked absent.
- Link text that names a different source than the URL resolves to. Keep
  both: the name is what the reader was told, the URL is where they were
  sent.

## Fields per entry

Record these fields for every citation, in a working list before the audit
table exists:

- citation_id: C1, C2, C3, in order of first appearance.
- claim_text: the claim as the document states it, verbatim or as a tight
  paraphrase that changes neither strength nor scope.
- claim_location: where the claim appears: section, paragraph, page.
- cited_url: the URL the document gives, exactly as written. Normalize
  nothing yet; a malformed URL is an audit finding, not something to fix
  silently.
- cited_passage: the passage the document quotes, if any, plus the locator
  it gives (page, section, heading). If the document paraphrases instead
  of quoting, write paraphrase and keep the paraphrase.
- citation_form: inline, footnote, bibliography, bare attribution.
- notes: anything odd: two claims sharing one footnote, a citation whose
  link text names a different source, a date inside the citation.

## Clustered citations

One footnote or one sentence of citations often covers several claims:

- If distinct claims share one citation, create one entry per claim-source
  pair. The audit table has one row per citation, and a row carrying two
  claims cannot get a single honest passage verdict.
- If one claim carries several citations, keep one entry per cited source.
  Each is checked separately; corroboration across them is recorded, not
  assumed.
- When the split is genuinely ambiguous, record the ambiguity in notes and
  choose the reading that gives each claim its own checkable row.

## Claims with no citation

Load-bearing claims with no citation are an audit finding:

- List them in the report under findings, with their location and text.
- Do not invent a citation for them, and do not attach them to a neighbor's
  citation. The finding is precisely that no citation exists.
- Peripheral uncited claims (the author's own framing, common knowledge)
  can be noted once in bulk instead of itemized, and say which is which.

## What not to do

- Do not rewrite a claim into a version you could more easily verify. The
  audit tests the claim as written; scope and strength stay intact.
- Do not resolve an ambiguous citation by guessing the intended source.
  Mark it ambiguous and audit what the citation literally says.
- Do not skip citations inside images, charts, or alt text without saying
  so in the limitations. If the medium hid citations from you, report it.
- Do not deduplicate across different URLs. Same content at two URLs is
  still two citations in the document, and each link is checked.
