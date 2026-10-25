---
title: Contributing a resource
description: How to add a catalog record: schema rules, pull request steps, validation, and review criteria.
group: resource-library
slug: contributing-a-resource
order: 10
---

## The schema

Every record conforms to data/schemas/resource.schema.json. Required fields: id (kebab-case, unique), name, canonical_url (https), category (a key from data/categories.json), description (40 to 320 characters, factual), best_for (1 to 4 phrases), resource_type, publisher, region, language (ISO 639-1 code), resource_access, api_available, official_source, license, date_added, verification_status, provenance, and tags (1 to 8). Optional fields: subcategory, documentation_url, attribution_requirements, access_requirements, last_checked, and status_notes. Every field must be factual; where a value is not known, use null or the literal string unknown rather than guessing.

## Steps

1. Fork the repository and create a branch.
2. Append the record as a single JSON line to the data/resources file that covers its categories, keeping the file's id prefix convention.
3. Validate the file: python3 scripts/validate_catalog_file.py data/resources/<file>.jsonl
4. Rebuild the merged catalog: python3 scripts/build_resource_catalog.py. The build merges the seed files, drops cross-file duplicates with an audit trail, and regenerates catalog/catalog.json, catalog/catalog.jsonl, and catalog/stats.json.
5. Open a pull request containing the record, the regenerated outputs, and a sentence on where the resource is useful.

## Review criteria

Reviewers check that the resource exists and is reachable at the https URL; that the category matches the taxonomy definition in data/categories.json; that the description is factual with no hype and no em dashes, en dashes, or emoji; that license says unknown where rights are uncertain; and that api_available and official_source are true only when certain. New seeds enter as verification_status documented with last_checked null; verified is reserved for records that have passed a real live check. A submission that cannot meet a rule says so in status_notes instead of bending a field.
