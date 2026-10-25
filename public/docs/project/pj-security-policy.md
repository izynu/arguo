---
title: Security Policy
description: How to report vulnerabilities in Arguo privately, what is in scope, what is not, and what response to expect.
group: project
slug: pj-security-policy
order: 7
---

Supported version. Security fixes target the latest release on the main branch. There is no long-term-support line yet.

How to report. Report vulnerabilities privately; do not open a public issue. Preferred path: GitHub Security Advisories on the arguo repository, once the repository is published and advisories are enabled. Email: TODO for repository owner, insert the security contact address here before launch. Either channel is fine; do not report through both.

What is in scope:

- SSRF bypasses: any URL that reaches private, loopback, link-local, multicast, or reserved address ranges through the guard, including via redirects or DNS behavior.
- Prompt-injection failures where untrusted retrieved content changes agent behavior in ways the design forbids, such as following instructions found in a fetched page.
- Secret leakage: API keys or other credentials appearing in logs, run artifacts, cache files, or error messages despite the redaction layer.
- Artifact handling defects that let fetched content escape its role as quoted data.

What is not in scope: the upstream websites and services the toolkit retrieves, whose problems belong to their operators; factual accuracy of catalog records; brute force or denial of service against the site; and issues that require an attacker who already controls the local machine or environment.

Response expectations. Best effort, by volunteers. There are no promised response or fix times. You will receive an acknowledgment, a triage note, and credit in the changelog if you want it. Coordinated disclosure is preferred: please keep details private until a fix is released or a publication date is agreed.
