"use client";

import { useJson } from "@/lib/hooks";
import { Skeleton } from "@/components/ui/skeleton";

type StatsFull = {
  generated_at: string;
  total_records: number;
  categories: Record<string, number>;
  category_count: number;
  regions: Record<string, number>;
  region_count: number;
  resource_types: Record<string, number>;
  access_modes: Record<string, number>;
  verification_status: Record<string, number>;
  languages: Record<string, number>;
  api_availability: Record<string, number>;
};

const accessLabels: Record<string, string> = {
  open: "Open",
  "free-registration": "Free registration",
  "partial-open": "Partial open",
  paid: "Paid",
  mixed: "Mixed",
};

function BarList({
  title,
  caption,
  entries,
  formatLabel,
}: {
  title: string;
  caption: string;
  entries: [string, number][];
  formatLabel?: (k: string) => string;
}) {
  const max = Math.max(...entries.map(([, n]) => n), 1);
  return (
    <section aria-label={title} className="rounded-md border border-stone-200 dark:border-stone-800 p-4">
      <h2 className="font-serif font-semibold">{title}</h2>
      <p className="mt-0.5 text-xs text-muted-foreground">{caption}</p>
      <ul className="mt-3 space-y-1.5">
        {entries.map(([k, n]) => (
          <li key={k} className="grid grid-cols-[minmax(120px,220px)_1fr_48px] items-center gap-2 text-xs">
            <span className="truncate text-muted-foreground" title={k}>{formatLabel ? formatLabel(k) : k}</span>
            <span className="h-2 bg-stone-100 dark:bg-stone-800 overflow-hidden">
              <span
                className="block h-full bg-green-700 dark:bg-green-500"
                style={{ width: `${Math.max((n / max) * 100, 1)}%` }}
              />
            </span>
            <span className="text-right tabular-nums text-muted-foreground">{n.toLocaleString("en-US")}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function topEntries(record: Record<string, number>, count: number | null): [string, number][] {
  const all = Object.entries(record).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
  return count === null ? all : all.slice(0, count);
}

export function StatsView() {
  const { data, loading, error } = useJson<StatsFull>("/data/stats.json");

  if (error) {
    return (
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10 flex-1 w-full">
        <p className="text-sm text-red-700 dark:text-red-400">
          Failed to load statistics: {error}. Regenerate them with make site-stats.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl px-4 sm:px-6 py-10 flex-1 w-full">
      <div className="max-w-3xl">
        <h1 className="font-serif text-3xl font-bold tracking-tight">Catalog statistics</h1>
        <p className="mt-2 text-[15px] leading-7 text-muted-foreground">
          Every number on this page is generated from the shipped catalog by tools/generate_site_stats.py.
          Nothing here is estimated or padded: the counts are the counts.
        </p>
      </div>

      {loading || !data ? (
        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => <Skeleton key={i} className="h-28 w-full" />)}
        </div>
      ) : (
        <>
          <dl className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              ["Records", data.total_records.toLocaleString("en-US")],
              ["Categories", data.category_count.toLocaleString("en-US")],
              ["Regions", data.region_count.toLocaleString("en-US")],
              ["Live-verified", (data.verification_status.verified ?? 0).toLocaleString("en-US")],
            ].map(([label, value]) => (
              <div key={label} className="rounded-md border border-stone-200 dark:border-stone-800 p-4">
                <dt className="text-xs text-muted-foreground">{label}</dt>
                <dd className="mt-1 font-serif text-2xl font-bold tabular-nums">{value}</dd>
              </div>
            ))}
          </dl>
          <p className="mt-2 text-xs text-muted-foreground">
            Generated {data.generated_at}. Live-verified means a checker confirmed the URL resolved on that date;
            the remaining records are documented but not yet live-checked.
          </p>

          <div className="mt-8 grid gap-4 lg:grid-cols-2">
            <BarList
              title="Verification status"
              caption="Where each record stands in the verification pipeline"
              entries={topEntries(data.verification_status, null)}
            />
            <BarList
              title="Access models"
              caption="How the underlying resources can be used"
              entries={topEntries(data.access_modes, null)}
              formatLabel={(k) => accessLabels[k] ?? k}
            />
            <BarList
              title="API availability"
              caption="Records where the publisher exposes a documented API"
              entries={topEntries(data.api_availability, null)}
              formatLabel={(k) => (k === "api" ? "Has documented API" : "No API")}
            />
            <BarList
              title="Resource types"
              caption="Structural type of each catalog record (top 12)"
              entries={topEntries(data.resource_types, 12)}
            />
            <BarList
              title="Interface languages"
              caption="Primary interface language of each resource (top 12)"
              entries={topEntries(data.languages, 12)}
            />
            <BarList
              title="Top regions"
              caption={`Publishing country or region (top 15 of ${data.region_count})`}
              entries={topEntries(data.regions, 15)}
            />
          </div>

          <div className="mt-4">
            <BarList
              title="All categories"
              caption={`Every one of the ${data.category_count} categories, largest first`}
              entries={topEntries(data.categories, null)}
            />
          </div>
        </>
      )}
    </div>
  );
}
