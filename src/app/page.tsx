"use client";

import { useHashRoute, navigate } from "@/lib/hooks";
import { SiteHeader } from "@/components/site/header";
import { SiteFooter } from "@/components/site/footer";
import { HomeView } from "@/components/site/home";
import { DocsView } from "@/components/site/docs-viewer";
import { ResourcesView } from "@/components/site/resource-explorer";
import { StatsView } from "@/components/site/stats-view";
import { MethodologyView } from "@/components/site/methodology";
import { EvalsView } from "@/components/site/evals";
import { PrivacyView, TermsView } from "@/components/site/legal";
import { CommandPalette } from "@/components/site/command-palette";
import { Button } from "@/components/ui/button";
import { useEffect } from "react";

function NotFoundView() {
  return (
    <div className="mx-auto max-w-3xl px-4 sm:px-6 py-24 text-center flex-1 w-full">
      <p className="font-mono text-sm text-muted-foreground">404</p>
      <h1 className="font-serif text-3xl font-bold mt-2">Page not found</h1>
      <p className="mt-3 text-sm text-muted-foreground">
        The address does not match any view of this site.
      </p>
      <Button variant="outline" className="mt-6" onClick={() => navigate("/")}>
        Back to the home page
      </Button>
    </div>
  );
}

export default function Page() {
  const route = useHashRoute();

  useEffect(() => {
    if (route.view !== "docs") {
      window.scrollTo({ top: 0 });
    }
  }, [route.view]);

  let content: React.ReactNode;
  switch (route.view) {
    case "home":
      content = <HomeView />;
      break;
    case "docs":
      content = <DocsView slug={route.slug} />;
      break;
    case "resources":
      content = <ResourcesView />;
      break;
    case "stats":
      content = <StatsView />;
      break;
    case "methodology":
      content = <MethodologyView />;
      break;
    case "evals":
      content = <EvalsView />;
      break;
    case "privacy":
      content = <PrivacyView />;
      break;
    case "terms":
      content = <TermsView />;
      break;
    default:
      content = <NotFoundView />;
  }

  return (
    <>
      <SiteHeader route={route} />
      <CommandPalette />
      <main id="main-content" className="flex-1 w-full">
        {content}
      </main>
      <SiteFooter />
    </>
  );
}
