#!/usr/bin/env python3
"""Validate Arguo skill packages.

Checks structure and standing style rules for skill folders under skill/:

- SKILL.md exists and has YAML frontmatter with name and description.
- The name is lowercase-hyphenated and matches the folder name.
- The description is under 1024 characters and SKILL.md stays under 300 lines.
- Every references/, templates/, or examples/ path the SKILL.md body points
  to actually exists in the package.
- Reference files stay within the 60 to 150 line budget; templates stay at
  or above 40 lines; examples stay at or above 60 lines; README.md exists.
- skill/arguo additionally requires its canonical 20 references, 5
  templates, and 2 examples.
- Authored files contain no em dashes, no en dashes, and no emoji.

Standard library only. Exits 0 when clean, 1 on any error.

Usage: python scripts/validate_skill.py [skill-folder ...]
  (no arguments defaults to skill/arguo; pass one or more folders, or
  "all" to validate every folder under skill/)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED_REFERENCES = [
    "research-planning.md",
    "search-strategy.md",
    "primary-sources.md",
    "source-quality.md",
    "evidence-ledger.md",
    "citation-standards.md",
    "publication-dates.md",
    "contradiction-analysis.md",
    "claim-verification.md",
    "quantitative-research.md",
    "literature-reviews.md",
    "technical-research.md",
    "market-research.md",
    "historical-research.md",
    "policy-research.md",
    "uncertainty-and-limitations.md",
    "report-writing.md",
    "privacy-and-safety.md",
    "prompt-injection-defense.md",
    "troubleshooting.md",
]

EXPECTED_TEMPLATES = [
    "research-plan-template.md",
    "evidence-ledger-template.md",
    "source-assessment-template.md",
    "contradiction-table-template.md",
    "report-template.md",
]

EXPECTED_EXAMPLES = [
    "example-basic-factual.md",
    "example-insufficient-evidence.md",
]

DASH_CODEPOINTS = {0x2014, 0x2013}  # em dash, en dash
EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),
    (0x2600, 0x27BF),
    (0x2B00, 0x2BFF),
    (0x1F1E6, 0x1F1FF),
    (0xFE00, 0xFE0F),
)

REFERENCE_LINE_MIN = 60
REFERENCE_LINE_MAX = 150
TEMPLATE_LINE_MIN = 40
EXAMPLE_LINE_MIN = 60

POINTER_PATTERN = re.compile(r"\b(?:references|templates|examples)/[\w.-]+\.md")


def is_emoji(codepoint: int) -> bool:
    return any(low <= codepoint <= high for low, high in EMOJI_RANGES)


def read_frontmatter(path: Path) -> tuple[dict[str, str], int]:
    """Return frontmatter fields and the line index where the body starts."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with a --- frontmatter block")
    fields: dict[str, str] = {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    if end is None:
        raise ValueError("frontmatter block is not closed with ---")
    return fields, end + 1


def check_forbidden_characters(path: Path, problems: list[str]) -> None:
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        for char in line:
            cp = ord(char)
            if cp in DASH_CODEPOINTS:
                problems.append(
                    f"{path}:{lineno}: forbidden dash character U+{cp:04X}"
                )
            elif is_emoji(cp):
                problems.append(
                    f"{path}:{lineno}: forbidden emoji codepoint U+{cp:04X}"
                )


def validate_folder(root: Path, problems: list[str]) -> dict[str, int]:
    """Validate one skill folder; append problems; return summary stats."""
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        problems.append(f"{root}: missing SKILL.md")
        return {"references": 0, "templates": 0, "examples": 0}

    try:
        fields, body_start = read_frontmatter(skill_md)
    except ValueError as exc:
        problems.append(f"{skill_md}: {exc}")
        return {"references": 0, "templates": 0, "examples": 0}

    name = fields.get("name", "")
    if name != root.name:
        problems.append(
            f"{root}: frontmatter name {name!r} does not match folder name"
        )
    if not name or name != name.lower() or " " in name or "_" in name:
        problems.append(f"{root}: frontmatter name {name!r} is not lowercase-hyphenated")

    description = fields.get("description", "")
    if not description:
        problems.append(f"{root}: frontmatter description is missing")
    elif len(description) >= 1024:
        problems.append(
            f"{root}: frontmatter description is {len(description)} chars (limit 1024)"
        )

    skill_lines = len(skill_md.read_text(encoding="utf-8").splitlines())
    if skill_lines >= 300:
        problems.append(f"{root}: SKILL.md has {skill_lines} lines (must stay under 300)")

    if not (root / "README.md").is_file():
        problems.append(f"{root}: missing README.md")

    # Every references/, templates/, or examples/ path the SKILL.md body
    # points to must exist inside the package.
    body_text = "\n".join(skill_md.read_text(encoding="utf-8").splitlines()[body_start:])
    pointers = sorted(set(POINTER_PATTERN.findall(body_text)))
    for pointer in pointers:
        if not (root / pointer).is_file():
            problems.append(f"{root}: SKILL.md points to missing file {pointer}")

    # Line budgets for every package file in each subfolder.
    counts = {"references": 0, "templates": 0, "examples": 0}
    for subdir, minimum, maximum in (
        ("references", REFERENCE_LINE_MIN, REFERENCE_LINE_MAX),
        ("templates", TEMPLATE_LINE_MIN, None),
        ("examples", EXAMPLE_LINE_MIN, None),
    ):
        folder = root / subdir
        if not folder.is_dir():
            problems.append(f"{root}: missing {subdir}/ folder")
            continue
        for path in sorted(folder.glob("*.md")):
            count = len(path.read_text(encoding="utf-8").splitlines())
            counts[subdir] += 1
            if count < minimum or (maximum is not None and count > maximum):
                budget = f"{minimum}-{maximum}" if maximum else f">= {minimum}"
                problems.append(
                    f"{root}: {subdir}/{path.name} has {count} lines (budget {budget})"
                )

    # Canonical file expectations for the original arguo skill.
    if root.name == "arguo":
        for filename in EXPECTED_REFERENCES:
            if not (root / "references" / filename).is_file():
                problems.append(f"{root}: missing references/{filename}")
        for filename in EXPECTED_TEMPLATES:
            if not (root / "templates" / filename).is_file():
                problems.append(f"{root}: missing templates/{filename}")
        for filename in EXPECTED_EXAMPLES:
            if not (root / "examples" / filename).is_file():
                problems.append(f"{root}: missing examples/{filename}")

    for path in sorted(root.rglob("*.md")):
        check_forbidden_characters(path, problems)

    return counts


def main(argv: list[str]) -> int:
    repo = Path(__file__).resolve().parent.parent
    args = argv[1:]
    if not args:
        args = ["arguo"]
    if args == ["all"]:
        targets = sorted(p for p in (repo / "skill").iterdir() if p.is_dir())
    else:
        targets = []
        for item in args:
            path = Path(item)
            if not path.is_absolute():
                path = repo / path
            if not path.is_dir() and not item.startswith("/") and "/" not in item:
                path = repo / "skill" / item
            if not path.is_dir():
                print(f"error: {path} is not a skill folder", file=sys.stderr)
                return 1
            targets.append(path)

    problems: list[str] = []
    totals = {"references": 0, "templates": 0, "examples": 0}
    for root in targets:
        counts = validate_folder(root, problems)
        for key in totals:
            totals[key] += counts[key]

    if problems:
        print(f"FAILED: {len(problems)} problem(s)")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(f"OK: {len(targets)} skill package(s) passed structure, budget, and style checks")
    for root in targets:
        print(f"- {root}")
    print(
        f"- totals: {totals['references']} references, "
        f"{totals['templates']} templates, {totals['examples']} examples"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
