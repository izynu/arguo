# Curation run report: {{RUN_NAME}}

Every field is filled from what actually happened in the run. Empty
sections are kept with an explicit "none" rather than deleted. This
report is the auditable record of the run; it must be reproducible from
the target file and the commands quoted below.

## Run identity

- Agent task ID: {{TASK_ID}}
- Date: {{YYYY-MM-DD}}
- Agent: {{AGENT_NAME}}
- Skill: arguo-curator
- Target file: data/resources/{{TARGET_FILE}}.jsonl
- New file or append to existing: {{NEW_OR_APPEND}}
- Network availability during the run: {{AVAILABLE_OR_UNAVAILABLE}}

## What was written

- Records written: {{N}}
- Per-category distribution for the new records:
  - {{CATEGORY_KEY}}: {{N}}
  - {{CATEGORY_KEY}}: {{N}}
- Categories and counts are quoted from the validator output below,
  not estimated.

## Skipped candidates

For each skipped candidate: name, reason (duplicate, uncertain, out of
scope, unreachable), and one sentence of detail.

- {{CANDIDATE_NAME}}: {{REASON}}. {{DETAIL}}
- {{CANDIDATE_NAME}}: {{REASON}}. {{DETAIL}}
- None: {{IF_NO_SKIPS}}

## Validation results

Quoted commands and exit codes, exactly as run:

- python3 scripts/validate_catalog_file.py data/resources/{{TARGET_FILE}}.jsonl
  Exit code: {{0}}. Per-category counts as printed: {{COUNTS}}
- python3 scripts/validate_resources.py
  Exit code: {{0}}.
- Pre-existing warnings observed on files this run did not touch:
  {{WARNINGS_VERBATIM_OR_NONE}}

## Link verification outcome

- Offline check run: {{YES_OR_NO}}; issues reported: {{N_OR_NONE}}
- Live check run: {{YES_OR_NO}}; URLs requested: {{N}}
- Promoted to verified this run: {{IDS_OR_NONE}} with last_checked {{YYYY-MM-DD}}
- Remained documented: {{N}}
- If no live check ran, the reason: {{REASON}}

## Anomalies for the maintainer

Anything a human should look at before the next catalog build:
collisions observed, name twins on one domain, pre-existing validator
warnings, suspicious hosts, or records that should be reclassified.

- {{ANOMALY_OR_NONE}}

## Honesty statement

- Every URL in the new records was confirmed or flagged in provenance:
  {{CONFIRMED}}
- Every unknown license is recorded as unknown, not guessed: {{CONFIRMED}}
- No record was marked verified without a live check in this session:
  {{CONFIRMED}}
- Skipped candidates listed above account for every candidate
  considered and not written: {{CONFIRMED}}
