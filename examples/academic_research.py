"""Academic research profile: scholarly mode with study metadata emphasis.

This example runs the academic profile, which uses scholarly oriented
queries, a longer report, and evidence requirements that name study types.
The question targets the "vaccine" fixture key so the offline run has study
style content to work with.

Environment variables (all optional):
  ARGUO_OUTPUT_DIR: where artifacts are written.
      Default for this script: ./runs/academic-demo
  TAVILY_API_KEY: search key for live runs; unused while OFFLINE is True.
  ARGUO_MODEL_BASE_URL / ARGUO_MODEL_NAME /
  ARGUO_MODEL_API_KEY: model endpoint for live runs; unused while
  OFFLINE is True.

OFFLINE defaults to True in every example script: running this file never
touches the network. Change OFFLINE to False only after setting the keys
above.

Usage (from the repository root):
  PYTHONPATH=python python3 examples/academic_research.py
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

OFFLINE = True
QUESTION = (
    "What do controlled studies say about vaccine effectiveness and safety "
    "surveillance in demonstration datasets?"
)
OUTPUT_DIR = Path(os.environ.get("ARGUO_OUTPUT_DIR", "./runs/academic-demo"))

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
    profile = PROFILES["academic"]
    orchestrator = ResearchOrchestrator(settings, profile, offline=OFFLINE)
    manifest = await orchestrator.run(QUESTION, output_dir=OUTPUT_DIR)

    artifacts_dir = ""
    for stage in manifest.stages:
        if stage.stage == "J-reporting" and stage.details.get("artifacts_dir"):
            artifacts_dir = str(stage.details["artifacts_dir"])
    print(f"Run {manifest.run_id} finished (offline: {manifest.offline_mode})")
    print(
        f"Profile: {profile.name}, scholarly mode: {profile.scholarly_mode}, "
        f"report length: {profile.report_length}"
    )
    print(
        f"Sources: {manifest.sources_retrieved}, evidence: "
        f"{manifest.evidence_records}"
    )
    if artifacts_dir:
        base = Path(artifacts_dir)
        print("Artifacts:")
        for name in ARTIFACT_NAMES:
            print(f"  {base / name}")
    for warning in manifest.warnings:
        print(f"Warning: {warning}")


if __name__ == "__main__":
    asyncio.run(main())
