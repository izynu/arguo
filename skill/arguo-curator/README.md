# arguo-curator

An Agent Skill package for curating the Arguo resource catalog: the
JSONL authoring files under data/resources/ that
scripts/build_resource_catalog.py compiles into the shipped catalog in
catalog/. The skill teaches an agent how to pick real and certain
candidates, write schema-conformant records, dedupe ids and urls,
validate with the repo's real scripts, and run the link verification
workflow that promotes documented records to verified.

The skill is text only. It has no code dependencies beyond the repo's
own validation scripts and works with any agent that can read files,
check facts about public resources, and write JSONL.

## Package layout

    skill/arguo-curator/
      SKILL.md                                        method and rules
      README.md                                       this file
      references/schema-fields.md                     exact field constraints
      references/category-selection.md                the 50-key taxonomy and candidate standard
      references/dedupe-and-collisions.md             normalization and resolution rules
      references/description-quality.md               free-text field quality
      references/validation-workflow.md               the validator commands and fixes
      references/link-checking.md                     live checks and promotion to verified
      templates/record-authoring-checklist-template.md   per-run fill-in checklist
      templates/curation-run-report-template.md          fixed run report format
      examples/example-mini-curation-run.md           illustrative three-record batch

## Installation

Copy the package into your agent's documented skills path:

    mkdir -p .claude/skills
    cp -r skill/arguo-curator .claude/skills/arguo-curator

Or reference it from any other documented skills directory your agent
uses. The paths inside the skill are relative to the repo root, so run
curation commands from the repo root after installation.

## Verification

These are the real commands the skill relies on. Run them from the repo
root.

Structural self-check of the skill package: pure ASCII decode, no em
dash or en dash characters, no emoji, and line budgets (references 60
to 150 lines, templates at least 40, SKILL.md body under 300):

    python3 - <<'EOF'
    import pathlib, sys
    root = pathlib.Path("skill/arguo-curator")
    bad = []
    dashes = {chr(0x2013), chr(0x2014)}
    for p in sorted(root.rglob("*.md")):
        t = p.read_text()
        rel = p.relative_to(root)
        n = len(t.splitlines())
        if not t.isascii() or any(c in dashes for c in t) or any(ord(c) > 0x2BFF for c in t):
            bad.append(f"{rel}: non-ASCII, dash, or emoji")
        if "references" in p.parts and not (60 <= n <= 150):
            bad.append(f"{rel}: {n} lines outside 60-150")
        if "templates" in p.parts and n < 40:
            bad.append(f"{rel}: {n} lines under 40")
    print("\n".join(bad) if bad else "OK: style and line budgets pass")
    sys.exit(1 if bad else 0)
    EOF

Catalog validators (the commands a curation run must pass):

    python3 scripts/validate_catalog_file.py data/resources/<file>.jsonl
    python3 scripts/validate_resources.py

Link checker (offline by default; --live makes real requests):

    python3 scripts/check_links.py

Note: scripts/validate_skill.py validates any skill package. Run it
with no arguments to check the arguo package, pass one or more folder
names such as skill/arguo-curator to check specific packages, or pass
the word all to check every package under skill/.

## Sample invocations

1. "Add 5 new government statistics resources to
   data/resources/gov-6.jsonl, then validate the file and the whole
   catalog and report per-category counts and skipped candidates."
2. "Review data/resources/academic-2.jsonl for dedupe collisions and
   style violations using the arguo-curator skill, and report anything
   that should go to the maintainer."
3. "Run the link verification workflow for the newest batch: offline
   check first, then a live check capped at 50 URLs, and promote only
   documented records whose canonical_url classified ok, setting
   last_checked to today."

## Honest limitations

- The skill cannot verify facts offline. Where the sandbox has no
  network, candidates stay unconfirmed and uncertain ones must be
  skipped; the verification_status stays "documented".
- The verified status means only that the canonical_url answered in a
  live check on the recorded date. It is not a statement about content
  quality, license accuracy, or long-term availability.
- scripts/validate_catalog_file.py uses a built-in mirror of the JSON
  Schema rules; if data/schemas/resource.schema.json changes, the
  mirror and this skill's field reference need a maintainer update.
- The link checker reads the built catalog (catalog/catalog.json), not
  the authoring files, so new records are link-checkable only after a
  catalog build or an explicit --catalog target.
- The example in examples/ is illustrative and labeled as such; its
  validator output is a sketch of the expected format, not captured
  output.
- Category keys, enum values, and the taxonomy size can change with
  data/categories.json; the skill defers to the file, not to this
  README.
