#!/usr/bin/env python3
"""Build the documentation index and llms.txt files from docs/ markdown.

Reads docs/**/*.md, parses the simple YAML frontmatter (the block between
the opening and closing --- lines; each line is "key: value"), and writes:

  public/data/docs-index.json  JSON array of {"group", "slug", "title",
                               "description", "order", "path"} entries sorted
                               by group then order (indent 1)
  public/llms.txt              "# Arguo" header, a short project
                               description, then "## <group>" sections listing
                               "- <title>: <description> (docs/<group-dir>/<file>)"
  public/llms-full.txt         header plus every page's full markdown, pages
                               separated by blank line "---" separators, each
                               under a "# <title>" heading

The public/data directory is created when missing. Files without valid
frontmatter are skipped and reported. No dependency beyond the stdlib.

Usage: python3 scripts/generate_docs.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
PUBLIC_DIR = ROOT / "public"
REQUIRED_FIELDS = ("title", "description", "group", "slug", "order")

PROJECT_TITLE = "Arguo"
PROJECT_TAGLINE = (
    "An open research intelligence toolkit: an evidence ledger, citation "
    "auditing, and a curated resource catalog. This file lists the "
    "documentation pages with their repo-relative paths."
)


def parse_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """Return (frontmatter dict, body) or None when the file has none."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return None
    meta: dict[str, str] = {}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return meta, body


def load_pages() -> tuple[list[dict], list[str]]:
    pages: list[dict] = []
    skipped: list[str] = []
    for path in sorted(DOCS_DIR.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            skipped.append(f"{path.relative_to(ROOT)}: unreadable ({exc})")
            continue
        parsed = parse_frontmatter(text)
        if parsed is None:
            skipped.append(f"{path.relative_to(ROOT)}: no frontmatter block")
            continue
        meta, body = parsed
        missing = [field for field in REQUIRED_FIELDS if not meta.get(field)]
        if missing:
            skipped.append(
                f"{path.relative_to(ROOT)}: frontmatter missing {', '.join(missing)}"
            )
            continue
        try:
            order = int(str(meta["order"]).strip())
        except ValueError:
            skipped.append(f"{path.relative_to(ROOT)}: order is not an integer")
            continue
        pages.append({
            "group": meta["group"],
            "slug": meta["slug"],
            "title": meta["title"],
            "description": meta["description"],
            "order": order,
            "path": path.relative_to(ROOT).as_posix(),
            "_body": body,
        })
    pages.sort(key=lambda page: (page["group"], page["order"], page["path"]))
    return pages, skipped


def write_json_index(pages: list[dict]) -> Path:
    out_dir = PUBLIC_DIR / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    index = [
        {key: page[key] for key in ("group", "slug", "title", "description", "order", "path")}
        for page in pages
    ]
    target = out_dir / "docs-index.json"
    target.write_text(
        json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return target


def group_pages(pages: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for page in pages:
        grouped.setdefault(page["group"], []).append(page)
    return grouped


def write_llms_txt(pages: list[dict]) -> Path:
    grouped = group_pages(pages)
    lines: list[str] = [f"# {PROJECT_TITLE}", "", PROJECT_TAGLINE, ""]
    for group in sorted(grouped):
        lines.append(f"## {group}")
        lines.append("")
        for page in grouped[group]:
            lines.append(
                f"- {page['title']}: {page['description']} ({page['path']})"
            )
        lines.append("")
    target = PUBLIC_DIR / "llms.txt"
    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return target


def write_llms_full_txt(pages: list[dict]) -> Path:
    header = f"# {PROJECT_TITLE}\n\n{PROJECT_TAGLINE}"
    blocks = [
        f"# {page['title']}\n\n{page['_body'].rstrip()}"
        for page in pages
    ]
    text = "\n\n---\n\n".join([header, *blocks])
    target = PUBLIC_DIR / "llms-full.txt"
    target.write_text(text.rstrip() + "\n", encoding="utf-8")
    return target


def mirror_markdown_pages(pages: list[dict]) -> tuple[int, int]:
    """Copy every indexed docs page to public/ so the site can fetch it.

    The docs viewer fetches /docs/<path> at runtime, so public/docs must
    mirror docs/ exactly. Copying from the same indexed page list keeps the
    two trees in sync and removes pages that were deleted or renamed.
    """
    removed = 0
    for old in PUBLIC_DIR.rglob("*.md"):
        source = ROOT / old.relative_to(PUBLIC_DIR)
        if not source.is_file():
            old.unlink()
            removed += 1
    copied = 0
    for page in pages:
        source = ROOT / page["path"]
        if not source.is_file():
            continue
        target = PUBLIC_DIR / page["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        copied += 1
    return copied, removed


def main() -> int:
    if not DOCS_DIR.is_dir():
        print(f"Error: docs directory not found: {DOCS_DIR}", file=sys.stderr)
        return 1
    pages, skipped = load_pages()
    if not pages:
        print("Error: no documentation pages with valid frontmatter were found.",
              file=sys.stderr)
        for note in skipped:
            print(f"  {note}", file=sys.stderr)
        return 1
    index_path = write_json_index(pages)
    llms_path = write_llms_txt(pages)
    full_path = write_llms_full_txt(pages)
    copied, mirrored_removed = mirror_markdown_pages(pages)
    groups = group_pages(pages)
    print(f"Indexed {len(pages)} page(s) across {len(groups)} group(s):")
    for group in sorted(groups):
        print(f"  {group}: {len(groups[group])} page(s)")
    for note in skipped:
        print(f"Skipped: {note}")
    print(f"Wrote {index_path}")
    print(f"Wrote {llms_path}")
    print(f"Wrote {full_path}")
    print(f"Mirrored {copied} markdown page(s) into {PUBLIC_DIR / 'docs'} ({mirrored_removed} stale removed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
