"use client";

import { Badge } from "@/components/ui/badge";

const stages = [
  { id: "A", name: "Intake", detail: "Validates the question, identifies depth, date constraints, and output needs. Never blocks progress with needless questions." },
  { id: "B", name: "Planning", detail: "Produces a ResearchPlan: subquestions, diverse queries, evidence requirements, and anticipated limitations. Heuristic planner offline, model planner when configured." },
  { id: "C", name: "Search", detail: "Queries the configured provider, normalizes results into one shape, deduplicates by canonical URL and title-domain pairs, and records retrieval metadata." },
  { id: "D", name: "Retrieval", detail: "Fetches pages through the SSRF guard with redirect revalidation, content-type allowlists, byte caps, and timeouts. Failures become recorded access notes." },
  { id: "E", name: "Evidence", detail: "Splits page text into passages and records them in the evidence ledger with source, retrieval time, relevance, and content hashes." },
  { id: "F", name: "Gap analysis", detail: "Finds subquestions with no evidence and runs at most one or two focused follow-up rounds in the default profiles." },
  { id: "G", name: "Verification", detail: "Applies the source rubric, groups corroboration by registrable domain, flags syndication, and scans for numeric contradictions." },
  { id: "H", name: "Synthesis", detail: "Assembles findings from recorded evidence only. Offline synthesis is deterministic and honest about its limits." },
  { id: "I", name: "Claim audit", detail: "Validates that every citation resolves, every claim has evidence, and unused sources are marked background." },
  { id: "J", name: "Reporting", detail: "Writes report.md plus sources.json, evidence.json, research_plan.json, audit.json, and manifest.json." },
];

const verdicts = [
  ["supported", "Independent evidence passages support the claim."],
  ["partially-supported", "Some support exists but it is thinner or narrower than the claim."],
  ["contradicted", "Evidence conflicts with the claim."],
  ["insufficient-evidence", "Nothing recorded bears on the claim."],
  ["source-unavailable", "A cited source could not be retrieved."],
  ["requires-human-review", "Automated checks cannot decide. A person should look."],
];

const rubric = [
  ["Authority for the question", "Is this publisher an authority on this specific question, not just on the general topic?"],
  ["Primary vs secondary", "Does the source originate the information or repeat it?"],
  ["Methodological quality", "For studies: design, sample, analysis. Not applicable for many documents."],
  ["Recency", "Parsed from real dates only. Unknown dates stay unknown."],
  ["Directness", "Does the passage address the claim directly, indirectly, or by inference?"],
  ["Transparency", "Are methods, data, and provenance documented?"],
  ["Conflicts of interest", "Declared, possible, or none known. Defaults to unknown."],
  ["Independent corroboration", "Do distinct registrable domains agree, or is one upstream source syndicated?"],
  ["Limitations", "Material constraints recorded against the evidence record."],
  ["Publisher provenance", "Who publishes this and where it sits relative to the event."],
];

