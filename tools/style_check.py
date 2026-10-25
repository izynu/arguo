#!/usr/bin/env python3
"""Style check for authored copy: no em dashes, no en dashes, no emoji.

Used by pre-commit (.pre-commit-config.yaml) and CI (.github/workflows/ci.yml).
Scans the given paths (or a default set) for:
  - em dash, U+2014
  - en dash, U+2013
  - emoji characters and the invisible formatting characters that emoji
    sequences use (variation selectors, zero-width joiners)

Prints one line per offender and exits 1 when any are found. Stdlib only.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Default scan set for this repository.
DEFAULT_TARGETS = [
    "docs",
    "skill",
    "src/app",
    "src/components/site",
    "README.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
]

SCAN_SUFFIXES = {
    ".md",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".svg",
    ".toml",
    ".cff",
    ".jsonl",
}

SKIP_DIRS = {".git", "node_modules", ".next", ".venv", "__pycache__"}

DASHES = {
    0x2014: "em dash",
    0x2013: "en dash",
}

EMOJI_RANGES = (
    (0x1F000, 0x1FAFF),  # pictographs, emoticons, transport, supplemental symbols
    (0x2600, 0x27BF),  # misc symbols and dingbats
    (0x2B00, 0x2BFF),  # misc symbols and arrows (stars, circles)
    (0xFE00, 0xFE0F),  # variation selectors
    (0x200B, 0x200D),  # zero width space, non-joiner, joiner
)


def classify(char: str) -> str | None:
    """Return a rule name for a forbidden character, or None."""
    point = ord(char)
    if point in DASHES:
        return DASHES[point]
    for low, high in EMOJI_RANGES:
        if low <= point <= high:
            return "emoji or emoji formatting character"
    return None


def iter_files(target: Path):
    if target.is_file():
        yield target
        return
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SCAN_SUFFIXES:
            continue
        yield path


def main(argv: list[str]) -> int:
    targets = argv[1:] if len(argv) > 1 else list(DEFAULT_TARGETS)
    offenders = 0
    for raw in targets:
        target = Path(raw)
        if not target.is_absolute():
            target = REPO_ROOT / target
        if not target.exists():
            print(f"style-check: target not found: {raw}")
            return 1
        for path in iter_files(target):
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for line_no, line in enumerate(text.splitlines(), start=1):
                for col, char in enumerate(line, start=1):
                    rule = classify(char)
                    if rule is None:
                        continue
                    offenders += 1
                    snippet = line.strip()
                    if len(snippet) > 80:
                        snippet = snippet[:77] + "..."
                    print(
                        f"{path.relative_to(REPO_ROOT)}:{line_no}:{col}: "
                        f"{rule} (U+{ord(char):04X}) in: {snippet}"
                    )
    if offenders:
        print(f"style-check: {offenders} offender(s) found. See the project style rules.")
        return 1
    print("style-check: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
