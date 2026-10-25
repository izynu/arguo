"use client";

import { useJson } from "@/lib/hooks";
import { Skeleton } from "@/components/ui/skeleton";

type SiteStats = { eval_cases: number };

const metrics = [
  {
    name: "Citation validity",
    formula: "runs with zero audit errors / total runs",
    judged: "automated",
    note: "Every cited identifier must resolve to a recorded source and every claim must carry evidence.",
  },
  {
    name: "Citation support precision",
    formula: "citations whose passage plausibly supports the claim / all citations",
    judged: "automated estimate plus human review",
    note: "Automated pass compares claim text with the actual passages; a human rubric grades the sample.",
  },
  {
    name: "Unsupported-claim rate",
    formula: "claims with no evidence / all claims",
    judged: "automated",
    note: "Target is zero. Any unsupported claim is removed or qualified before a report ships.",
  },
  {
    name: "Source diversity",
    formula: "distinct registrable domains / sources cited",
    judged: "automated",
    note: "Syndicated copies of one upstream source count once, via independence groups.",
  },
  {
    name: "Primary-source coverage",
    formula: "primary-type sources / sources cited, where type is known",
    judged: "automated with caveats",
    note: "Source type defaults to unknown; the metric only counts records where it was established.",
  },
  {
    name: "Appropriate uncertainty",
    formula: "human rubric",
    judged: "human",
    note: "Graded against the written rubric: does confidence match evidence strength, are limits stated.",
  },
  {
    name: "Robustness to prompt injection",
    formula: "injection cases where embedded instructions were not followed / injection cases",
    judged: "automated for fixtures",
    note: "Adversarial fixtures embed instruction-like text in retrieved content.",
  },
  {
    name: "Runtime and search count",
    formula: "wall time and provider calls per run",
    judged: "automated",
    note: "Reported per profile so cost and coverage can be compared honestly.",
  },
];

const caseMix = [
  ["Stable factual questions", "answers that change rarely; tests citation discipline"],
  ["Time-sensitive questions", "requires date awareness and current sources"],
  ["Scientific findings", "study quality and limitation handling"],
  ["Academic literature", "scholarly search, metadata, gaps"],
  ["Market comparisons", "filings and official statistics over marketing copy"],
  ["Historical disputes", "competing interpretations, event vs publication dates"],
  ["Statistics and numerical claims", "units, denominators, contradiction scan"],
  ["Contradictory source material", "detection and honest reporting of conflict"],
  ["Weak evidence", "insufficient-evidence is the correct outcome"],
  ["Outdated sources", "recency assessment"],
  ["Unsupported user assumptions", "the tool should push back, not agree"],
  ["Missing evidence", "gaps named, follow-ups proposed"],
  ["Duplicate reporting", "syndication detected, independence respected"],
  ["Adversarial prompt injection", "embedded instructions treated as data"],
  ["Citation mismatches", "audit flags claims cited to the wrong source"],
];

export function EvalsView() {
  const { data: stats } = useJson<SiteStats>("/data/site-stats.json");

  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 py-10 flex-1 w-full">
      <h1 className="font-serif text-3xl font-bold tracking-tight">Evaluations</h1>
      <p className="mt-3 text-[15px] leading-7 max-w-2xl">
        Research quality is measured, not marketed. The repository ships{" "}
        {stats ? stats.eval_cases : "loading"} benchmark cases and a runner that reports
        structural metrics. No scores are published on this page because no run reproduced here
        has been audited: run the suite yourself and inspect the output.
      </p>

      <h2 className="font-serif text-2xl font-bold mt-10">Running the suite</h2>
      <div className="mt-3 rounded-md border border-stone-200 dark:border-stone-800 bg-stone-950 text-stone-100 p-4 overflow-x-auto">
        <pre className="text-[13px] font-mono leading-6"><code>{`# offline structural run (no API keys needed)
python3 evals/run_evals.py --offline

# limit to a smoke run
python3 evals/run_evals.py --offline --limit 5

# live run requires configured providers and prints real costs
python3 evals/run_evals.py --live`}</code></pre>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        Reports land in evals/reports/ as JSON with per-case results. The runner reports only
        what it measured, and says when a case requires human judgment.
      </p>

      <h2 className="font-serif text-2xl font-bold mt-10">What the metrics mean</h2>
      <div className="mt-4 space-y-2.5">
        {metrics.map((m) => (
          <div key={m.name} className="rounded-md border border-stone-200 dark:border-stone-800 p-4">
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <p className="font-semibold text-sm">{m.name}</p>
              <span className="text-[11px] rounded bg-stone-100 dark:bg-stone-800 px-1.5 py-0.5 text-muted-foreground">
                {m.judged}
              </span>
            </div>
            <p className="font-mono text-[12px] text-green-900 dark:text-green-400 mt-1.5">{m.formula}</p>
            <p className="text-[13px] text-muted-foreground leading-5 mt-1">{m.note}</p>
          </div>
        ))}
      </div>

      <h2 className="font-serif text-2xl font-bold mt-10">The case mix</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Cases mix answerable questions with deliberately ambiguous ones and questions whose
        evidence base is inadequate. Where fixtures embed gold facts, they carry provenance
        notes; nothing is manufactured to make a benchmark look complete.
      </p>
      <div className="mt-4 overflow-x-auto rounded-md border border-stone-200 dark:border-stone-800">
        <table className="w-full text-sm">
          <thead className="bg-stone-100 dark:bg-stone-800/70">
            <tr>
              <th className="px-3 py-2 text-left font-semibold border-b border-stone-200 dark:border-stone-800">Case family</th>
              <th className="px-3 py-2 text-left font-semibold border-b border-stone-200 dark:border-stone-800">What it probes</th>
            </tr>
          </thead>
          <tbody>
            {caseMix.map(([family, probes]) => (
              <tr key={family}>
                <td className="px-3 py-2 align-top font-medium border-b border-stone-100 dark:border-stone-800/60 whitespace-nowrap">{family}</td>
                <td className="px-3 py-2 align-top border-b border-stone-100 dark:border-stone-800/60 text-muted-foreground leading-6">{probes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-10 rounded-md border border-amber-300 dark:border-amber-700/60 bg-amber-50 dark:bg-amber-950/30 p-5">
        <p className="text-sm leading-6">
          These metrics measure structure and discipline. They do not measure truth. A report
          can pass every automated check and still be wrong if its underlying sources are
          wrong: that residual risk is documented, not hidden. See{" "}
          <a href="#/docs/qs-citation-precision" className="underline hover:text-foreground">citation precision</a>{" "}
          and{" "}
          <a href="#/docs/qs-high-stakes" className="underline hover:text-foreground">high-stakes limitations</a>.
        </p>
      </div>
    </div>
  );
}
