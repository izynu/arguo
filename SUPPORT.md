# Support

## Where to ask

Open a GitHub Issue on this repository (github.com/izynu/arguo). Use the bug report or feature request template that fits. For anything you do not want public, contact [@izynu](https://github.com/izynu) through GitHub.

## Before asking

Many answers are already in the repository:

- Setup and first run: `docs/getting-started/`
- CLI and Python API: `docs/developer-guide/`
- Environment variables: `.env.example` and `docs/getting-started/gs-environment-variables.md`
- The research method: `skill/arguo/SKILL.md` and `docs/core-concepts/`
- Troubleshooting: `docs/getting-started/gs-troubleshooting.md`

## Filing a bug

Include, where relevant:

- The exact command you ran and its full output
- Your operating system and Python version (`python3 --version`)
- Whether the run was `--offline` or used live providers
- The six run artifacts from the failing run, with any API keys removed
- What you expected to happen instead

Run artifacts (research_plan.json, sources.json, evidence.json, audit.json, report.md, manifest.json) contain the question and the sources used. Remove any content you do not want public before attaching them.

## Expected behavior notes

- The agent's automated checks verify internal consistency and whether report passages are supported by recorded evidence. They cannot guarantee truth, and they do not replace human review.
- Offline mode uses fixture providers from `tests/fixtures/offline_search.json`. Its outputs are demonstrations, not research.
- 1,420 of 1,570 catalog records are marked `documented`, not `verified`. A record moves to `verified` only after an actual live check; 150 records were live-checked on 2026-10-25.
- Low or empty findings in a run can be the honest result: the pipeline reports `insufficient-evidence` when the evidence does not support a verdict.

## Commercial support

None is offered. There is no paid tier, no SLA, and no paid support channel for this project.
