# Deployment: publishing the Arguo repository and docs site

This is the operator-facing deployment guide. The docs-page version of this checklist lives at `docs/project/pj-publishing.md`; both cover the same ground, so keep them in sync when you change one.

## 1. Create the GitHub repository

1. Create a repository named `arguo` under your account or organization.
2. Push the project:

   ```bash
   git init && git add . && git commit -m "Arguo 0.1.0"
   git remote add origin git@github.com:izynu/arguo.git
   git push -u origin main
   ```

   The repository owner is [izynu](https://github.com/izynu). Repository URLs across the project already point at github.com/izynu/arguo.

## 2. Site deploy options

The site is a Next.js app in `src/`. Two supported options:

### Option A: GitHub Pages (included workflow)

`.github/workflows/deploy-pages.yml` deploys on every push to `main` and on manual dispatch:

1. Enable GitHub Pages in repository settings with the source set to "GitHub Actions".
2. The workflow sets `NEXT_OUTPUT=export` (next.config.ts reads this env var and switches from the default `standalone` output to a static export into `out/`) and `NEXT_PUBLIC_BASE_PATH=/{repository name}` so asset URLs work at the repository subpath `https://izynu.github.io/arguo/`.
3. Run it once via the Actions tab ("Deploy site to GitHub Pages", Run workflow) to confirm the build and deploy succeed.
4. For a custom domain at the zone root, remove `NEXT_PUBLIC_BASE_PATH` from the workflow env block.

Build details: the workflow installs dependencies with bun (the repository has a `bun.lock` and no package-lock.json, so `npm ci` is not an option) and invokes `next build` directly instead of `bun run build`, because the package.json build script copies `.next/standalone` files that only exist in standalone output. `scripts/generate_docs.py` is stdlib-only, so the job regenerates the docs data without installing Python dependencies.

### Option B: any static host

1. Build locally or in your pipeline:

   ```bash
   bun install
   NEXT_OUTPUT=export NEXT_PUBLIC_BASE_PATH=/your-subpath NEXT_TELEMETRY_DISABLED=1 bunx --bun next build
   ```

   Omit `NEXT_PUBLIC_BASE_PATH` when hosting at a domain root.
2. Upload the generated `out/` directory to the host of your choice.

## 3. Custom domain

1. Add the DNS records per your host's instructions. For GitHub Pages: a `CNAME` record pointing `www.your-domain` (or the apex via A/ALIAS records) at your Pages URL, per the GitHub Pages docs.
2. When using GitHub Pages with a custom domain, add a `CNAME` file containing the domain to `public/` so it is included in the exported output, and enable HTTPS enforcement in the repository Pages settings after the first deploy.
3. Keep `NEXT_PUBLIC_BASE_PATH` unset for zone-root domains; the site fetches its data through `withBase()` in `src/lib/site-config.ts`, which returns bare paths when the env var is absent.

## 4. Site identity configuration

`src/lib/site-config.ts` holds the site name, tagline, description, `repoUrl`, and `siteUrl`. Both URL fields are `null` in the repository on purpose so the site never links to an address that does not exist yet. Set them before launch:

```ts
repoUrl: "https://github.com/YOUR-HANDLE/arguo",
siteUrl: "https://your-domain-or-pages-url",
```

## 5. Favicon status

Included. The site uses `src/app/icon.svg` under the App Router icon convention, so the favicon ships with the site without extra configuration. Confirm the file exists in your checkout before launch.

## 6. Privacy and terms status

Included. The privacy policy and terms render at the hash routes `#/privacy` and `#/terms` (implemented in `src/components/site/legal.tsx`). Confirm both render before launch.

## 7. Badge check

The site contains no "Made with AI" badge or similar tag, and none should be added. Verify before launch:

```bash
grep -ri "made with ai" src/ || echo clean
```

## 8. Root robots.txt

`robots.txt` at the repository root is a template: it allows all crawlers and contains a commented `Sitemap:` line with a `YOUR-DOMAIN` placeholder. When you deploy the site, serve a real file at the site root with your actual domain, and only uncomment the Sitemap line once a sitemap exists.

## 9. Final checks

Run the full gate before launch:

```bash
make lint test validate
python3 tools/style_check.py
```

`make lint test validate` runs ruff, the 167-test offline suite, and the three validators. The style check scans docs, skill, site components, and the root README, CHANGELOG, and CONTRIBUTING files for em dashes, en dashes, and emoji. Launch only when every step passes.
