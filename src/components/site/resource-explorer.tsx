"use client";

import { useMemo, useState } from "react";
import { useJson, navigate, useHashQuery, replaceHashQuery, useBookmarks } from "@/lib/hooks";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Search, X, ExternalLink, ChevronLeft, ChevronRight, Database, Star, Download, Link2, Braces, Copy,
} from "lucide-react";

export type ResourceRecord = {
  id: string;
  name: string;
  canonical_url: string;
  category: string;
  subcategory?: string | null;
  description: string;
  best_for: string[];
  resource_type: string;
  publisher: string;
  region: string;
  language: string;
  resource_access: string;
  api_available: boolean;
  documentation_url?: string | null;
  official_source: boolean;
  license: string;
  date_added: string;
  last_checked: string | null;
  verification_status: string;
  provenance: { source: string; note?: string | null };
  tags: string[];
};

type Stats = {
  total_records: number;
  category_count: number;
  categories: Record<string, number>;
};

const PAGE_SIZE = 24;

const accessLabels: Record<string, string> = {
  open: "Open",
  "free-registration": "Free registration",
  "partial-open": "Partial open",
  paid: "Paid",
  mixed: "Mixed",
};

const statusLabels: Record<string, string> = {
  documented: "Documented",
  verified: "Verified",
  "community-submitted": "Community submitted",
  deprecated: "Deprecated",
};

function statusClasses(status: string): string {
  switch (status) {
    case "verified":
      return "bg-green-100 text-green-900 border-green-300 dark:bg-green-950 dark:text-green-300 dark:border-green-800";
    case "community-submitted":
      return "bg-amber-100 text-amber-900 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800";
    case "deprecated":
      return "bg-red-100 text-red-900 border-red-300 dark:bg-red-950 dark:text-red-300 dark:border-red-800";
    default:
      return "bg-stone-100 text-stone-700 border-stone-300 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-700";
  }
}

/* --------------------------------- URL filter state --------------------------------- */

type FilterState = {
  q: string;
  category: string;
  access: string;
  region: string;
  apiOnly: boolean;
  bookmarkedOnly: boolean;
  sort: string;
  page: number;
  detailId: string | null;
};

function readFilters(params: URLSearchParams): FilterState {
  const pageRaw = parseInt(params.get("page") ?? "1", 10);
  return {
    q: params.get("q") ?? "",
    category: params.get("category") ?? "all",
    access: params.get("access") ?? "all",
    region: params.get("region") ?? "all",
    apiOnly: params.get("api") === "1",
    bookmarkedOnly: params.get("bm") === "1",
    sort: params.get("sort") ?? "name",
    page: Number.isFinite(pageRaw) && pageRaw > 0 ? pageRaw : 1,
    detailId: params.get("id"),
  };
}

function writeFilters(state: FilterState) {
  const p = new URLSearchParams();
  if (state.q) p.set("q", state.q);
  if (state.category !== "all") p.set("category", state.category);
  if (state.access !== "all") p.set("access", state.access);
  if (state.region !== "all") p.set("region", state.region);
  if (state.apiOnly) p.set("api", "1");
  if (state.bookmarkedOnly) p.set("bm", "1");
  if (state.sort !== "name") p.set("sort", state.sort);
  if (state.page > 1) p.set("page", String(state.page));
  if (state.detailId) p.set("id", state.detailId);
  replaceHashQuery(p);
}

/* --------------------------------- Search helpers --------------------------------- */

function tokenize(q: string): string[] {
  return q.toLowerCase().split(/\s+/).filter(Boolean);
}

