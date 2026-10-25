# Publishing Arguo

Arguo is an evidence-first open research intelligence toolkit. This archive
contains the complete repository: a Next.js documentation site with a
searchable catalog explorer, a Python research engine with an offline test
suite, three Agent Skill packages, a schema-validated resource catalog of
1,570 records across 50 categories, docs, evals, and all build and
validation scripts.

## Requirements

- git
- Node.js 20 or later, plus bun (recommended) or npm
- Python 3.11 or later for the engine, tests, and scripts

## Run it locally

1. Unzip the archive and open the folder in VS Code.
2. Install web dependencies and start the dev server:

   ```bash
   bun install
   bun run dev
   ```

   Then open http://localhost:3000. With npm instead: `npm install` and
   `npm run dev`.

3. Run the Python test suite and validators from the repo root:

   ```bash
   python3 -m pytest tests/
   python3 scripts/validate_resources.py
   python3 scripts/validate_skill.py all
   python3 tools/style_check.py
   ```

The site runs without any API keys. The Python engine also runs fully
offline in demo mode; live providers are optional and need your own keys.

## Publish to GitHub

The archive ships without git history, so initialize a fresh repository:

```bash
git init -b main
git add -A
git commit -m "Import Arguo 0.1.0"
git remote add origin git@github.com:YOUR-USERNAME/arguo.git
git push -u origin main
```

Create the empty `arguo` repository on GitHub first (no README, no
license, no gitignore) so the push lands cleanly. Then in the repo
settings:

1. Set the description and topics, for example: research, evidence,
   citations, fact-checking, osint, catalog, agent-skills.
2. Confirm the detected license matches the included LICENSE file.
3. Keep Issues enabled; add Discussions if you want community input.

## Release a version

```bash
git tag -a v0.1.0 -m "Arguo 0.1.0"
git push origin v0.1.0
```

Then create a GitHub release from the tag and attach the archive zip.
Regenerate the archives any time with `make package` (writes
`public/arguo-latest.zip` and `public/arguo-latest.tar.gz` from the
current HEAD). The repository also tracks a ready-made copy of both
archives under `public/` for direct download from the site footer.

## Hosting the site

The web app is a standard Next.js 16 App Router project. It deploys to
any Node host (Vercel, Railway, Fly.io, or a VPS running
`bun run build && bun run start`). The catalog data under `public/data`
is served statically, so the explorer works on static hosts that support
the Next.js server output.

## Where things live

| Path | Contents |
| --- | --- |
| `src/` | Next.js site: home, explorer, docs viewer, stats |
| `python/arguo/` | Python research engine and CLI |
| `skill/` | Three Agent Skill packages: arguo, arguo-curator, arguo-source-audit |
| `data/` | Resource catalog source files (JSONL), schema, categories |
| `catalog/` | Built catalog outputs (JSON, JSONL, stats) |
| `docs/` | Markdown documentation mirrored into the site |
| `evals/` | Evaluation harness cases |
| `scripts/`, `tools/` | Build, validation, link-check, and style scripts |
| `tests/` | Offline test suite |
