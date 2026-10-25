---
title: Arguo Skill Overview
description: What the arguo Agent Skill is, what it does, and when an agent should load it.
group: skill-guide
slug: sk-overview
order: 1
---

An Agent Skill, following the conventions popularized by agentskills.io, is a folder containing a SKILL.md file with YAML frontmatter. The frontmatter carries a name and a description that the agent runtime uses to decide when the skill activates. The body of SKILL.md holds the method, and optional supporting files such as references, templates, and examples are loaded only when the instructions point to them. Skills are plain files: no build step, no runtime, no network access at load time.

The arguo skill is a text-only research method. It turns web access into auditable research: every claim is recorded with its source, corroboration is checked through independence groups, contradictions are classified instead of hidden, and confidence is stated qualitatively with reasons. The method has 12 steps, from understanding the question and planning subquestions, through searching in rounds, recording evidence rows, evaluating source quality on a ten-criterion rubric, and auditing citations, to reporting with explicit uncertainty. The output contract requires four things in every report: a claim-evidence table, a source list with URLs and retrieval dates, an explicit limitations section, and qualitative confidence with reasons. Insufficient evidence is a supported verdict, not a failure.

An agent should load this skill when the task involves rigorous research questions, fact-checking, literature reviews, cited reports, claim verification, or investigating conflicting information. It fits whenever the deliverable needs traceable evidence, auditable citations, source-quality assessment, or honest handling of uncertainty.

The skill is not needed for casual summaries, creative writing, or questions where a single well-known fact is enough. It adds discipline and bookkeeping, and that overhead pays off only when the report must show its evidence.

The skill lives at skill/arguo in this repository. SKILL.md stays under 300 lines; depth lives in 20 reference files, five templates, and two worked examples, all markdown. Two companion packages extend the toolkit: skill/arguo-curator teaches an agent how to curate and validate the resource catalog, and skill/arguo-source-audit teaches an agent how to audit the citations in an existing report.
