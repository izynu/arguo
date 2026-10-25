"""CLI integration tests using typer's CliRunner. No network access."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

import arguo.cli as cli_module
from arguo.cli import app

runner = CliRunner()

QUESTION = "Does urban tree cover reduce summer heat in cities?"


def test_help_exits_zero_and_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    for command in ("research", "resources", "config", "doctor", "cache", "eval"):
        assert command in result.output


def test_doctor_runs_without_exception() -> None:
    result = runner.invoke(app, ["doctor"])
    assert "Traceback" not in result.output
    assert result.exception is None
    assert result.exit_code in (0, 1)
    assert "python" in result.output


def test_resources_stats_against_tmp_catalog(
    tmp_path: Path, tmp_catalog, monkeypatch
) -> None:
    # CATALOG_PATH is a module attribute of arguo.cli; patching it
    # redirects every _load_catalog call in the commands under test.
    monkeypatch.setattr(cli_module, "CATALOG_PATH", tmp_catalog)
    monkeypatch.setattr(cli_module, "STATS_PATH", tmp_path / "missing-stats.json")
    result = runner.invoke(app, ["resources", "stats"])
    assert result.exit_code == 0, result.output
    assert "Records: 3" in result.output
    assert "Categories: 3" in result.output
    assert "documented" in result.output


def test_resources_search_matches_substring(tmp_catalog, monkeypatch) -> None:
    monkeypatch.setattr(cli_module, "CATALOG_PATH", tmp_catalog)
    result = runner.invoke(app, ["resources", "search", "archive", "--limit", "5"])
    assert result.exit_code == 0
    assert "1 matching record(s)" in result.output
    assert "example-archive" in result.output


def test_research_offline_end_to_end(tmp_path: Path) -> None:
    output_dir = tmp_path / "run"
    result = runner.invoke(
        app,
        [
            "research",
            "test question",
            "--offline",
            "--profile",
            "quick",
            "--output-dir",
            str(output_dir),
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Research run complete" in result.output
    for name in (
        "report.md",
        "sources.json",
        "evidence.json",
        "research_plan.json",
        "audit.json",
        "manifest.json",
    ):
        assert (output_dir / name).is_file(), f"missing artifact: {name}"
    report = (output_dir / "report.md").read_text(encoding="utf-8")
    assert "## Claim and evidence table" in report


def test_research_rejects_unknown_profile(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "research",
            "test question",
            "--offline",
            "--profile",
            "bogus",
            "--output-dir",
            str(tmp_path / "nope"),
        ],
    )
    assert result.exit_code != 0
    assert "Unknown profile" in result.output
