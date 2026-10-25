---
title: Support
description: Where to ask questions about Arguo, how to report bugs well, and what response times to expect.
group: project
slug: pj-support
order: 8
---

Where to ask. For questions about using the toolkit, open a thread in GitHub Discussions on the arguo repository. For concrete bugs and feature requests, open a GitHub Issue. Both URLs are placeholders marked TODO for the repository owner until the repository is published; this page will list the direct links then. There is no chat, forum, or paid support channel.

How to report a bug. Use the bug report template on the issue form. Include:

- What you ran: the exact command or script, the profile, and the package version.
- Environment: operating system, Python version, which search and model providers were in use, and whether the run was offline.
- What happened: expected versus actual behavior, plus the full error text.
- Artifacts: the run manifest and audit report from runs/ for the failing run. Keep the research question in if you are comfortable with it; it helps reproduction.
- Logs: console output with secrets removed. The logging layer redacts registered keys, but check before pasting.

Privacy note: do not paste API keys, private URLs, or confidential material into issues. Issues are public.

Response expectations. Support is best effort by volunteers: no response-time promises, no guaranteed fixes. Issues may be closed as stale after inactivity, which is not a judgment about the report. Before filing, please search existing issues and read the docs under docs/, since setup and configuration questions are often answered there already.
