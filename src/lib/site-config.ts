export type SiteConfig = {
  name: string;
  tagline: string;
  description: string;
  /**
   * Set these before publishing. They stay null in the repository so the site
   * never links to an address that does not exist yet.
   */
  repoUrl: string | null;
  siteUrl: string | null;
};

export const siteConfig: SiteConfig = {
  name: "Arguo",
  tagline: "Research deeply. Verify independently. Show your evidence.",
  description:
    "An open-source research intelligence toolkit: an agent skill, a Python research agent with a traceable evidence ledger and citation auditing, and a curated catalog of research resources.",
  repoUrl: "https://github.com/izynu/arguo",
  siteUrl: null,
};

/**
 * Prefix for client-side fetches. Empty in development. Set
 * NEXT_PUBLIC_BASE_PATH when deploying under a subpath such as
 * /arguo/ on GitHub Pages.
 */
export const basePath = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

export function withBase(path: string): string {
  return `${basePath}${path}`;
}
