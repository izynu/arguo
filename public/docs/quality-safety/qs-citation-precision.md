---
title: Citation Metrics
description: Precise definitions, formulas, and limitations of the citation quality metrics computed or judged in Arguo.
group: quality-safety
slug: qs-citation-precision
order: 3
---

These definitions are structural: they specify what the eval runner and the audit stage compute. None of them is a published result.

Citation validity. The fraction of citations in a report whose source URL is well formed (http or https), resolves, and was fetched successfully during the run. Formula: valid citations divided by total citations. Limitations: liveness changes over time; paywalls, robot blocks, and timeouts produce source-unavailable outcomes that lower the score without any wrongdoing; a valid URL says nothing about the claim it supports.

Citation support precision. The fraction of citations where the relevant passage recorded in the evidence ledger appears in, or is a faithful rendering of, the fetched source text. The automated part compares the recorded passage against stored content using the content hash and lexical overlap. Formula: supported citations divided by total citations. Limitations: lexical matching misses paraphrase and translation; the final semantic judgment is human.

Unsupported-claim rate. The fraction of claims with no supporting evidence record, or carrying an unsupported-claim or missing-source issue. Formula: unsupported claims divided by total claims. Limitations: the rate depends on how text is segmented into claims; the same report can yield different rates under different segmentation.

Source diversity. Distinct independence groups (registrable domains or syndication groups) among cited sources. Formula: unique independence groups divided by total sources. Limitations: domain independence is not editorial independence; wire copy and syndication can hide shared origins.

Primary-source coverage. The fraction of sources classified as primary among sources with a known type. Formula: primary sources divided by sources with a known type. Limitations: classification is recorded metadata, often heuristic, and misclassification is common; unknown types are excluded from the denominator.

Automated versus human judged. The runner computes syntax, fetch outcomes, hashes, overlaps, and counts. Humans judge semantic support, source type, and independence. Reports must keep the two separated, and no aggregate quality score is published.
