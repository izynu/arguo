# Arguo skill

An arguo research method packaged as an Agent Skill. The skill turns
an agent's web access into auditable research: every claim recorded with its
source, corroboration checked through independence groups, contradictions
classified instead of hidden, and confidence reported qualitatively with
reasons. Insufficient evidence is a supported outcome, not a failure.

The skill is text only: markdown files, no code dependencies, no network
calls of its own. It works with any agent that can read files and search the
web.

## Package contents

- `SKILL.md`: the method, loaded when the skill activates. Keep it under 300
  lines; details live in the references.
- `references/`: 20 files with the depth: planning, search, primary sources,
  source quality, the ledger schema, citations, dates, contradictions,
  claim verification, quantitative work, literature reviews, technical,
  market, historical, and policy research, uncertainty, report writing,
  privacy, injection defense, and troubleshooting.
- `templates/`: five fill-in templates: research plan, evidence ledger,
  source assessment, contradiction table, and report.
- `examples/`: two worked examples: a basic factual question, and an
  insufficiency verdict handled honestly.

## Installation

Agents load skills from a skills directory. Copy the whole folder, keeping
the directory name:

```bash
# Claude Code style agents
mkdir -p .claude/skills
cp -r /path/to/arguo .claude/skills/arguo

# Agents with a documented skills path: copy into that path instead, e.g.
cp -r /path/to/arguo <agent-skills-path>/arguo
```

Requirements:

- The folder must be named `arguo` and contain `SKILL.md` at its
  root. Most agent runtimes read the YAML frontmatter (`name`,
  `description`) to decide when the skill activates.
- No other installation steps: no dependencies, no build, no network access
  needed at load time.

If your agent has no skill mechanism, the skill still works as a prompt
package: paste or attach `SKILL.md` at the start of a research session and
instruct the agent to read the referenced files from the same folder as
needed. The pointers in `SKILL.md` ("Read references/<file>.md when ...")
are the progressive-disclosure mechanism; the agent reads only the depth it
needs.

## Verification

The repo ships a validator. From the repository root:

```bash
python scripts/validate_skill.py skill/arguo
```

The script checks, and exits nonzero on failure:

- `SKILL.md` exists, has frontmatter with `name` and `description`, the name
  is lowercase-hyphenated and matches the folder, and the description is
  under 1024 characters.
- The expected references, templates, and examples exist.
- Reference files stay within the 60 to 150 line budget.
- Authored files contain no em dashes, no en dashes, and no emoji, which are
  standing style rules of this project.

Manual checks, if you prefer not to run the script:

```bash
wc -l skill/arguo/SKILL.md                                  # under 300
grep -c "references/" skill/arguo/SKILL.md                  # 8 or more
grep -rPn "\x{2014}|\x{2013}" skill/arguo/                  # no output
ls skill/arguo/references/ | wc -l                          # 20
```

## Usage

The description in the frontmatter triggers the skill on research tasks.
Sample invocations:

1. "Use the arguo skill to research whether skipping breakfast
   affects concentration, and produce a cited report with a claim-evidence
   table."
2. "Fact-check these five claims about electric vehicle battery life with
   the arguo skill, and report confidence per claim."
3. "Use the arguo skill to run a literature review on remote work
   productivity, with a documented search protocol."
4. "Investigate with the arguo skill why published figures for
   X disagree, and give me a contradiction table with your resolution."
5. "Use the arguo skill to research this market question; if the
   evidence is insufficient, tell me what you could not establish and what
   searches would settle it."

Expected deliverable shape, enforced by the skill's output contract:

- a claim-evidence table with per-claim verification status,
- a source list with URLs and retrieval dates,
- an explicit limitations section,
- confidence stated qualitatively with reasons.

## The catalog

The repository ships a curated catalog of research resources at
`data/resources/`, categorized by the keys in `data/categories.json`. The
skill instructs the agent to consult that catalog on demand for strong
starting points in categories like government statistics or law; the catalog
is searched when needed and is deliberately not embedded in `SKILL.md`.
Sources found through the catalog still go through the same quality rubric
as anything else.

## Customization

- Domain depth lives in `references/`. Add a domain file (for example
  `energy-research.md`) and point to it from the domain list in section 10
  of `SKILL.md`. Keep new files within the 60 to 150 line budget and free of
  the characters the validator rejects.
- The ten-criterion rubric in `references/source-quality.md` mirrors the
  `SourceAssessment` model in the Python package. If you change criteria,
  change both, and the source assessment template.
- Ledger fields in `references/evidence-ledger.md` match the
  `EvidenceRecord` model under `python/arguo`. Keep the JSONL
  variant of the ledger template aligned with that schema so runs can feed
  the toolkit.
- Examples are teaching artifacts labeled as illustrative; replace them with
  real runs only if you can cite real, checked sources.

## Portability

- Markdown only: works on any file system, in any agent that reads files.
  No scripts are executed by the skill itself, so nothing to sandbox.
- The frontmatter uses the two common fields (`name`, `description`). Runtimes
  that want extra fields (version, license, metadata files) can have them
  added without touching the body.
- All cross-references are relative paths inside the folder; moving or
  renaming the parent directory does not break anything.
- The skill assumes the agent can fetch web content and write files. Without
  web access it still structures planning, ledger discipline, and reporting,
  but cannot gather new evidence; the limitations section should say so.

## License and scope

Part of the Arguo repository. The skill organizes and cites
evidence; it does not provide legal, medical, or financial advice, and the
policy reference file states that boundary explicitly.
