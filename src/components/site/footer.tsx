"use client";

import { siteConfig } from "@/lib/site-config";

const featuredGroups = [
  { label: "Getting Started", href: "#/docs/gs-introduction" },
  { label: "Core Concepts", href: "#/docs/cc-overview" },
  { label: "Resource Library", href: "#/docs/rl-browse" },
  { label: "Project", href: "#/docs/pj-about" },
];

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-stone-200 dark:border-stone-800 bg-stone-100/60 dark:bg-stone-900/60 pb-[env(safe-area-inset-bottom)]">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div>
            <h2 className="font-serif font-semibold text-sm mb-3">Documentation</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              {featuredGroups.map((g) => (
                <li key={g.href}>
                  <a href={g.href} className="hover:text-foreground transition-colors">
                    {g.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="font-serif font-semibold text-sm mb-3">Toolkit</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#/resources" className="hover:text-foreground transition-colors">Resource catalog</a></li>
              <li><a href="#/stats" className="hover:text-foreground transition-colors">Catalog statistics</a></li>
              <li><a href="#/methodology" className="hover:text-foreground transition-colors">Methodology</a></li>
              <li><a href="#/evals" className="hover:text-foreground transition-colors">Evaluations</a></li>
              <li><a href="#/docs/gs-cli-tutorial" className="hover:text-foreground transition-colors">CLI tutorial</a></li>
            </ul>
          </div>
          <div>
            <h2 className="font-serif font-semibold text-sm mb-3">Policies</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="#/privacy" className="hover:text-foreground transition-colors">Privacy policy</a></li>
              <li><a href="#/terms" className="hover:text-foreground transition-colors">Terms of use</a></li>
              <li><a href="#/docs/pj-license" className="hover:text-foreground transition-colors">License</a></li>
              <li><a href="#/docs/pj-security-policy" className="hover:text-foreground transition-colors">Security policy</a></li>
            </ul>
          </div>
          <div>
            <h2 className="font-serif font-semibold text-sm mb-3">Repository</h2>
            <div className="space-y-2 text-sm text-muted-foreground">
              <a
                href="/arguo-latest.zip"
                download
                className="hover:text-foreground transition-colors"
              >
                Download source (.zip)
              </a>
              {siteConfig.repoUrl ? (
                <a
                  href={siteConfig.repoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:text-foreground transition-colors"
                >
                  Source code
                </a>
              ) : (
                <p>
                  Repository URL is not configured yet.{" "}
                  <a href="#/docs/pj-publishing" className="underline hover:text-foreground">
                    Publishing guide
                  </a>
                </p>
              )}
              <p>Apache-2.0. Provided as is, without warranty.</p>
            </div>
          </div>
        </div>
        <div className="mt-8 pt-6 border-t border-stone-200 dark:border-stone-800 text-xs text-muted-foreground flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <p>
            {siteConfig.name} is an open-source project built by{" "}
            <a href="https://github.com/izynu" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-foreground transition-colors">Zynu</a>
            {" "}and{" "}
            <a href="https://github.com/xhraddha" target="_blank" rel="noopener noreferrer" className="underline underline-offset-2 hover:text-foreground transition-colors">Shraddha</a>
            . Research outputs are aids for human judgment, not authoritative answers.
          </p>
        </div>
      </div>
    </footer>
  );
}
