# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Two new Agent Skill packages: `skill/arguo-curator` (a method for curating and validating the resource catalog) and `skill/arguo-source-audit` (a method for auditing the citations in an existing report).
- `scripts/validate_skill.py` now validates any skill package under `skill/`: pass folder names or `all`, and the canonical `arguo` file expectations still apply to the default run.

### Changed

- Resource catalog expanded by 300 records in three new authoring files (`data/resources/academic-5.jsonl`, `gov-5.jsonl`, `general-6.jsonl`): 1,570 unique records across 50 categories and 82 regions, 369 with documented public APIs. All new records are `documented` and dedupe-checked.
- README, docs, and the Makefile validate target now cover all three skill packages.

## [0.1.0] - 2026-10-24

First public release.

### Added

- Agent skill at `skill/arguo`: SKILL.md method guide, 20 references, 5 templates (research plan, evidence ledger, source assessment, contradiction table, report), and 2 worked examples. Text only, no code dependencies.
- Python package `arguo` (import name `arguo`) with a 10-stage research pipeline: plan, search, retrieve, extract, ledger, assess, corroborate, audit citations, synthesize, and report. CLI app `arguo` with `research`, `resources` (search, list, validate, stats), `config check`, `doctor`, `cache clear`, and `eval run`.
- Evidence ledger data model with claims, evidence records, source links, corroboration across independent domains, and an explicit `insufficient-evidence` verdict.
- Citation audit that reports missing, unused, and unsupported citations, plus numeric contradiction scanning across sources.
- Four research profiles: `quick`, `standard`, `deep`, `academic`, each with its own source and time budgets.
- Offline demo mode: fixture-backed search provider and a fully offline test path. No API keys required.
- Resource catalog: 1,570 unique records across 50 categories and 82 regions, merged with dedupe (1,594 raw records across 19 authoring files, 24 cross-file duplicates dropped with an audit trail). 150 records carry verification status `verified` from the 2026-10-25 live link check; the remaining 1,420 are `documented`.
- Resource tooling: `scripts/validate_resources.py`, `scripts/validate_catalog_file.py`, `scripts/build_resource_catalog.py`, `scripts/check_links.py` (offline by default, opt-in polite live mode), `scripts/sync_resources.py` (disabled example sources), `scripts/generate_docs.py`.
- Source ingestion policy in `data/source-policy.yaml`: official APIs first, robots respected, polite rate limits, provenance recorded, metadata only, licenses recorded or `unknown`, no fabrication.
- Test suite: 167 offline tests covering models, guards, cache, dedupe, ledger, citations, assessment, contradictions, synthesis, report, CLI, and the end-to-end offline pipeline.
- Evaluation harness with 56 structural cases in 8 files, including adversarial prompt-injection and cross-domain contradiction cases.
- Docs site: Next.js static site fed by 81 documentation pages in 8 groups, with a catalog explorer, eval overview, methodology and legal pages, and generated `docs-index.json`, `llms.txt`, and `llms-full.txt`.
- Security controls: URL scheme allowlist, private and link-local address blocking, credential rejection, redirect revalidation with a 3-hop limit, 2,000,000-byte response cap, 20-second fetch timeout, a 7-pattern prompt-injection guard with wrapped untrusted content and a 6,000-character prompt cap, and a secret registry that scrubs logs and artifacts.
- Community and CI files: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, SUPPORT.md, GOVERNANCE.md, CITATION.cff, Makefile, pre-commit config, GitHub workflow templates for CI, Pages deploy, and scheduled resource validation.

### Changed

- Nothing: this is the first released version. Earlier development happened before the changelog existed; see `worklog.md` for the build record.

### Honest limitations

- 1,420 of 1,570 catalog records are `documented`, not `verified`. Verification status `verified` is reserved for records that pass an actual live check: a rate-capped live pass on 2026-10-25 verified 150 records; the rest keep `documented` until they are checked.
- The agent's automated checks verify internal consistency and whether report passages are supported by recorded evidence. They cannot guarantee truth and do not replace human review.
- Known SSRF residual risks are documented, including DNS rebinding between the safety check and the fetch, exotic redirect chains, and non-default ports.
- The catalog authoring files in `data/resources/` still contain cross-file duplicate ids and URLs; the build dedupes them, and the validator reports them as warnings by default (`--strict` fails).
- The docs site deploy workflow has not been exercised against a published repository yet; it is written for GitHub Pages with `NEXT_PUBLIC_BASE_PATH` and requires Pages to be enabled in repository settings.
