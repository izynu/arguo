# Governance

## Model

Arguo is maintainer-led. There is no foundation, no company, and no governance board behind this repository, and none is claimed. Decisions are made by the maintainer(s) with input from contributors.

## Maintainers

- [Zynu](https://github.com/izynu): lead maintainer and repository owner. The upstream repository lives at github.com/izynu/arguo.
- [Shraddha](https://github.com/xhraddha): co-maintainer.

## Current stage

The project is at the start of its public life:

- Two maintainers (listed above)
- Contributors who open issues, PRs, and catalog records

This document will be updated as that changes.

## Decision process

- Small changes (typos, doc fixes, test additions, validator refinements): a direct commit or a normal PR with one maintainer approval.
- Significant changes (public model fields, exit codes, CLI surface, schema changes, catalog policy, new dependencies, CI that runs on the main branch): an issue describing the change, the alternatives considered, and the tradeoffs. The issue stays open for a consensus window so contributors can comment. A consensus window is one week for routine changes and two weeks for breaking ones. The maintainer then decides and records the outcome in the issue.
- Anything that would change the honesty rules (verification status meanings, counts, style rules) is significant by default.

If a decision turns out wrong, reopen the issue or file a new one. Reversibility beats ceremony.

## Becoming a maintainer

Maintainer status is granted by the existing maintainer(s) based on:

- Sustained, merged contributions over time (code, tests, docs, or catalog work)
- Demonstrated understanding of the project's honesty rules and the arguo method
- Constructive participation in review and issue discussion

There is no fixed number of contributions, no election, and no time-in-project requirement. A current maintainer proposes the promotion in an issue, and an existing maintainer approves it.

## Transparency

- Decisions are documented. Significant decisions live in issues, and choices that shape architecture are written up as short ADR-style notes under `docs/` when they need lasting context.
- The worklog (`worklog.md`) records what was built and verified at each stage, including deviations from plans.
- Counts and claims in the README, docs, and changelog must be reproducible from real files and real runs. If a number cannot be reproduced, it does not ship.

## Code of conduct authority

Maintainers have the authority and the responsibility to enforce the [Code of Conduct](CODE_OF_CONDUCT.md): they may edit or remove contributions, warn, block, or escalate as described there. Enforcement decisions are recorded privately to protect the people involved.

## No foundation claims

This project is not affiliated with, endorsed by, or governed by any foundation, institute, university, or company. If that ever changes, this file and the README are updated in the same commit.
