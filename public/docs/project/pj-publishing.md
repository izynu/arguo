---
title: Publishing Checklist
description: A numbered launch checklist for the repository owner, from repo creation to final checks.
group: project
slug: pj-publishing
order: 10
---

Launch checklist for the repository owner, in order.

1. Create the GitHub repository. Create arguo under your account, then push:

```bash
git init && git add . && git commit -m "Arguo 0.1.0"
git remote add origin git@github.com:izynu/arguo.git
git push -u origin main
```

Repository URLs already point at github.com/izynu/arguo. If the repository moves to another owner, update the URLs in pyproject.toml, CITATION.cff, and the docs pages.

2. Website deployment. Two options: GitHub Pages using .github/workflows/deploy-pages.yml, or any static host. The site is a Next.js app: for static hosting, set output: "export" in next.config.ts and build. For repository subpaths, set NEXT_PUBLIC_BASE_PATH (for example /arguo); for a custom domain at the zone root, no base path is needed.

3. Site identity. Configure the site name, repository URL, and deployment URL in src/lib/site-config.ts.

4. Favicon. The site uses app/icon.svg under the App Router icon convention. Confirm it is present in your checkout before launch.

5. Privacy and terms. The privacy policy and terms pages live at the hash routes #/privacy and #/terms. Confirm both render before launch.

6. Custom domain. Add DNS CNAME or A records per the GitHub Pages docs. When using Pages with a custom domain, add a CNAME file to public/ and enable HTTPS enforcement in repository settings.

7. Badge check. Confirm no "Made with AI" or similar badge appears anywhere in the site. A text search of src/ currently returns no matches; re-run before launch:

```bash
grep -ri "made with ai" src/ || echo clean
```

8. Final checks. Run make lint && make test && make validate. If the Makefile is not yet present in your checkout, run the direct equivalents:

```bash
bun run lint
python -m pytest
python scripts/validate_skill.py all
python scripts/validate_catalog_file.py data/resources/<file>.jsonl
python scripts/build_resource_catalog.py
```

The last command rebuilds the catalog outputs; diff the results against the committed files. Launch only when every step passes.