export function MethodologyView() {
  return (
    <div className="mx-auto max-w-4xl px-4 sm:px-6 py-10 flex-1 w-full">
      <h1 className="font-serif text-3xl font-bold tracking-tight">Methodology</h1>
      <p className="mt-3 text-[15px] leading-7 max-w-2xl">
        Arguo is built around one idea: a research tool should be able to show its
        work. Every claim in a report traces to recorded evidence, every evidence record traces
        to a retrieved source, and every stage leaves an inspectable artifact.
      </p>

      <h2 className="font-serif text-2xl font-bold mt-12 mb-1">The pipeline</h2>
      <p className="text-sm text-muted-foreground mb-5">Ten stages, each independently observable and testable.</p>
      <ol className="space-y-2.5">
        {stages.map((s) => (
          <li key={s.id} className="flex gap-4 rounded-md border border-stone-200 dark:border-stone-800 p-4">
            <span className="shrink-0 h-7 w-7 rounded-md bg-green-800 dark:bg-green-700 text-white text-sm font-semibold grid place-items-center" aria-hidden="true">
              {s.id}
            </span>
            <div>
              <p className="font-semibold text-sm">{s.name}</p>
              <p className="text-[13px] text-muted-foreground leading-5 mt-1">{s.detail}</p>
            </div>
          </li>
        ))}
      </ol>

      <h2 className="font-serif text-2xl font-bold mt-12 mb-1">The evidence ledger</h2>
      <p className="mt-2 text-[15px] leading-7">
        The ledger is the system&rsquo;s core data structure. Each record pairs a passage with
        its source and context, and missing values stay explicitly null: unknown dates are
        never invented, unknown publishers are never guessed.
      </p>
      <div className="mt-4 rounded-md border border-stone-200 dark:border-stone-800 bg-stone-950 text-stone-100 p-4 overflow-x-auto">
        <pre className="text-[13px] font-mono leading-6"><code>{`{
  "evidence_id": "E7",
  "claim_ids": ["C3"],
  "source_id": "S2",
  "relevant_passage": "Installations reached 1.6 TW in 2023...",
  "published_at": null,          // stays null unless actually known
  "retrieved_at": "2026-10-24T09:14:02+00:00",
  "supports_or_contradicts": "supports",
  "relevance": "direct",
  "independence_group": "example.org",
  "verification_status": "requires-human-review",
  "content_hash": "9f2a..."
}`}</code></pre>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        Corroboration is grouped by registrable domain, so three outlets repeating one press
        release count as one independent source, not three.
      </p>

      <h2 className="font-serif text-2xl font-bold mt-12 mb-1">Verdict vocabulary</h2>
      <p className="mt-2 text-[15px] leading-7">
        Claims and citations get one of six verdicts. There is no numeric trust score, and
        nothing is marked verified merely because a model said so.
      </p>
      <dl className="mt-4 space-y-2">
        {verdicts.map(([name, desc]) => (
          <div key={name} className="flex gap-3 items-start rounded-md border border-stone-200 dark:border-stone-800 px-4 py-2.5">
            <dt><Badge variant="outline" className="font-mono text-[11px] shrink-0 mt-0.5">{name}</Badge></dt>
            <dd className="text-sm text-muted-foreground leading-5">{desc}</dd>
          </div>
        ))}
      </dl>

      <h2 className="font-serif text-2xl font-bold mt-12 mb-1">Source quality rubric</h2>
      <p className="mt-2 text-[15px] leading-7">
        Ten transparent criteria produce a qualitative assessment. Domain reputation and
        popularity are deliberately excluded as proof of truth.
      </p>
      <div className="mt-4 overflow-x-auto rounded-md border border-stone-200 dark:border-stone-800">
        <table className="w-full text-sm">
          <thead className="bg-stone-100 dark:bg-stone-800/70">
            <tr>
              <th className="px-3 py-2 text-left font-semibold border-b border-stone-200 dark:border-stone-800">Criterion</th>
              <th className="px-3 py-2 text-left font-semibold border-b border-stone-200 dark:border-stone-800">What it asks</th>
            </tr>
          </thead>
          <tbody>
            {rubric.map(([c, q]) => (
              <tr key={c}>
                <td className="px-3 py-2 align-top font-medium border-b border-stone-100 dark:border-stone-800/60 whitespace-nowrap">{c}</td>
                <td className="px-3 py-2 align-top border-b border-stone-100 dark:border-stone-800/60 text-muted-foreground leading-6">{q}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="font-serif text-2xl font-bold mt-12 mb-1">What the audit can and cannot do</h2>
      <p className="mt-2 text-[15px] leading-7">
        Automated citation checks verify internal consistency: that cited identifiers exist,
        that claims have evidence, that URLs are well formed, that passages plausibly support
        their claims. They cannot establish truth, and the audit output says so verbatim in
        every report. Confidence in reports is qualitative and reasoned, never a fabricated
        percentage.
      </p>

      <div className="mt-10 rounded-md border border-stone-200 dark:border-stone-800 bg-stone-100/50 dark:bg-stone-900/40 p-5">
        <p className="text-sm">
          The full method, with field-level schemas and rules, is documented in the{" "}
          <a href="#/docs/cc-overview" className="text-green-800 dark:text-green-400 underline underline-offset-2">core concepts</a>{" "}
          section. Security reasoning lives in{" "}
          <a href="#/docs/qs-prompt-injection" className="text-green-800 dark:text-green-400 underline underline-offset-2">quality and safety</a>.
        </p>
      </div>
    </div>
  );
}
