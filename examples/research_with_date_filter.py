"""Research with a date filter: restrict evidence to a publication window.

This example runs the quick profile with since and until dates, so the plan
carries an explicit time boundary and the report states the date range. The
question targets the "interest rate" fixture key so the offline run has
dated material to work with.

Environment variables (all optional):
  ARGUO_OUTPUT_DIR: where artifacts are written.
      Default for this script: ./runs/date-filter-demo
  TAVILY_API_KEY: search key for live runs; unused while OFFLINE is True.
  ARGUO_MODEL_BASE_URL / ARGUO_MODEL_NAME /
  ARGUO_MODEL_API_KEY: model endpoint for live runs; unused while
  OFFLINE is True.

OFFLINE defaults to True in every example script: running this file never
touches the network. Change OFFLINE to False only after setting the keys
above.

Usage (from the repository root):
  PYTHONPATH=python python3 examples/research_with_date_filter.py
"""

from __future__ import annotations

import asyncio
import datetime as dt
import os
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

OFFLINE = True
QUESTION = (
    "How did the demonstration central bank interest rate decision affect "
    "market reaction in early 2025?"
)
OUTPUT_DIR = Path(
    os.environ.get("ARGUO_OUTPUT_DIR", "./runs/date-filter-demo")
)
SINCE = dt.date(2025, 1, 1)
UNTIL = dt.date(2025, 12, 31)

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
    manifest = await orchestrator.run(
        QUESTION, since=SINCE, until=UNTIL, output_dir=OUTPUT_DIR
    )

    artifacts_dir = ""
    for stage in manifest.stages:
        if stage.stage == "J-reporting" and stage.details.get("artifacts_dir"):
            artifacts_dir = str(stage.details["artifacts_dir"])
    print(f"Run {manifest.run_id} finished (offline: {manifest.offline_mode})")
    print(f"Date window: {SINCE.isoformat()} to {UNTIL.isoformat()}")
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
