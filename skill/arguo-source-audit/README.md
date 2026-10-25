# arguo-source-audit skill

An Agent Skill for auditing the citations of an existing document: a
report, article, brief, or bibliography. For every citation the method
checks three things: does the link work today, does the cited source
actually support the claim it is attached to, and is the source good
enough for that claim. It produces an audit table with one row per
citation, per-citation verdicts from a closed vocabulary, one overall
verdict (pass, pass-with-issues, needs-rework, or cannot-audit), and a
mandatory limitations section.

The skill is text only: markdown files, no code dependencies, no network
calls of its own. It works with any agent that can read files and fetch
web pages.

## Package contents

- `SKILL.md`: the eight-step audit method plus the output contract. Keep
  it under 300 lines; the depth lives in the references.
- `references/`: six files: citation extraction, link classification,
  passage verification, misattribution patterns, date checks, and the
  audit report format with the verdict vocabularies and the compact
  ten-criterion re-grade rubric.
- `templates/`: two fill-in templates: the audit report and the
  per-citation row (the evidence block behind each table row).
- `examples/`: one worked walkthrough, clearly labeled illustrative, that
  audits a short fictional report with three citations and lands on an
  honest pass-with-issues verdict.

## Installation

Agents load skills from a skills directory. Copy the whole folder, keeping
the directory name:

```bash
# Claude Code style agents
mkdir -p .claude/skills
cp -r /path/to/arguo-source-audit .claude/skills/arguo-source-audit

# Agents with a documented skills path: copy into that path instead, e.g.
cp -r /path/to/arguo-source-audit <agent-skills-path>/arguo-source-audit
```

Requirements:

- The folder must be named `arguo-source-audit` and contain `SKILL.md` at
  its root. Runtimes read the YAML frontmatter (`name`, `description`) to
  decide when the skill activates.
- No other installation steps: no dependencies, no build step, nothing to
  run at load time.

The skill works standalone. If the arguo skill is installed alongside it,
the pointer in step 6's companion reference to the full ten-criterion
rubric (in `skill/arguo/references/source-quality.md`) resolves; without
it, the compact rubric in `references/audit-report-format.md` carries the
same vocabulary and level words.

## Structural self-check

A structural self-check, not a semantic one: it verifies file presence,
line budgets, ASCII-only content with no em dashes, en dashes, or emoji,
and that every relative path mentioned in `SKILL.md` exists. From the
repository root:

```bash
python3 - <<'EOF'
import pathlib, re, sys
root = pathlib.Path("skill/arguo-source-audit")
problems = []
files = sorted(root.rglob("*.md"))
for p in files:
    text = p.read_text(encoding="utf-8")
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        problems.append(f"{p}: non-ASCII content")
    for i, ch in enumerate(text):
        if ord(ch) in (0x2013, 0x2014) or ord(ch) >= 0x1F000:
            problems.append(f"{p}: forbidden character U+{ord(ch):04X}")
for p in sorted((root / "references").glob("*.md")):
    n = len(p.read_text(encoding="utf-8").splitlines())
    if not 60 <= n <= 150:
        problems.append(f"{p}: {n} lines (budget 60-150)")
for p in sorted((root / "templates").glob("*.md")):
    if len(p.read_text(encoding="utf-8").splitlines()) < 40:
        problems.append(f"{p}: template under 40 lines")
skill = root / "SKILL.md"
lines = skill.read_text(encoding="utf-8").splitlines()
if len(lines) >= 300:
    problems.append(f"SKILL.md: {len(lines)} lines (must stay under 300)")
for path in sorted(set(re.findall(r"(?:references|templates|examples)/[\w.-]+\.md", skill.read_text(encoding='utf-8')))):
    if not (root / path).is_file():
        problems.append(f"SKILL.md mentions missing path {path}")
print("\n".join(problems) if problems else f"OK: {len(files)} files pass structure and style checks")
sys.exit(1 if problems else 0)
EOF
```

## Sample invocations

1. "Audit every citation in reports/community-solar-brief.md and give me
   the audit table with per-citation verdicts."
2. "Run a link rot check on the bibliography of article-draft.md: classify
   each link and list which citations are dead, moved, or bot-blocked."
3. "Verify that the sources cited in our published market brief actually
   support the claims, re-grade them on the ten-criterion rubric, and tell
   me honestly whether the brief holds up."

The skill activates on tasks like auditing citations in a report or
article, verifying that cited sources support claims, link rot checks,
misattribution detection, and re-grading source quality after publication.

## Honest limitations

- The audit sees only what the agent can fetch during the run. Sources
  that are bot-blocked, paywalled past anything usable, or unreachable
  produce cannot-audit rows, not guesses, and a report full of blocked
  sources produces an overall cannot-audit verdict rather than a
  comfortable one.
- One retry per transient failure; the skill does not solve challenges,
  enter credentials, or otherwise break through access controls.
- Fetch coverage depends on the agent's fetch mechanism: scripted pages,
  embedded documents, and content behind interactive elements may be
  invisible to it, and the audit says so instead of guessing.
- The skill judges citations against sources as they are today. What a
  page contained when the document was written is established only where
  evidence survives (archive snapshots, redirect histories); otherwise it
  is recorded as unknown.
- Examples in this package are illustrative and use representative
  domains; no file in the package reports live check results.
- The self-check above verifies structure and style only. It cannot check
  whether an audit's judgments were correct.

## Relationship to the arguo skill

The arguo skill produces researched documents with traceable evidence.
This skill examines documents after the fact, including documents arguo
itself produced. Both share the ten-criterion source quality rubric
vocabulary, so a re-grade here reads the same way as a grade made during
research. Use arguo to write, and arguo-source-audit to check what was
written.
