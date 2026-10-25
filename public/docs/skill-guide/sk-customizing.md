---
title: Customizing the Skill
description: How to adapt the arguo skill for a domain, keep SKILL.md small, and what must not change.
group: skill-guide
slug: sk-customizing
order: 4
---

Domain depth lives in references/. To adapt the skill for a domain, add a reference file such as energy-research.md, keep it within the 60 to 150 line budget enforced by the validator, and point to it from the domain list in section 10 of SKILL.md, alongside literature-reviews.md and the other domain extensions. A domain rubric extends the ten criteria in references/source-quality.md with domain-specific checks, for example trial registration for clinical evidence or filing standards for corporate data. Do not replace the ten criteria; add to them, because the rubric mirrors the SourceAssessment model in the Python package, and the source-assessment template expects those fields.

Keep SKILL.md under 300 lines. The validator fails the package if it grows beyond that. Put detail in a reference file and add a one-line pointer instead of expanding a body section. Every new file must avoid em dashes, en dashes, and emoji, which are standing style rules of this project and checked by scripts/validate_skill.py.

Portability comes from a few properties worth preserving: the skill is markdown only, so it works in any agent that reads files; all cross-references are relative paths inside the folder, so moving or renaming the parent directory breaks nothing; the frontmatter uses only the two common fields, name and description, and runtimes that want extra fields such as version or license can add them without touching the body.

Do not change the frontmatter name field. It must stay arguo, lowercase-hyphenated, and identical to the folder name; the validator and most runtimes treat a mismatch as a broken package. Keep the description under 1024 characters and preserve its activation triggers, because that text is what makes the skill load on research tasks. Keep the output contract section intact: the four required report elements are the point of the skill. If you change ledger fields in references/evidence-ledger.md, keep them aligned with the EvidenceRecord model and the JSONL variant of the ledger template so runs can still feed the Python toolkit.
