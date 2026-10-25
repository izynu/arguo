"""End-to-end offline orchestrator run into a temporary directory."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from arguo.config import PROFILES, get_settings
from arguo.orchestrator import ResearchOrchestrator

QUESTION = (
    "Does urban tree cover reduce summer heat in cities?"
)

EXPECTED_ARTIFACTS = (
    "report.md",
    "sources.json",
    "evidence.json",
    "research_plan.json",
    "audit.json",
    "manifest.json",
)


def run_offline(tmp_path: Path):
    settings = get_settings(env={})
    orchestrator = ResearchOrchestrator(
        settings, PROFILES["quick"], offline=True
    )
    return asyncio.run(orchestrator.run(QUESTION, output_dir=tmp_path))


def test_offline_run_writes_all_artifacts(tmp_path: Path) -> None:
    run_offline(tmp_path)
    for name in EXPECTED_ARTIFACTS:
        assert (tmp_path / name).is_file(), f"missing artifact: {name}"


def test_offline_report_contains_required_sections(tmp_path: Path) -> None:
    run_offline(tmp_path)
    report = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "## Claim and evidence table" in report
    assert "## Research question and scope" in report
    assert "This run used offline fixture providers" in report


def test_audit_json_parses_and_has_issues_list(tmp_path: Path) -> None:
    run_offline(tmp_path)
    audit = json.loads((tmp_path / "audit.json").read_text(encoding="utf-8"))
    assert isinstance(audit["issues"], list)
    assert audit["citations_checked"] >= 1
    assert "Automated checks" in audit["automated_note"]
    error_count = sum(
        1 for issue in audit["issues"] if issue["severity"] == "error"
    )
    assert error_count == 0


def test_manifest_records_at_least_ten_stages(tmp_path: Path) -> None:
    manifest = run_offline(tmp_path)
    assert len(manifest.stages) >= 10
    names = {stage.stage for stage in manifest.stages}
    for stage in (
        "A-intake", "B-planning", "C-search", "D-retrieval", "E-evidence",
        "F-gap-analysis", "G-verification", "H-synthesis", "I-claim-audit",
        "J-reporting",
    ):
        assert stage in names
    payload = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert payload["run_id"] == manifest.run_id
    assert payload["offline_mode"] is True
    assert payload["providers"]["search"] == "offline-fixture"
    assert len(payload["stages"]) >= 10


def test_plan_and_ledger_artifacts_are_consistent(tmp_path: Path) -> None:
    run_offline(tmp_path)
    plan = json.loads((tmp_path / "research_plan.json").read_text(encoding="utf-8"))
    assert plan["generated_by"] == "heuristic"
    assert plan["subquestions"]
    sources = json.loads((tmp_path / "sources.json").read_text(encoding="utf-8"))
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert sources["sources"], "fixture run should retrieve sources"
    assert evidence["evidence"], "fixture run should extract passages"
    for source in sources["sources"]:
        assert source["url"].startswith("https://")
        assert source["retrieved_at"]
