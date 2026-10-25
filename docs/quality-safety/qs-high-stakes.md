---
title: High-Stakes Limitations
description: Why Arguo output is an aid for medical, legal, financial, and safety questions, never an authority, and what human review it requires.
group: quality-safety
slug: qs-high-stakes
order: 7
---

Arguo is an aid for research, not an authority. For medical, legal, financial, and safety matters, its output is a starting point for a qualified human, never a conclusion.

Automated checks cannot guarantee truth. The audit stage verifies internal consistency: that citations resolve, that quoted passages exist in the fetched sources, and that every claim carries evidence. The audit report model states this in its own automated note: automated checks verify internal consistency and passage support, and they cannot guarantee truth. A report can be perfectly cited and still wrong, because every source can share a flaw, be outdated, or be misread.

Human review requirements. Every claim and evidence record defaults to the requires-human-review verification status. High-stakes work should keep that default: a qualified professional reviews each load-bearing claim against the cited passage, checks that guidance is current for the relevant jurisdiction or field, and signs off. Unreviewed output should not inform clinical, legal, financial, or safety decisions.

Known blind spots. Retrieval favors what is reachable and indexable; paywalled standards, case law, and non-English literature may be missing entirely. Time-sensitive facts can be stale by the time the report is read. Contradiction analysis surfaces conflicts between sources but cannot resolve them. Extraction is conservative, and complex pages can yield little text, which the toolkit records rather than papering over.

Incident reporting. If you find a safety-relevant defect, such as an SSRF bypass, a prompt-injection handling failure, or secret leakage, report it privately through the security policy page rather than a public issue. Coordinated disclosure is preferred.
