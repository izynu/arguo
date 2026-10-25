# Description quality and free-text fields

The free-text fields are the reader-facing surface of the catalog. The
website shows them verbatim. Write them like a reference work, not like
marketing.

## description (40 to 320 characters)

A good description answers three questions in one or two sentences:

- What is this resource, stated plainly?
- Who publishes or operates it?
- What does a researcher actually get from it?

Rules:

- Factual prose only. No hype adjectives: no "leading", "best",
  "comprehensive", "powerful", "premier", "cutting-edge". State the
  scope and let scope speak.
- No first person, no editorializing, no speculation about future
  features, no unverifiable superlatives.
- One or two sentences. Between 40 and 320 characters, measured as
  characters, so keep some margin under the ceiling.
- Pure ASCII: no em dashes, no en dashes, no emoji, no smart quotes.
  Use commas, colons, and hyphens.
- Say what it is even when it is famous. "US federal agency measuring
  labor market activity" beats "the official BLS site".
- Naming the publisher inside the description is good practice, and the
  publisher field should agree with it.

## best_for (1 to 4 items, each at most 60 characters)

- Concrete researcher uses, phrased as short noun phrases: "US
  population data", "decennial census tables", "CPI and inflation
  series".
- Each item under 60 characters, specific enough that two different
  resources in one category do not share identical lists.
- Order from the most distinctive use to the most general. One strong
  item beats four padded ones.

## tags (1 to 8, lowercase hyphenated, each at most 30 characters)

- Lowercase, hyphenated where a tag needs two words: "open-data",
  "clinical-trials", "united-states".
- Reuse tags that already appear in the same category so filtering
  works; invent a new tag only when no existing tag fits.
- Cover what the resource is about, not what it is called. Do not tag
  the category key itself as a substitute for thinking.

## license honesty

- Use an SPDX identifier only when the resource states one: CC-BY-4.0,
  MIT, ODbL-1.0, and so on, in SPDX form.
- "varies-by-item" is for aggregations where the content license differs
  per item, such as repositories mixing publisher licenses.
- "unknown" is the correct value whenever you did not determine the
  license. It is not a failure; a wrong license is the failure.
- Do not infer a site license from the license of one dataset or one
  code repository hosted under the same domain.

## The boolean and access fields

- api_available: true only when a public API exists and is documented
  somewhere you can point to. Availability of a download button is not
  an API. When unsure, false.
- official_source: true when the publisher is the originating authority
  for the content; false for aggregators, mirrors, and secondary
  indexes.
- resource_access reflects the interface, not the ideal: free-registration
  when an account is required, partial-open when some content is gated,
  mixed when free and paid tiers coexist.
- access_requirements: only when factual, at most 200 characters, for
  example eligibility rules or account requirements. Omit when there is
  nothing real to state.

## phrasing patterns that work

- "Principal statistical agency of the US federal government. Produces
  ... publishes ... and ...". Named role, then outputs.
- "Free research tool for ... with ..., operated by ...". Function, then
  features, then operator.
- "Web search engine indexing ... including ..., with ...". Scope, then
  coverage, then extras.

Read two or three existing records in your target category in
data/resources/ before writing, and match their register.

See references/schema-fields.md for the exact length limits and allowed
values, and references/category-selection.md when description writing
reveals the category was wrong.
