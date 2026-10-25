"use client";

import { useJson, navigate } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, FileText, Database, FolderCheck, ScrollText } from "lucide-react";

type SiteStats = {
  catalog_records: number;
  catalog_categories: number;
  regions: number;
  docs_pages: number;
  eval_cases: number;
  pipeline_stages: number;
};

const stages = [
  ["A", "Intake", "Validate the question, depth, and date constraints"],
  ["B", "Planning", "Produce a structured plan of subquestions and queries"],
  ["C", "Search", "Query the configured provider, deduplicate results"],
  ["D", "Retrieval", "Fetch pages with size, timeout, and SSRF limits"],
  ["E", "Evidence", "Extract passages into the evidence ledger with provenance"],
  ["F", "Gap analysis", "Find subquestions without evidence, run follow-ups"],
  ["G", "Verification", "Source rubric, corroboration, contradiction scan"],
  ["H", "Synthesis", "Assemble findings that only cite recorded evidence"],
  ["I", "Claim audit", "Check every citation resolves and every claim is supported"],
  ["J", "Reporting", "Write the report and machine-readable artifacts"],
];

const artifacts = [
  { name: "report.md", desc: "The research report with 15 fixed sections, inline [S#] citations, and an audit summary." },
  { name: "sources.json", desc: "Every retrieved source with URL, retrieval timestamp, and explicit unknown fields." },
  { name: "evidence.json", desc: "Passages linked to claims, with independence groups and content hashes." },
  { name: "research_plan.json", desc: "The inspectable plan: subquestions, queries, limitations." },
  { name: "audit.json", desc: "Citation issues, support-review verdicts, and contradiction records." },
  { name: "manifest.json", desc: "Stage timings, budgets used, providers, and warnings for the run." },
];

const deliverables = [
  {
    icon: ScrollText,
    title: "Agent Skill",
    body: "A portable SKILL.md with 20 reference files that any compatible agent can load, following progressive disclosure.",
    href: "#/docs/sk-overview",
  },
  {
    icon: FileText,
    title: "Python research agent",
    body: "A CLI and library that runs a 10-stage pipeline and writes auditable artifacts. Works offline against fixtures for testing.",
    href: "#/docs/gs-quickstart",
  },
  {
    icon: Database,
    title: "Resource catalog",
    body: "Real, schema-validated records of research resources: government statistics, academic indexes, archives, and APIs.",
    href: "#/resources",
  },
  {
    icon: FolderCheck,
    title: "Evaluation suite",
    body: "Structural benchmark cases that measure citation validity, unsupported-claim rate, and source diversity without fabricating scores.",
    href: "#/evals",
  },
];

const ledgerSample = [
  { claim: "Climate adaptation budgets across example cities", evidence: "E1 E2", sources: "S1 S2", verdict: "supported", confidence: "medium" },
  { claim: "Tree canopy share paired with summer surface temperature", evidence: "E1 E2", sources: "S1 S2", verdict: "supported", confidence: "medium" },
];

