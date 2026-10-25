---
title: Skill Troubleshooting
description: Fixes for a skill that will not activate, missing references, validator failures, and style rule violations.
group: skill-guide
slug: sk-troubleshooting
order: 5
---

The skill does not activate. Activation is driven by the description field in the SKILL.md frontmatter, so check three things. First, confirm the folder sits in the skills directory the agent actually reads, for example .claude/skills/arguo. Second, confirm the frontmatter is intact: the file must start with a --- block containing name and description. Third, tune the description by adding the phrases your requests use, such as fact-check, literature review, or cited report, and keep it under 1024 characters. If the agent has no skill mechanism at all, paste SKILL.md into the session and tell it to read referenced files from the same folder.

A reference file is not found. All pointers are relative paths such as references/source-quality.md, resolved inside the skill folder. The folder name arguo and its internal layout (references/, templates/, examples/) must be preserved by the copy. A missing file usually means a partial copy or a renamed subfolder; run the validator to list missing paths. Renaming the folder itself also breaks the frontmatter name match that most runtimes check.

The validator fails. python scripts/validate_skill.py exits nonzero and prints one line per problem. Common failures: SKILL.md at or above 300 lines, a reference file outside the 60 to 150 line budget, a missing template or example, a frontmatter name that does not match the folder or is not lowercase-hyphenated, and a description of 1024 characters or more. Fix each listed file, then rerun until it reports OK.

Style rule violations. The validator rejects em dash (U+2014), en dash (U+2013), and emoji codepoints in every markdown file of the package. Replace an em dash with a comma, colon, or hyphen, and remove emoji rather than replacing them with lookalike characters. Find offenders with grep -rPn "\x{2014}|\x{2013}" over the skill folder. After edits, rerun the validator so the package returns to a passing state before redistribution.
