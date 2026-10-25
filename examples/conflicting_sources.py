"""Conflicting sources: watch the pipeline surface disagreement honestly.

This example runs the deep profile, which enables contradiction focus and a
second follow up round. The question targets the "vaccine" fixture key
whose entries deliberately disagree, so the run shows how contradictions,
weak corroboration, and audit warnings are reported instead of smoothed
away.

Environment variables (all optional):
  ARGUO_OUTPUT_DIR: where artifacts are written.
      Default for this script: ./runs/conflicting-sources-demo
  TAVILY_API_KEY: search key for live runs; unused while OFFLINE is True.
  ARGUO_MODEL_BASE_URL / ARGUO_MODEL_NAME /
  ARGUO_MODEL_API_KEY: model endpoint for live runs; unused while
  OFFLINE is True.

OFFLINE defaults to True in every example script: running this file never
touches the network. Change OFFLINE to False only after setting the keys
above.

Usage (from the repository root):
  PYTHONPATH=python python3 examples/conflicting_sources.py
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

OFFLINE = True
QUESTION = (
    "Do the demonstration fixtures disagree about vaccine effectiveness, "
    "and what do the safety surveillance passages say?"
)
OUTPUT_DIR = Path(
    os.environ.get("ARGUO_OUTPUT_DIR", "./runs/conflicting-sources-demo")
)

ARTIFACT_NAMES = (
    "report.md",
    "sources.json",
    "evidence.json",
    "research_plan.json",
    "audit.json",
    "manifest.json",
)


async def main() -> None:
    settings = get_settings({})
    profile = PROFILES["deep"]
    orchestrator = ResearchOrchestrator(settings, profile, offline=OFFLINE)
    manifest = await orchestrator.run(QUESTION, output_dir=OUTPUT_DIR)

    artifacts_dir = ""
    contradiction_count = 0
    for stage in manifest.stages:
        if stage.stage == "J-reporting" and stage.details.get("artifacts_dir"):
            artifacts_dir = str(stage.details["artifacts_dir"])
        if stage.stage == "G-verification":
            contradiction_count = int(stage.details.get("contradictions", 0))
    print(f"Run {manifest.run_id} finished (offline: {manifest.offline_mode})")
    print(
        f"Sources: {manifest.sources_retrieved}, evidence: "
        f"{manifest.evidence_records}, contradictions flagged by the "
        f"numeric scan: {contradiction_count}"
    )
    print("Open the report and check the Conflicting evidence section.")
    if artifacts_dir:
        base = Path(artifacts_dir)
        print("Artifacts:")
        for name in ARTIFACT_NAMES:
            print(f"  {base / name}")
    for warning in manifest.warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    asyncio.run(main())
