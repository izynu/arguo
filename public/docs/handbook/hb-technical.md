---
title: Software and standards research
description: Researching software, versions, and standards with official documentation, changelogs, and security advisories first.
group: handbook
slug: technical-research
order: 3
---

## Official documentation first

For questions about how software behaves, the load-bearing source is the official documentation, the changelog, or the source tree, not a blog post about it. The catalog's technical-documentation category (15 records) points at primary docs: MDN Web Docs, the Python documentation, the Kubernetes and PostgreSQL docs, and others. Aggregator posts and tutorials are useful leads and context; cite them as such, and anchor claims that carry weight in the official text.

## Version awareness

Software claims are version claims. Check that the documentation you are reading describes the version you actually run, record the version in the ledger row, and treat a behavior that changed between versions as a different claim per version. A page updated yesterday can still document an interface removed last year.

## Changelogs and release notes

For what changed and when, prefer the project's own changelog, release notes, or repository tags. A release note is a primary source for its own release. Deprecation notices deserve special attention because they bear on forward-looking claims: a feature marked deprecated supports present tense claims only.

## Security advisories

The security-advisories category (10 records) includes the National Vulnerability Database, OSV.dev, the CVE Program, the CISA Known Exploited Vulnerabilities Catalog, and the GitHub Advisory Database. Treat third party claims about vulnerabilities as leads until an advisory or the fix commit confirms them. Read the affected version ranges, not just the identifier: a CVE number alone does not tell you whether your version is exposed.

## Standards and specifications

The standards-specifications category (12 records) covers ISO, IEC, ITU, W3C, the RFC Editor, NIST, and others. Cite the specific revision of a standard, because revisions change requirements, and cite a draft as a draft. For package level questions, the software-registries category (18 records) lists GitHub, PyPI, npm, and their peers.