export function HomeView() {
  const { data: stats } = useJson<SiteStats>("/data/site-stats.json");

  const numbers: { label: string; value: string }[] = [
    { label: "pipeline stages", value: String(stats?.pipeline_stages ?? "10") },
    { label: "catalog records", value: stats ? stats.catalog_records.toLocaleString("en-US") : "" },
    { label: "categories", value: stats ? String(stats.catalog_categories) : "" },
    { label: "documentation pages", value: stats ? String(stats.docs_pages) : "" },
    { label: "benchmark cases", value: stats ? String(stats.eval_cases) : "" },
  ].filter((n) => n.value !== "");

  return (
    <div>
      <section className="border-b border-stone-200 dark:border-stone-800">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-16 sm:py-24">
          <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-start lg:gap-14">
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant="outline" className="border-stone-300 dark:border-stone-700 text-muted-foreground font-normal">
                  Open source, Apache-2.0
                </Badge>
                <Badge variant="outline" className="border-stone-300 dark:border-stone-700 text-muted-foreground font-normal">
                  Python 3.11+
                </Badge>
                <Badge variant="outline" className="border-stone-300 dark:border-stone-700 text-muted-foreground font-normal">
                  Offline mode, no keys required
                </Badge>
              </div>
              <h1 className="mt-5 font-serif text-4xl sm:text-5xl font-bold tracking-tight max-w-3xl text-balance">
                Arguo
              </h1>
              <p className="mt-3 font-serif text-lg sm:text-xl text-muted-foreground max-w-2xl">
                The open research intelligence toolkit.
              </p>
              <p className="mt-5 text-[15px] leading-7 max-w-2xl text-foreground/90">
                Arguo plans searches, records what each source actually says, checks
                whether citations support their claims, and writes reports that state their own
                limits. It does not promise accuracy: it makes research auditable.
              </p>
              <div className="mt-7 flex flex-wrap gap-3">
                <Button onClick={() => navigate("/docs/gs-quickstart")} className="bg-green-800 hover:bg-green-900 dark:bg-green-700 dark:hover:bg-green-600">
                  Get started
                  <ArrowRight className="ml-1.5 h-4 w-4" aria-hidden="true" />
                </Button>
                <Button variant="outline" onClick={() => navigate("/resources")}>
                  Browse the catalog
                </Button>
                <Button variant="ghost" onClick={() => navigate("/methodology")}>
                  Read the methodology
                </Button>
              </div>
              <p className="mt-6 text-xs text-muted-foreground">
                Built by Zynu and Shraddha. Maintained at github.com/izynu/arguo.
              </p>
            </div>

            <div className="rounded-lg border border-stone-200 dark:border-stone-800 bg-stone-50 dark:bg-stone-900/40 overflow-hidden">
              <div className="px-5 pt-5">
                <h2 className="font-serif text-base font-bold">Every claim carries its evidence</h2>
                <p className="mt-1 text-[13px] text-muted-foreground leading-5">
                  Each run ends in a claim table where every row points to numbered evidence
                  records and sources. This one is from the bundled sample report.
                </p>
              </div>
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-[12.5px]">
                  <thead>
                    <tr className="border-y border-stone-200 dark:border-stone-800 bg-stone-100/70 dark:bg-stone-900/70 text-muted-foreground">
                      <th className="px-5 py-2 font-medium">Claim</th>
                      <th className="px-3 py-2 font-medium">Evidence</th>
                      <th className="px-3 py-2 font-medium">Sources</th>
                      <th className="px-3 py-2 font-medium">Verdict</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ledgerSample.map((row) => (
                      <tr key={row.claim} className="border-b border-stone-200 dark:border-stone-800 last:border-0 align-top">
                        <td className="px-5 py-3 leading-5">{row.claim}</td>
                        <td className="px-3 py-3 font-mono text-green-900 dark:text-green-400 whitespace-nowrap">{row.evidence}</td>
                        <td className="px-3 py-3 font-mono text-green-900 dark:text-green-400 whitespace-nowrap">{row.sources}</td>
                        <td className="px-3 py-3 whitespace-nowrap">
                          {row.verdict}{" "}
                          <span className="text-muted-foreground">({row.confidence})</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="px-5 py-3 text-[11.5px] text-muted-foreground">
                Offline fixture run, clearly labeled. See the full sample report and the six
                artifacts a run writes below.
              </div>
            </div>
          </div>
        </div>
      </section>

      {numbers.length > 0 ? (
        <section className="border-b border-stone-200 dark:border-stone-800 bg-stone-100/50 dark:bg-stone-900/40">
          <div className="mx-auto max-w-6xl px-4 sm:px-6 py-8">
            <dl className="grid grid-cols-2 sm:grid-cols-5 gap-6">
              {numbers.map((n) => (
                <div key={n.label}>
                  <dd className="font-serif text-2xl sm:text-3xl font-bold text-green-900 dark:text-green-400">{n.value}</dd>
                  <dt className="text-xs text-muted-foreground mt-1">{n.label}</dt>
                </div>
              ))}
            </dl>
            <p className="mt-4 text-xs text-muted-foreground">
              Counts are generated from the repository contents by build scripts. They describe
              what ships here, not adoption or quality.
            </p>
          </div>
        </section>
      ) : null}

      <section className="border-b border-stone-200 dark:border-stone-800">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-14">
          <h2 className="font-serif text-2xl font-bold tracking-tight">What ships in this repository</h2>
          <div className="mt-7 grid gap-4 sm:grid-cols-2">
            {deliverables.map((d) => (
              <a
                key={d.title}
                href={d.href}
                className="group rounded-lg border border-stone-200 dark:border-stone-800 bg-background p-5 hover:border-green-800 dark:hover:border-green-600 transition-colors"
              >
                <d.icon className="h-5 w-5 text-green-800 dark:text-green-400" aria-hidden="true" />
                <h3 className="font-serif text-lg font-bold mt-3">{d.title}</h3>
                <p className="text-sm text-muted-foreground leading-6 mt-1.5">{d.body}</p>
              </a>
            ))}
          </div>
        </div>
      </section>

      <section className="border-b border-stone-200 dark:border-stone-800 bg-stone-100/50 dark:bg-stone-900/40">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-14">
          <h2 className="font-serif text-2xl font-bold tracking-tight">How a research run works</h2>
          <p className="mt-2 text-[15px] text-muted-foreground max-w-2xl">
            Ten observable stages. Each one can be inspected, tested, and audited on its own.
          </p>
          <ol className="mt-7 grid gap-2.5 sm:grid-cols-2">
            {stages.map(([letter, name, desc]) => (
              <li
                key={letter}
                className="flex gap-3.5 rounded-md border border-stone-200 dark:border-stone-800 px-4 py-3 bg-background"
              >
                <span className="shrink-0 h-7 w-7 rounded-md bg-green-800 dark:bg-green-700 text-white text-sm font-semibold grid place-items-center" aria-hidden="true">
                  {letter}
                </span>
                <div>
                  <p className="text-sm font-semibold">{name}</p>
                  <p className="text-[13px] text-muted-foreground leading-5 mt-0.5">{desc}</p>
                </div>
              </li>
            ))}
          </ol>
          <a href="#/methodology" className="inline-flex items-center gap-1 mt-5 text-sm text-green-800 dark:text-green-400 hover:underline underline-offset-2">
            Full methodology
            <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
          </a>
        </div>
      </section>

      <section className="border-b border-stone-200 dark:border-stone-800">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-14">
          <h2 className="font-serif text-2xl font-bold tracking-tight">What a run produces</h2>
          <p className="mt-2 text-[15px] text-muted-foreground max-w-2xl">
            Every run writes six artifacts. The report cites evidence identifiers that resolve
            into the machine-readable files.
          </p>
          <div className="mt-7 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {artifacts.map((a) => (
              <div key={a.name} className="rounded-md border border-stone-200 dark:border-stone-800 p-4">
                <p className="font-mono text-sm font-semibold text-green-900 dark:text-green-400">{a.name}</p>
                <p className="text-[13px] text-muted-foreground leading-5 mt-1.5">{a.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section>
        <div className="mx-auto max-w-6xl px-4 sm:px-6 py-14">
          <div className="rounded-lg border border-amber-300 dark:border-amber-700/60 bg-amber-50 dark:bg-amber-950/30 p-6">
            <h2 className="font-serif text-lg font-bold">Honest limitations</h2>
            <ul className="mt-3 space-y-2 text-sm leading-6 text-foreground/90 list-disc ml-5">
              <li>Automated citation checks verify internal consistency and passage support. They cannot guarantee truth.</li>
              <li>Offline mode runs against labeled fixtures. It demonstrates the pipeline; it does not perform research.</li>
              <li>Catalog records ship as &ldquo;documented&rdquo;, not &ldquo;verified&rdquo;, until the link checker has live-checked them.</li>
              <li>Heuristic quality signals are rough. The project deliberately avoids numerical trust scores.</li>
              <li>For medical, legal, financial, or safety decisions, treat output as a starting point for human review.</li>
            </ul>
            <a href="#/docs/qs-high-stakes" className="inline-block mt-4 text-sm text-green-800 dark:text-green-400 hover:underline underline-offset-2">
              Read the full limitations statement
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
