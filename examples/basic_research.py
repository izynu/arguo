"""Basic offline research run: the fastest way to see every artifact.

This example runs the full pipeline (planning, search, retrieval, evidence
ledger, verification, synthesis, audit, report) for one question using the
quick profile, then prints the paths of the artifacts it wrote.

Environment variables (all optional):
  ARGUO_OUTPUT_DIR: where artifacts are written.
      Default for this script: ./runs/basic-research
  TAVILY_API_KEY: search key for live runs; unused while OFFLINE is True.
  ARGUO_MODEL_BASE_URL / ARGUO_MODEL_NAME /
  ARGUO_MODEL_API_KEY: model endpoint for live runs; unused while
  OFFLINE is True.

OFFLINE defaults to True in every example script: running this file never
touches the network. It uses clearly labeled fixture content instead. To go
live, set OFFLINE to False and provide the keys above.

Usage (from the repository root):
  PYTHONPATH=python python3 examples/basic_research.py
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

OFFLINE = True
QUESTION = (
    "Does urban tree cover reduce summer heat in cities according to "
    "climate records?"
)
OUTPUT_DIR = Path(os.environ.get("ARGUO_OUTPUT_DIR", "./runs/basic-research"))

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
    orchestrator = ResearchOrchestrator(
        settings, PROFILES["quick"], offline=OFFLINE
    )
    manifest = await orchestrator.run(QUESTION, output_dir=OUTPUT_DIR)

    artifacts_dir = ""
    for stage in manifest.stages:
        if stage.stage == "J-reporting" and stage.details.get("artifacts_dir"):
            artifacts_dir = str(stage.details["artifacts_dir"])
    print(f"Run {manifest.run_id} finished (offline: {manifest.offline_mode})")
    print(
        f"Sources: {manifest.sources_retrieved}, evidence: "
        f"{manifest.evidence_records}, model calls: {manifest.model_calls}"
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
