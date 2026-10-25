---
title: Installing the Skill
description: Where to copy the arguo skill folder, how to verify it, and sample invocations.
group: skill-guide
slug: sk-installing
order: 2
---

Agents load skills from a skills directory. Installation is a copy operation that keeps the directory name.

For Claude Code style agents, copy the folder into .claude/skills/ at the project root or in the home directory:

```bash
mkdir -p .claude/skills
cp -r /path/to/arguo .claude/skills/arguo
```

For agents with a documented project-level skills path, copy into that path instead:

```bash
cp -r /path/to/arguo <agent-skills-path>/arguo
```

Requirements are minimal. The folder must be named arguo and contain SKILL.md at its root. Most runtimes read the YAML frontmatter fields name and description to decide when the skill activates. There are no dependencies, no build step, and no network access needed at load time.

If your agent has no skill mechanism at all, the package still works as a prompt bundle: paste or attach SKILL.md at the start of a session and instruct the agent to read the referenced files from the same folder as needed.

Verify the installation with the repo validator:

```bash
python scripts/validate_skill.py all
```

The script is standard library only. It checks that SKILL.md exists with frontmatter, that the name is lowercase-hyphenated and matches the folder, that the description is under 1024 characters, that the 20 references, 5 templates, and 2 examples exist, that references stay within the 60 to 150 line budget, and that no em dashes, en dashes, or emoji appear in the markdown files. It exits nonzero and lists problems on failure. Run it with no arguments to validate the arguo package only, pass one or more skill folders to validate specific packages, or pass the word all to validate every package under skill/.

Sample invocations:

1. "Use the arguo skill to research whether skipping breakfast affects concentration, and produce a cited report with a claim-evidence table."
2. "Fact-check these five claims about electric vehicle battery life with the arguo skill, and report confidence per claim."
3. "Use the arguo skill to run a literature review on remote work productivity, with a documented search protocol."