function matchesTokens(r: ResourceRecord, tokens: string[]): boolean {
  return tokens.every((t) =>
    r.name.toLowerCase().includes(t) ||
    r.description.toLowerCase().includes(t) ||
    r.publisher.toLowerCase().includes(t) ||
    r.category.toLowerCase().includes(t) ||
    r.region.toLowerCase().includes(t) ||
    r.tags.some((tag) => tag.includes(t))
  );
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function Highlight({ text, tokens }: { text: string; tokens: string[] }) {
  if (tokens.length === 0) return <>{text}</>;
  const pattern = tokens.map(escapeRegExp).join("|");
  let parts: string[];
  try {
    parts = text.split(new RegExp(`(${pattern})`, "ig"));
  } catch {
    return <>{text}</>;
  }
  const lower = tokens.map((t) => t.toLowerCase());
  return (
    <>
      {parts.map((part, i) =>
        lower.includes(part.toLowerCase()) ? (
          <mark key={i} className="bg-green-100 text-green-900 dark:bg-green-950 dark:text-green-300">
            {part}
          </mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

/* --------------------------------- Export helpers --------------------------------- */

const EXPORT_COLUMNS: { key: keyof ResourceRecord; label: string }[] = [
  { key: "id", label: "id" },
  { key: "name", label: "name" },
  { key: "category", label: "category" },
  { key: "resource_type", label: "type" },
  { key: "publisher", label: "publisher" },
  { key: "region", label: "region" },
  { key: "language", label: "language" },
  { key: "resource_access", label: "access" },
  { key: "api_available", label: "api_available" },
  { key: "official_source", label: "official_source" },
  { key: "license", label: "license" },
  { key: "verification_status", label: "verification_status" },
  { key: "date_added", label: "date_added" },
  { key: "last_checked", label: "last_checked" },
  { key: "canonical_url", label: "canonical_url" },
  { key: "description", label: "description" },
  { key: "best_for", label: "best_for" },
  { key: "tags", label: "tags" },
];

function csvCell(value: unknown): string {
  const s = Array.isArray(value) ? value.join("; ") : String(value ?? "");
  return `"${s.replace(/"/g, '""')}"`;
}

function download(records: ResourceRecord[], format: "csv" | "json") {
  let blob: Blob;
  let filename: string;
  if (format === "json") {
    blob = new Blob([JSON.stringify(records, null, 2)], { type: "application/json" });
    filename = `arguo-resources-${records.length}.json`;
  } else {
    const header = EXPORT_COLUMNS.map((c) => csvCell(c.label)).join(",");
    const rows = records.map((r) =>
      EXPORT_COLUMNS.map((c) => csvCell(r[c.key])).join(",")
    );
    blob = new Blob([`${header}\n${rows.join("\n")}`], { type: "text/csv;charset=utf-8" });
    filename = `arguo-resources-${records.length}.csv`;
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

/* --------------------------------- Related records --------------------------------- */

function relatedRecords(all: ResourceRecord[], record: ResourceRecord, limit = 4): ResourceRecord[] {
  const scored = all
    .filter((r) => r.id !== record.id)
    .map((r) => {
      const sharedTags = r.tags.filter((t) => record.tags.includes(t)).length;
      const score = (r.category === record.category ? 2 : 0) + sharedTags + (r.publisher === record.publisher ? 1 : 0);
      return { r, score };
    })
    .filter((x) => x.score > 1)
    .sort((a, b) => b.score - a.score || a.r.name.localeCompare(b.r.name));
  return scored.slice(0, limit).map((x) => x.r);
}

/* --------------------------------- Main view --------------------------------- */

export function ResourcesView() {
  const { data, loading, error } = useJson<ResourceRecord[]>("/data/catalog.json");
  const { data: stats } = useJson<Stats>("/data/stats.json");
  const params = useHashQuery();
  const { ids: bookmarkIds, has: hasBookmark, toggle: toggleBookmark } = useBookmarks();
  const { toast } = useToast();

  const f = readFilters(params);
  const tokens = useMemo(() => tokenize(f.q), [f.q]);

  const setFilter = (patch: Partial<FilterState>) => {
    const next: FilterState = { ...f, ...patch };
    const structuralKeys: (keyof FilterState)[] = ["q", "category", "access", "region", "apiOnly", "bookmarkedOnly", "sort"];
    if (structuralKeys.some((k) => k in patch)) next.page = 1;
    writeFilters(next);
  };

  const regions = useMemo(() => {
    if (!data) return [];
    return [...new Set(data.map((r) => r.region))].sort();
  }, [data]);

  const bookmarkSet = useMemo(() => new Set(bookmarkIds), [bookmarkIds]);

  const filtered = useMemo(() => {
    if (!data) return [];
    let out = data.filter((r) => {
      if (f.category !== "all" && r.category !== f.category) return false;
      if (f.access !== "all" && r.resource_access !== f.access) return false;
      if (f.region !== "all" && r.region !== f.region) return false;
      if (f.apiOnly && !r.api_available) return false;
      if (f.bookmarkedOnly && !bookmarkSet.has(r.id)) return false;
      if (tokens.length > 0 && !matchesTokens(r, tokens)) return false;
      return true;
    });
    out = [...out].sort((a, b) => {
      switch (f.sort) {
        case "name-desc":
          return b.name.localeCompare(a.name);
        case "category":
          return a.category.localeCompare(b.category) || a.name.localeCompare(b.name);
        case "region":
          return a.region.localeCompare(b.region) || a.name.localeCompare(b.name);
        case "date-added":
          return b.date_added.localeCompare(a.date_added) || a.name.localeCompare(b.name);
        default:
          return a.name.localeCompare(b.name);
      }
    });
    return out;
  }, [data, f.category, f.access, f.region, f.apiOnly, f.bookmarkedOnly, f.sort, tokens, bookmarkSet]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(f.page, pageCount);
  const pageItems = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const hasFilters =
    f.q !== "" || f.category !== "all" || f.access !== "all" || f.region !== "all" || f.apiOnly || f.bookmarkedOnly;

  const clearFilters = () => {
    setFilter({
      q: "", category: "all", access: "all", region: "all",
      apiOnly: false, bookmarkedOnly: false, sort: "name",
    });
  };

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({ title: "Link copied", description: "The current filters are encoded in the address." });
    } catch {
      toast({ title: "Copy failed", description: "The browser blocked clipboard access." });
    }
  };

  const exportView = (format: "csv" | "json") => {
    download(filtered, format);
    toast({
      title: `Exported ${filtered.length.toLocaleString("en-US")} records`,
      description: `Saved as ${format.toUpperCase()} in your downloads.`,
    });
  };

  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10 flex-1">
        <p className="text-sm text-red-700 dark:text-red-400">
          Failed to load the catalog: {error}. Regenerate it with scripts/build_resource_catalog.py.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10 flex-1 w-full">
      <div className="max-w-3xl">
        <h1 className="font-serif text-3xl font-bold tracking-tight">Research resource catalog</h1>
        <p className="mt-2 text-[15px] leading-7 text-muted-foreground">
          {stats
            ? `${stats.total_records.toLocaleString("en-US")} schema-validated records across ${stats.category_count} research categories: government statistics, scholarly indexes, archives, legal databases, APIs, and more. Records are factual metadata with explicit unknowns.`
            : "Loading catalog metadata."}
        </p>
        <p className="mt-2 text-xs text-muted-foreground">
          Status definitions:{" "}
          <a href="#/docs/rl-quality-licensing" className="underline hover:text-foreground">
            how verification statuses work
          </a>
        </p>
      </div>

      <div className="mt-8 grid gap-3 md:grid-cols-[1fr_auto]">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Input
            value={f.q}
            onChange={(e) => setFilter({ q: e.target.value })}
            placeholder="Search by name, description, publisher, region, or tag"
            aria-label="Search resources"
            className="pl-8 h-10 bg-background"
          />
        </div>
        <div className="flex gap-3">
          <Select value={f.sort} onValueChange={(v) => setFilter({ sort: v })}>
            <SelectTrigger className="w-[170px] h-10" aria-label="Sort order">
              <SelectValue placeholder="Sort" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="name">Name, A to Z</SelectItem>
              <SelectItem value="name-desc">Name, Z to A</SelectItem>
              <SelectItem value="category">Category</SelectItem>
              <SelectItem value="region">Region</SelectItem>
              <SelectItem value="date-added">Newest added</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <Select value={f.category} onValueChange={(v) => setFilter({ category: v })}>
          <SelectTrigger className="w-[220px] h-9" aria-label="Filter by category">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent className="max-h-72">
            <SelectItem value="all">All categories</SelectItem>
            {stats
              ? Object.keys(stats.categories).sort().map((c) => (
                  <SelectItem key={c} value={c}>
                    {c} ({stats.categories[c]})
                  </SelectItem>
                ))
              : null}
          </SelectContent>
        </Select>
        <Select value={f.access} onValueChange={(v) => setFilter({ access: v })}>
          <SelectTrigger className="w-[170px] h-9" aria-label="Filter by access model">
            <SelectValue placeholder="Access" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Any access</SelectItem>
            {Object.entries(accessLabels).map(([k, v]) => (
              <SelectItem key={k} value={k}>{v}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={f.region} onValueChange={(v) => setFilter({ region: v })}>
          <SelectTrigger className="w-[190px] h-9" aria-label="Filter by region">
            <SelectValue placeholder="Region" />
          </SelectTrigger>
          <SelectContent className="max-h-72">
            <SelectItem value="all">Any region</SelectItem>
            {regions.map((r) => (
              <SelectItem key={r} value={r}>{r}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <label className="flex items-center gap-2 text-sm text-muted-foreground h-9 cursor-pointer">
          <Checkbox
            checked={f.apiOnly}
            onCheckedChange={(v) => setFilter({ apiOnly: v === true })}
            aria-label="Only resources with an API"
          />
          Has API
        </label>
        <label className="flex items-center gap-2 text-sm text-muted-foreground h-9 cursor-pointer">
          <Checkbox
            checked={f.bookmarkedOnly}
            onCheckedChange={(v) => setFilter({ bookmarkedOnly: v === true })}
            aria-label="Show bookmarked resources only"
          />
          Bookmarked{bookmarkIds.length > 0 ? ` (${bookmarkIds.length})` : ""}
        </label>
        {hasFilters ? (
          <Button variant="ghost" size="sm" onClick={clearFilters} className="h-9">
            <X className="h-3.5 w-3.5 mr-1" aria-hidden="true" />
            Clear filters
          </Button>
        ) : null}
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-2">
        <p className="text-sm text-muted-foreground mr-auto" role="status">
          {loading
            ? "Loading records."
            : `${filtered.length.toLocaleString("en-US")} of ${(stats?.total_records ?? 0).toLocaleString("en-US")} records`}
        </p>
        {!loading && filtered.length > 0 ? (
          <>
            <Button variant="outline" size="sm" className="h-8" onClick={() => exportView("csv")}>
              <Download className="h-3.5 w-3.5 mr-1.5" aria-hidden="true" />
              CSV
            </Button>
            <Button variant="outline" size="sm" className="h-8" onClick={() => exportView("json")}>
              <Braces className="h-3.5 w-3.5 mr-1.5" aria-hidden="true" />
              JSON
            </Button>
          </>
        ) : null}
        <Button variant="outline" size="sm" className="h-8" onClick={copyLink}>
          <Link2 className="h-3.5 w-3.5 mr-1.5" aria-hidden="true" />
          Copy link
        </Button>
      </div>

      {loading ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {Array.from({ length: 8 }).map((_, i) => <Skeleton key={i} className="h-36 w-full" />)}
        </div>
      ) : filtered.length === 0 ? (
        <div className="mt-6 rounded-md border border-dashed border-stone-300 dark:border-stone-700 py-16 text-center">
          <Database className="h-8 w-8 mx-auto text-muted-foreground" aria-hidden="true" />
          <p className="mt-3 text-sm font-medium">
            {f.bookmarkedOnly && bookmarkIds.length === 0
              ? "No bookmarks yet. Use the star button on any record to save it here."
              : "No records match these filters."}
          </p>
          <Button variant="outline" size="sm" className="mt-4" onClick={clearFilters}>
            Clear filters
          </Button>
        </div>
      ) : (
        <>
          <ul className="mt-4 grid gap-3 sm:grid-cols-2">
            {pageItems.map((r) => (
              <li
                key={r.id}
                className="rounded-md border border-stone-200 dark:border-stone-800 p-4 flex flex-col hover:border-stone-300 dark:hover:border-stone-700 transition-colors"
              >
                <div className="flex items-start justify-between gap-3">
                  <button
                    onClick={() => setFilter({ detailId: r.id })}
                    className="text-left font-medium text-[15px] leading-5 hover:text-green-800 dark:hover:text-green-400 transition-colors"
                    aria-label={`Show details for ${r.name}`}
                  >
                    <Highlight text={r.name} tokens={tokens} />
                  </button>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <button
                      onClick={() => toggleBookmark(r.id)}
                      aria-pressed={hasBookmark(r.id)}
                      aria-label={hasBookmark(r.id) ? `Remove ${r.name} from bookmarks` : `Bookmark ${r.name}`}
                      className="p-1 rounded-sm text-stone-400 hover:text-green-800 dark:hover:text-green-400 transition-colors"
                    >
                      <Star className={`h-4 w-4 ${hasBookmark(r.id) ? "fill-green-700 text-green-700 dark:fill-green-400 dark:text-green-400" : ""}`} aria-hidden="true" />
                    </button>
                    <Badge variant="outline" className={`text-[11px] ${statusClasses(r.verification_status)}`}>
                      {statusLabels[r.verification_status] ?? r.verification_status}
                    </Badge>
                  </div>
                </div>
                <p className="mt-1.5 text-[13px] text-muted-foreground leading-5 flex-1">
                  <Highlight text={r.description} tokens={tokens} />
                </p>
                <div className="mt-3 flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                  <span className="rounded bg-stone-100 dark:bg-stone-800 px-1.5 py-0.5">{r.category}</span>
                  <span>{accessLabels[r.resource_access] ?? r.resource_access}</span>
                  <span aria-hidden="true">·</span>
                  <span>{r.region}</span>
                  {r.api_available ? (
                    <>
                      <span aria-hidden="true">·</span>
                      <span>API</span>
                    </>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>

          {pageCount > 1 ? (
            <nav aria-label="Catalog pagination" className="mt-7 flex items-center justify-center gap-2">
              <Button variant="outline" size="sm" disabled={safePage <= 1} onClick={() => setFilter({ page: safePage - 1 })}>
                <ChevronLeft className="h-4 w-4" aria-hidden="true" />
                Previous
              </Button>
              <span className="text-sm text-muted-foreground px-2">
                Page {safePage} of {pageCount}
              </span>
              <Button variant="outline" size="sm" disabled={safePage >= pageCount} onClick={() => setFilter({ page: safePage + 1 })}>
                Next
                <ChevronRight className="h-4 w-4" aria-hidden="true" />
              </Button>
            </nav>
          ) : null}
        </>
      )}

      <ResourceDetail
        record={data?.find((r) => r.id === f.detailId) ?? null}
        all={data ?? []}
        onClose={() => setFilter({ detailId: null })}
        onOpen={(id) => setFilter({ detailId: id })}
      />
    </div>
  );
}

/* --------------------------------- Detail dialog --------------------------------- */

function ResourceDetail({
  record,
  all,
  onClose,
  onOpen,
}: {
  record: ResourceRecord | null;
  all: ResourceRecord[];
  onClose: () => void;
  onOpen: (id: string) => void;
}) {
  const { has: hasBookmark, toggle: toggleBookmark } = useBookmarks();
  const { toast } = useToast();

  if (!record) return null;
  const related = relatedRecords(all, record);

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(record, null, 2));
      toast({ title: "Record JSON copied", description: record.name });
    } catch {
      toast({ title: "Copy failed", description: "The browser blocked clipboard access." });
    }
  };

  const rows: [string, React.ReactNode][] = [
    ["Category", record.category],
    ["Type", record.resource_type],
    ["Publisher", record.publisher],
    ["Region", record.region],
    ["Language", record.language],
    ["Access", accessLabels[record.resource_access] ?? record.resource_access],
    ["API available", record.api_available ? "Yes" : "No"],
    ["Official source", record.official_source ? "Yes: the publisher originates the content" : "No: aggregator or secondary service"],
    ["License", record.license],
    ["Verification", statusLabels[record.verification_status] ?? record.verification_status],
    ["Last checked", record.last_checked ?? "never live-checked"],
    ["Date added", record.date_added],
    ["Provenance", record.provenance?.source ?? "unknown"],
    ["Best for", record.best_for.join(", ")],
    ["Tags", record.tags.join(", ")],
  ];

  return (
    <Dialog open={record !== null} onOpenChange={(open) => { if (!open) onClose(); }}>
      <DialogContent className="max-w-xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between gap-3">
            <DialogTitle className="font-serif text-xl">{record.name}</DialogTitle>
            <button
              onClick={() => toggleBookmark(record.id)}
              aria-pressed={hasBookmark(record.id)}
              aria-label={hasBookmark(record.id) ? "Remove bookmark" : "Bookmark this resource"}
              className="p-1.5 rounded-sm text-stone-400 hover:text-green-800 dark:hover:text-green-400 transition-colors shrink-0"
            >
              <Star className={`h-5 w-5 ${hasBookmark(record.id) ? "fill-green-700 text-green-700 dark:fill-green-400 dark:text-green-400" : ""}`} aria-hidden="true" />
            </button>
          </div>
          <DialogDescription>{record.description}</DialogDescription>
        </DialogHeader>
        <div className="flex flex-wrap gap-2">
          <a
            href={record.canonical_url}
            target="_blank"
            rel="noopener noreferrer nofollow"
            className="inline-flex items-center gap-1.5 text-sm text-green-800 dark:text-green-400 underline underline-offset-2"
          >
            Visit {new URL(record.canonical_url).hostname}
            <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
          {record.documentation_url ? (
            <a
              href={record.documentation_url}
              target="_blank"
              rel="noopener noreferrer nofollow"
              className="inline-flex items-center gap-1.5 text-sm text-green-800 dark:text-green-400 underline underline-offset-2"
            >
              Documentation
              <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
            </a>
          ) : null}
          <button
            onClick={copyJson}
            className="inline-flex items-center gap-1.5 text-sm text-muted-foreground underline underline-offset-2 hover:text-foreground"
          >
            <Copy className="h-3.5 w-3.5" aria-hidden="true" />
            Copy record JSON
          </button>
        </div>
        <dl className="mt-2 divide-y divide-stone-100 dark:divide-stone-800 text-sm">
          {rows.map(([k, v]) => (
            <div key={k} className="grid grid-cols-[130px_1fr] gap-3 py-2">
              <dt className="text-muted-foreground">{k}</dt>
              <dd className="leading-6">{v}</dd>
            </div>
          ))}
        </dl>
        {related.length > 0 ? (
          <div>
            <h3 className="text-sm font-semibold">Related records</h3>
            <ul className="mt-2 grid gap-1.5">
              {related.map((r) => (
                <li key={r.id}>
                  <button
                    onClick={() => onOpen(r.id)}
                    className="w-full text-left rounded-sm border border-stone-200 dark:border-stone-800 px-3 py-2 hover:border-stone-300 dark:hover:border-stone-700 transition-colors"
                  >
                    <span className="text-sm font-medium">{r.name}</span>
                    <span className="ml-2 text-xs text-muted-foreground">{r.category}</span>
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{r.description}</p>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
        <p className="text-xs text-muted-foreground leading-5">
          Record id: {record.id}. Metadata describes the resource; it is not a statement about
          the quality of the resource&rsquo;s content. See the{" "}
          <button
            onClick={() => { onClose(); navigate("/docs/rl-quality-licensing"); }}
            className="underline hover:text-foreground"
          >
            verification methodology
          </button>
          .
        </p>
      </DialogContent>
    </Dialog>
  );
}
