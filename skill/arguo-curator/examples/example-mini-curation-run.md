# Example: a mini curation run

> This file is an illustrative example with representative sources, not
> a live run. The three records below use real, well-known organization
> homepages, and the validator output is a sketch of the expected
> format, not captured output. In a real run every value comes from
> observation or from the publisher, and every command is actually
> executed.

## Scenario

A maintainer asks for a small batch of international organization
resources to extend the catalog. The run targets a new authoring file,
data/resources/int-9.jsonl, and considers seven candidates.

## Step 1 and 2: candidates and the dedupe check

Seven candidates were considered. Collecting ids and normalized urls
from all data/resources/*.jsonl files showed four of them already
cataloged:

| Candidate | Homepage | Outcome |
| --- | --- | --- |
| World Health Organization | https://www.who.int/ | skipped: duplicate url |
| United Nations | https://www.un.org/ | skipped: duplicate url |
| World Bank | https://www.worldbank.org/ | skipped: duplicate url |
| International Monetary Fund | https://www.imf.org/ | skipped: duplicate url |
| International Labour Organization | https://www.ilo.org/ | written |
| United Nations Children's Fund | https://www.unicef.org/ | written |
| World Trade Organization | https://www.wto.org/ | written |

The skip reasons are recorded in the report; no record was weakened or
edited to make room for them.

## Step 3: the records written

Three records, one JSON object per line, single trailing newline at the
end of the file. All three enter as documented with last_checked null.

```jsonl
{"id": "ilo", "name": "International Labour Organization (ILO)", "canonical_url": "https://www.ilo.org/", "category": "international-organizations", "subcategory": "un system data", "description": "United Nations specialized agency for the world of work. Sets international labour standards, produces labour market statistics through ILOSTAT, and publishes research on employment, wages, and social protection.", "best_for": ["Labour standards and conventions", "Labour market statistics", "Employment and wage research"], "resource_type": "agency", "publisher": "International Labour Organization", "region": "global", "language": "en", "resource_access": "open", "api_available": false, "official_source": true, "license": "unknown", "date_added": "2026-10-25", "last_checked": null, "verification_status": "documented", "provenance": {"source": "curated-expansion", "note": null}, "tags": ["labour", "standards", "statistics", "un-system"]}
{"id": "unicef", "name": "United Nations Children's Fund (UNICEF)", "canonical_url": "https://www.unicef.org/", "category": "international-organizations", "subcategory": "un system data", "description": "United Nations agency for children. Works on child health, education, protection, and humanitarian response worldwide, and publishes child-focused statistics and flagship reports such as the State of the World's Children.", "best_for": ["Child wellbeing data", "Humanitarian program reports", "Global policy briefs"], "resource_type": "agency", "publisher": "United Nations Children's Fund", "region": "global", "language": "en", "resource_access": "open", "api_available": false, "official_source": true, "license": "unknown", "date_added": "2026-10-25", "last_checked": null, "verification_status": "documented", "provenance": {"source": "curated-expansion", "note": null}, "tags": ["children", "humanitarian", "un-system"]}
{"id": "wto", "name": "World Trade Organization (WTO)", "canonical_url": "https://www.wto.org/", "category": "trade-supply-chain", "subcategory": null, "description": "Intergovernmental organization for the rules of trade between nations. Administers trade agreements, monitors trade policy, and publishes global trade statistics, tariff profiles, and world trade reports.", "best_for": ["Global trade statistics", "Trade policy monitoring", "Tariff profiles"], "resource_type": "organization", "publisher": "World Trade Organization", "region": "global", "language": "en", "resource_access": "open", "api_available": false, "official_source": true, "license": "unknown", "date_added": "2026-10-25", "last_checked": null, "verification_status": "documented", "provenance": {"source": "curated-expansion", "note": null}, "tags": ["trade", "tariffs", "statistics", "global"]}
```

Notes on choices a reviewer should be able to check:

- api_available is false for all three: no documented public API was
  confirmed in this run, so none is claimed.
- license is "unknown" for all three: no site license was determined,
  and none was guessed.
- WTO carries subcategory null: no existing subcategory wording fit and
  inventing one was not worth it.
- The ILO and UNICEF subcategories reuse "un system data", the wording
  already dominant in the international-organizations category.

## Step 4: validation (sketch of expected output, not captured output)

```text
$ python3 scripts/validate_catalog_file.py data/resources/int-9.jsonl
File: data/resources/int-9.jsonl
Records: 3
Category counts:
  international-organizations: 2
  trade-supply-chain: 1
PASS: schema, uniqueness, and style checks OK

$ python3 scripts/validate_resources.py
(per-file checks pass on all files; cross-file uniqueness: no new
duplicates introduced by int-9.jsonl)
```

Both commands exited 0 in the sketch; a real report quotes the real
exit codes.

## Step 5: link verification

No live check was executed in this illustrative run, so all three
records remain documented with last_checked null. A real run would run
scripts/check_links.py after a catalog build, and only records whose
canonical_url classified ok would be promoted to verified with
last_checked set to the check date. Promotion without that check is
never allowed, offline in this example or anywhere else.

## Run report summary

- Records written: 3 (international-organizations 2, trade-supply-chain 1)
- Skipped candidates: 4, all reason duplicate url
- Validators: both pass (exit 0)
- Promoted to verified: none
- Anomalies: none
