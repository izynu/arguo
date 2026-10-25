---
name: Bug report
about: Report something that does not work as documented
labels:
  - bug
---

Thanks for taking the time to file a bug. Please fill in the sections below and remove anything that does not apply.

## Summary

A clear, short description of the problem.

## What you ran

The exact command or code path, for example:

```bash
arguo research "your question" --offline --output-dir runs/bug
```

## What happened

The actual output or behavior. Paste the relevant log lines.

## What you expected

What you expected to happen instead, ideally referencing the documented behavior (which docs page or doc section).

## Environment

- OS:
- Python version (`python3 --version`):
- Run mode: offline (`--offline`) or live providers:
- Version (from `pyproject.toml` or the package metadata):

## Run artifacts

If the bug involves a research run, attach the relevant artifacts (`research_plan.json`, `sources.json`, `evidence.json`, `audit.json`, `report.md`, `manifest.json`) with any API keys or private content removed.

## Extra context

Anything else that helps reproduce the problem. Do not include secrets, API keys, or personal data.
