"use client";

import { useTheme } from "next-themes";
import { Menu, Moon, Sun, ExternalLink, BookOpen, Database, ScrollText, FlaskConical, BarChart3, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetTitle,
} from "@/components/ui/sheet";
import { useState, useSyncExternalStore } from "react";
import { siteConfig } from "@/lib/site-config";
import type { Route } from "@/lib/hooks";

/** False during SSR and the first client render, true after hydration. */
function useMounted(): boolean {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  );
}

function LogoMark({ className = "h-7 w-7" }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      <rect x="7" y="4" width="50" height="56" rx="6" className="fill-stone-100 stroke-stone-800 dark:fill-stone-800 dark:stroke-stone-200" strokeWidth="4" />
      <line x1="16" y1="18" x2="48" y2="18" className="stroke-stone-500 dark:stroke-stone-400" strokeWidth="4" strokeLinecap="round" />
      <line x1="16" y1="27" x2="48" y2="27" className="stroke-stone-500 dark:stroke-stone-400" strokeWidth="4" strokeLinecap="round" />
      <line x1="16" y1="36" x2="38" y2="36" className="stroke-stone-500 dark:stroke-stone-400" strokeWidth="4" strokeLinecap="round" />
      <path d="M20 46 l9 9 l17 -19" fill="none" className="stroke-green-700 dark:stroke-green-400" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

const navItems = [
  { href: "#/docs", label: "Docs", icon: BookOpen },
  { href: "#/resources", label: "Resources", icon: Database },
  { href: "#/stats", label: "Stats", icon: BarChart3 },
  { href: "#/methodology", label: "Methodology", icon: ScrollText },
  { href: "#/evals", label: "Evals", icon: FlaskConical },
];

export function SiteHeader({ route }: { route: Route }) {
  const { theme, setTheme } = useTheme();
  const mounted = useMounted();
  const [open, setOpen] = useState(false);

  const isActive = (href: string) => {
    const head = href.replace("#/", "");
    if (head === "docs") return route.view === "docs";
    return route.view === head;
  };

  return (
    <header className="sticky top-0 z-40 border-b border-stone-200 dark:border-stone-800 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <a
        href="#main-content"
        onClick={(e) => {
          // Move focus without changing the hash, so the view router is not
          // disturbed (a hash like #main-content is not a route).
          e.preventDefault();
          const main = document.getElementById("main-content");
          if (main) {
            main.setAttribute("tabindex", "-1");
            main.focus();
          }
        }}
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-2 focus:z-50 focus:bg-background focus:px-3 focus:py-2 focus:border focus:border-stone-300 focus:rounded-md"
      >
        Skip to content
      </a>
      <div className="mx-auto max-w-6xl px-4 sm:px-6 h-14 flex items-center gap-4">
        <a href="#/" className="flex items-center gap-2.5 shrink-0" aria-label={`${siteConfig.name} home`}>
          <LogoMark />
          <span className="font-serif font-bold text-lg tracking-tight">{siteConfig.name}</span>
        </a>

        <nav aria-label="Main" className="hidden md:flex items-center gap-1 ml-4">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              aria-current={isActive(item.href) ? "page" : undefined}
              className={`px-3 py-1.5 rounded-md text-sm transition-colors ${
                isActive(item.href)
                  ? "bg-stone-100 dark:bg-stone-800 text-foreground font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-stone-100 dark:hover:bg-stone-800"
              }`}
            >
              {item.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true, bubbles: true }))}
            className="hidden sm:inline-flex items-center gap-2 rounded-md border border-stone-200 dark:border-stone-800 px-3 h-8 text-sm text-muted-foreground hover:text-foreground hover:border-stone-300 dark:hover:border-stone-700 transition-colors"
            aria-label="Open search palette"
          >
            <Search className="h-3.5 w-3.5" aria-hidden="true" />
            Search
            <kbd className="font-mono text-[10px] text-muted-foreground border border-stone-200 dark:border-stone-700 rounded px-1">Cmd K</kbd>
          </button>
          {siteConfig.repoUrl ? (
            <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
              <a href={siteConfig.repoUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-4 w-4 mr-1.5" aria-hidden="true" />
                Repository
              </a>
            </Button>
          ) : null}
          <Button
            variant="ghost"
            size="icon"
            aria-label={mounted && theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {mounted && theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden" aria-label="Open menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              <SheetTitle className="sr-only">Navigation menu</SheetTitle>
              <nav aria-label="Mobile" className="mt-6 flex flex-col gap-1">
                {navItems.map((item) => (
                  <a
                    key={item.href}
                    href={item.href}
                    onClick={() => setOpen(false)}
                    className={`flex items-center gap-2.5 px-3 py-2.5 rounded-md text-sm ${
                      isActive(item.href)
                        ? "bg-stone-100 dark:bg-stone-800 font-medium"
                        : "text-muted-foreground"
                    }`}
                  >
                    <item.icon className="h-4 w-4" aria-hidden="true" />
                    {item.label}
                  </a>
                ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}

export { LogoMark };
