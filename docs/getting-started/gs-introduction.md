---
title: Introduction
description: What Arguo is, what it ships, who it is for, and what it honestly does not do.
group: getting-started
slug: gs-introduction
order: 1
---

## What Arguo is

Arguo is an open source research toolkit built around one rule: a claim without a recorded source is an opinion. Instead of producing a free standing answer, every research run assembles a ledger of sources, evidentiary passages, and claims, then audits its own citations before a report is written. Unknowns stay explicit, contradictions are surfaced rather than smoothed over, and insufficient evidence is a valid final verdict.

## The three deliverables

| Deliverable | Location | What it is |
| --- | --- | --- |
| Agent Skills | `skill/arguo/`, `skill/arguo-curator/`, `skill/arguo-source-audit/` | Text only methods (SKILL.md, references, templates) that any file reading agent can follow, with no code dependencies: the research method, catalog curation, and citation auditing. |
| Python research agent | `python/arguo/` | The `arguo` package with the `arguo` CLI. It runs a staged pipeline: plan, search, fetch, extract, record evidence, verify, audit, report. |
| Resource catalog and docs site | `data/resources/`, `catalog/`, `docs/` | Curated starting point resources merged into a catalog by `scripts/build_resource_catalog.py`, plus a Next.js documentation site inside the same repository. |

## Who it is for

Researchers, journalists, analysts, students, and engineers who need cited, auditable research outputs and want the audit trail in machine readable form. It also serves builders of research agents who want a reference implementation of evidence first behavior: explicit nulls, budget enforcement, provenance on every passage, and honest handling of uncertainty.

## Honest scope statement

Arguo structures and audits research. It does not guarantee truth. The citation checker verifies internal consistency and whether a cited passage actually supports a claim; it cannot certify that the underlying source is correct. Every `audit.json` carries that note verbatim. Treat the toolkit as a discipline and an audit layer, not an oracle. Human review remains necessary for high stakes conclusions.

## Where to go next

The getting-started group continues with installation, a quickstart, a first research run, CLI and Python tutorials, configuration, environment variables, troubleshooting, and an FAQ. The core-concepts group explains the architecture, the ten stage workflow, the ledger model, corroboration, contradictions, citation verification, dates, uncertainty, budgets, and caching.

Other documentation groups cover the rest of the project: skill-guide for the Agent Skill method, resource-library for the catalog, handbook for method deep dives, developer-guide for contributing code, quality-safety for the security model, and project for roadmap and decisions.
