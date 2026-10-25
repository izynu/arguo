"use client";

import { useEffect, useMemo, useState } from "react";
import { useJson, navigate, groupLabels, groupOrder } from "@/lib/hooks";
import { withBase } from "@/lib/site-config";
import { Markdown, stripFrontmatter } from "@/components/site/markdown";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Search, ChevronLeft, ChevronRight, FileQuestion } from "lucide-react";

export type DocPage = {
  group: string;
  slug: string;
  title: string;
  description: string;
  order: number;
  path: string;
};

export function DocsView({ slug }: { slug?: string }) {
  const { data: index, loading, error } = useJson<DocPage[]>("/data/docs-index.json");
  const [query, setQuery] = useState("");

  const byGroup = useMemo(() => {
    const map = new Map<string, DocPage[]>();
    if (!index) return map;
    const filtered = query
      ? index.filter(
          (p) =>
            p.title.toLowerCase().includes(query.toLowerCase()) ||
            p.description.toLowerCase().includes(query.toLowerCase())
        )
      : index;
    for (const page of filtered) {
      const list = map.get(page.group) ?? [];
      list.push(page);
      map.set(page.group, list);
    }
    for (const list of map.values()) list.sort((a, b) => a.order - b.order);
    return map;
  }, [index, query]);

  const current = index?.find((p) => p.slug === slug);
  const flat = useMemo(() => (index ? [...index].sort((a, b) => (groupOrder.indexOf(a.group) - groupOrder.indexOf(b.group)) || a.order - b.order) : []), [index]);
  const currentIdx = flat.findIndex((p) => p.slug === slug);
  const prev = currentIdx > 0 ? flat[currentIdx - 1] : null;
  const next = currentIdx >= 0 && currentIdx < flat.length - 1 ? flat[currentIdx + 1] : null;

  if (error) {
    return <Shell><p className="text-sm text-red-700 dark:text-red-400">Failed to load the documentation index: {error}</p></Shell>;
  }

  if (slug && !loading && !current) {
    return (
      <Shell>
        <div className="py-16 text-center">
          <FileQuestion className="h-10 w-10 mx-auto text-muted-foreground" aria-hidden="true" />
          <h1 className="font-serif text-2xl font-bold mt-4">Page not found</h1>
          <p className="text-sm text-muted-foreground mt-2">
            No documentation page has the slug &ldquo;{slug}&rdquo;.
          </p>
          <Button variant="outline" className="mt-5" onClick={() => navigate("/docs")}>
            Browse all pages
          </Button>
        </div>
      </Shell>
    );
  }

  return (
    <Shell>
      <div className="grid lg:grid-cols-[260px_1fr] gap-8">
        <aside aria-label="Documentation navigation" className="lg:sticky lg:top-20 lg:self-start lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto lg:pr-2">
          <div className="relative mb-4">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Filter pages"
              aria-label="Filter documentation pages"
              className="pl-8 h-9"
            />
          </div>
          {loading ? (
            <div className="space-y-2">
              {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-5 w-40" />)}
            </div>
          ) : (
            <nav className="space-y-5">
              {groupOrder.filter((g) => byGroup.has(g)).map((g) => (
                <div key={g}>
                  <h2 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5">
                    {groupLabels[g]}
                  </h2>
                  <ul className="space-y-0.5">
                    {(byGroup.get(g) ?? []).map((p) => (
                      <li key={p.slug}>
                        <a
                          href={`#/docs/${p.slug}`}
                          aria-current={p.slug === slug ? "page" : undefined}
                          className={`block rounded px-2.5 py-1.5 text-[13px] leading-5 transition-colors ${
                            p.slug === slug
                              ? "bg-green-50 dark:bg-green-950/40 text-green-900 dark:text-green-300 font-medium"
                              : "text-muted-foreground hover:text-foreground hover:bg-stone-100 dark:hover:bg-stone-800"
                          }`}
                        >
                          {p.title}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </nav>
          )}
        </aside>

        <article className="min-w-0 max-w-3xl">
          {current ? (
            <DocContent page={current} prev={prev} next={next} />
          ) : (
            <div>
              <h1 className="font-serif text-3xl font-bold tracking-tight">Documentation</h1>
              <p className="mt-2 text-[15px] text-muted-foreground">
                {index ? `${index.length} pages covering the skill, the Python agent, the catalog, and the project.` : "Loading."}
              </p>
              {loading ? (
                <div className="mt-8 space-y-3">
                  {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-6 w-full max-w-md" />)}
                </div>
              ) : (
                <div className="mt-8 space-y-8">
                  {groupOrder.filter((g) => byGroup.has(g)).map((g) => (
                    <section key={g}>
                      <h2 className="font-serif text-lg font-bold pb-1.5 border-b border-stone-200 dark:border-stone-800">
                        {groupLabels[g]}
                      </h2>
                      <ul className="mt-3 grid sm:grid-cols-2 gap-2">
                        {(byGroup.get(g) ?? []).map((p) => (
                          <li key={p.slug}>
                            <a
                              href={`#/docs/${p.slug}`}
                              className="block rounded-md border border-stone-200 dark:border-stone-800 p-3 hover:border-green-800 dark:hover:border-green-600 transition-colors"
                            >
                              <p className="text-sm font-medium">{p.title}</p>
                              <p className="text-xs text-muted-foreground mt-1 leading-5">{p.description}</p>
                            </a>
                          </li>
                        ))}
                      </ul>
                    </section>
                  ))}
                </div>
              )}
            </div>
          )}
        </article>
      </div>
    </Shell>
  );
}

function DocContent({ page, prev, next }: { page: DocPage; prev: DocPage | null; next: DocPage | null }) {
  const [result, setResult] = useState<{ path: string; markdown: string } | null>(null);
  const [failed, setFailed] = useState<{ path: string; message: string } | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(withBase(`/docs/${page.path.replace(/^docs\//, "")}`))
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.text();
      })
      .then((text) => {
        if (!cancelled) {
          setFailed(null);
          setResult({ path: page.path, markdown: stripFrontmatter(text) });
        }
      })
      .catch((err: Error) => {
        if (!cancelled) setFailed({ path: page.path, message: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, [page.path]);

  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [page.slug]);

  if (failed && failed.path === page.path) {
    return <p className="text-sm text-red-700 dark:text-red-400">Could not load this page&rsquo;s content ({failed.message}). The site data may need to be regenerated: run scripts/generate_docs.py and republish.</p>;
  }

  const markdown = result && result.path === page.path ? result.markdown : null;

  return (
    <div>
      <p className="text-xs uppercase tracking-wider text-muted-foreground">{groupLabels[page.group]}</p>
      <h1 className="font-serif text-3xl font-bold tracking-tight mt-1 mb-2">{page.title}</h1>
      {markdown ? (
        <Markdown>{markdown}</Markdown>
      ) : (
        <div className="mt-4 space-y-3">
          <Skeleton className="h-8 w-2/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      )}
      <nav aria-label="Page navigation" className="mt-12 pt-6 border-t border-stone-200 dark:border-stone-800 flex justify-between gap-4">
        {prev ? (
          <a href={`#/docs/${prev.slug}`} className="group text-sm max-w-[48%]">
            <span className="flex items-center gap-1 text-muted-foreground text-xs"><ChevronLeft className="h-3.5 w-3.5" aria-hidden="true" /> Previous</span>
            <span className="text-green-800 dark:text-green-400 group-hover:underline underline-offset-2">{prev.title}</span>
          </a>
        ) : <span />}
        {next ? (
          <a href={`#/docs/${next.slug}`} className="group text-sm text-right max-w-[48%]">
            <span className="flex items-center justify-end gap-1 text-muted-foreground text-xs">Next <ChevronRight className="h-3.5 w-3.5" aria-hidden="true" /></span>
            <span className="text-green-800 dark:text-green-400 group-hover:underline underline-offset-2">{next.title}</span>
          </a>
        ) : <span />}
      </nav>
    </div>
  );
}

function Shell({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10 flex-1 w-full">
      {children}
    </div>
  );
}
