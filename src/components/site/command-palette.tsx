"use client";

import { useEffect, useMemo, useState } from "react";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator } from "@/components/ui/command";
import { useJson, useBookmarks } from "@/lib/hooks";
import { Badge } from "@/components/ui/badge";
import {
  Home, BookOpen, Database, ScrollText, FlaskConical, BarChart3, ShieldCheck, FileText, Star, CornerDownLeft,
} from "lucide-react";

type ResourceRecord = {
  id: string;
  name: string;
  canonical_url: string;
  category: string;
  description: string;
  publisher: string;
  tags: string[];
};

const views = [
  { href: "#/", label: "Home", icon: Home, hint: "Overview and pipeline" },
  { href: "#/resources", label: "Resource catalog", icon: Database, hint: "Search every record" },
  { href: "#/stats", label: "Catalog statistics", icon: BarChart3, hint: "Counts by category and region" },
  { href: "#/docs", label: "Documentation", icon: BookOpen, hint: "All guide pages" },
  { href: "#/methodology", label: "Methodology", icon: ScrollText, hint: "How records are verified" },
  { href: "#/evals", label: "Evaluations", icon: FlaskConical, hint: "Benchmark results" },
  { href: "#/privacy", label: "Privacy policy", icon: ShieldCheck, hint: "What is and is not collected" },
  { href: "#/terms", label: "Terms of use", icon: FileText, hint: "Conditions for using Arguo" },
];

function matches(r: ResourceRecord, tokens: string[]): boolean {
  return tokens.every((t) =>
    r.name.toLowerCase().includes(t) ||
    r.description.toLowerCase().includes(t) ||
    r.publisher.toLowerCase().includes(t) ||
    r.category.toLowerCase().includes(t) ||
    r.tags.some((tag) => tag.includes(t))
  );
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  // Global shortcut: Ctrl+K on Windows/Linux, Cmd+K on macOS.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <CommandDialog open={open} onOpenChange={setOpen} className="max-w-xl">
      {open ? <PaletteContent query={query} setQuery={setQuery} close={() => setOpen(false)} /> : null}
    </CommandDialog>
  );
}

function PaletteContent({ query, setQuery, close }: { query: string; setQuery: (v: string) => void; close: () => void }) {
  // The catalog is fetched only while the palette is open.
  const { data } = useJson<ResourceRecord[]>("/data/catalog.json");
  const { ids: bookmarkIds } = useBookmarks();

  const tokens = useMemo(
    () => query.toLowerCase().split(/\s+/).filter(Boolean),
    [query]
  );

  const resourceHits = useMemo(() => {
    if (!data || tokens.length === 0) return [];
    const bookmarksFirst = [...data].sort((a, b) => {
      const ab = bookmarkIds.includes(a.id) ? 0 : 1;
      const bb = bookmarkIds.includes(b.id) ? 0 : 1;
      return ab - bb;
    });
    return bookmarksFirst.filter((r) => matches(r, tokens)).slice(0, 8);
  }, [data, tokens, bookmarkIds]);

  const bookmarkedResources = useMemo(() => {
    if (!data || tokens.length > 0 || bookmarkIds.length === 0) return [];
    return data.filter((r) => bookmarkIds.includes(r.id)).slice(0, 5);
  }, [data, tokens, bookmarkIds]);

  return (
    <>
      <CommandInput
        value={query}
        onValueChange={setQuery}
        placeholder="Search resources or jump to a page"
        aria-label="Command palette search"
      />
      <CommandList className="max-h-[380px]">
        <CommandEmpty>
          {data ? "No matching records. Try fewer words." : "Loading catalog."}
        </CommandEmpty>

        {tokens.length === 0 ? (
          <CommandGroup heading="Pages">
            {views.map((v) => (
              <CommandItem
                key={v.href}
                value={`page ${v.label}`}
                onSelect={() => { window.location.hash = v.href.slice(1); close(); }}
              >
                <v.icon className="h-4 w-4" aria-hidden="true" />
                <span>{v.label}</span>
                <span className="ml-auto text-xs text-muted-foreground">{v.hint}</span>
              </CommandItem>
            ))}
          </CommandGroup>
        ) : null}

        {bookmarkedResources.length > 0 ? (
          <CommandGroup heading="Bookmarked">
            {bookmarkedResources.map((r) => (
              <CommandItem
                key={r.id}
                value={`bookmark ${r.name} ${r.id}`}
                onSelect={() => { window.location.hash = `/resources?id=${encodeURIComponent(r.id)}`; close(); }}
              >
                <Star className="h-4 w-4 fill-current" aria-hidden="true" />
                <span>{r.name}</span>
                <Badge variant="outline" className="ml-auto text-[11px]">{r.category}</Badge>
              </CommandItem>
            ))}
          </CommandGroup>
        ) : null}

        {resourceHits.length > 0 ? (
          <>
            {tokens.length === 0 ? <CommandSeparator /> : null}
            <CommandGroup heading="Resources">
              {resourceHits.map((r) => (
                <CommandItem
                  key={r.id}
                  value={`resource ${r.name} ${r.publisher} ${r.tags.join(" ")}`}
                  onSelect={() => { window.location.hash = `/resources?id=${encodeURIComponent(r.id)}`; close(); }}
                >
                  <Database className="h-4 w-4 shrink-0" aria-hidden="true" />
                  <span className="truncate">{r.name}</span>
                  <span className="ml-auto truncate max-w-[140px] text-xs text-muted-foreground">{r.publisher}</span>
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        ) : null}
      </CommandList>
      <div className="border-t border-stone-200 dark:border-stone-800 px-3 py-2 text-xs text-muted-foreground flex items-center gap-4">
        <span className="inline-flex items-center gap-1"><CornerDownLeft className="h-3 w-3" aria-hidden="true" /> open</span>
        <span>esc close</span>
        <span className="ml-auto">{data ? `${data.length.toLocaleString("en-US")} records indexed` : "loading"}</span>
      </div>
    </>
  );
}
