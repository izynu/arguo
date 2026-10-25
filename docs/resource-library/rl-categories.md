---
title: The category taxonomy
description: The 50 category keys of the resource catalog, grouped in a compact table showing what belongs where.
group: resource-library
slug: category-taxonomy
order: 2
---

The catalog holds 1,570 records organized into 50 categories in the 2026-10-25 build. The keys below are stable identifiers defined in data/categories.json and used in records, the CLI, and the website.

| Category keys | What belongs there |
|---|---|
| academic-search, bibliographic-metadata, journals-open-access, preprint-repositories, institutional-repositories | Scholarly discovery, citation metadata, open-access journals, preprints, university repositories |
| biomedical-literature, clinical-trials, systematic-reviews, research-methods, research-ethics | Biomedical literature, trial registries, review registries, methods and synthesis, ethics and governance |
| physical-sciences, computer-science, ai-models-datasets, statistics-reproducibility, patents-ip | Physics, math, chemistry, computing and ML literature, model and dataset hubs, reproducibility, patents |
| software-registries, technical-documentation, standards-specifications, security-advisories, public-apis | Package registries, official docs, standards bodies, vulnerability databases, public API listings |
| government-statistics, economics-finance, international-organizations, demographics-population, public-opinion-surveys | National statistical offices, economic and monetary series, multilateral data, population, surveys |
| climate-meteorology, environment-ecology, energy-resources, agriculture-food, earth-observation | Climate records, ecology and biodiversity, energy, agriculture and land use, satellite data |
| law-regulation, international-relations-policy, corporate-filings, financial-markets, trade-supply-chain | Legislation and courts, policy and IR, company disclosures, market data, trade |
| public-procurement-budgets, elections-politics, education-social-science, geospatial-mapping, astronomy-space | Spending data, elections, education and social science, maps and places, space science |
| history-archives, national-libraries, news-archives, web-archives, journalism-investigative | Archives, national collections, digitized newspapers, web snapshots, investigative journalism |
| data-journalism, fact-checking, scientific-assessments, open-data-catalogs, discovery-utilities | Data journalism tools, fact-checking organizations, assessment bodies, dataset catalogs, general lookups |

Category sizes vary by design. The largest are institutional-repositories with 44 records, government-statistics with 40, and economics-finance with 29. The smallest are systematic-reviews with 7 and discovery-utilities with 3. All counts come from catalog/stats.json and change only when the catalog is rebuilt.
