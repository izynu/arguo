"""Arguo command line interface.

Commands: research, resources (search, list, validate, stats), config check,
doctor, cache clear, and eval run. Failures print "Error: ..." to stderr and
exit with the matching EvidenceLedgerError exit code. Secret values are
never printed.
"""

from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from arguo.config import PROFILES, Settings
from arguo.exceptions import ConfigurationError, EvidenceLedgerError, ResourceCatalogError
from arguo.storage.cache import ResponseCache
from arguo.utilities.logging import setup_logging

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "catalog" / "catalog.json"
STATS_PATH = ROOT / "catalog" / "stats.json"
RESOURCES_DIR = ROOT / "data" / "resources"
OFFLINE_FIXTURE_PATH = ROOT / "tests" / "fixtures" / "offline_search.json"

app = typer.Typer(
    name="arguo",
    help="Arguo: research deeply, verify independently, show your evidence.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)
resources_app = typer.Typer(help="Search and validate the curated resource catalog.", no_args_is_help=True)
config_app = typer.Typer(help="Configuration checks.", no_args_is_help=True)
cache_app = typer.Typer(help="Cache management.", no_args_is_help=True)
eval_app = typer.Typer(help="Evaluation harness.", no_args_is_help=True)

app.add_typer(resources_app, name="resources")
app.add_typer(config_app, name="config")
app.add_typer(cache_app, name="cache")
app.add_typer(eval_app, name="eval")


def _fail(exc: EvidenceLedgerError) -> None:
    typer.echo(f"Error: {exc.user_message()}", err=True)
    raise typer.Exit(code=exc.exit_code)


def _load_catalog() -> list[dict]:
    if not CATALOG_PATH.is_file():
        raise ResourceCatalogError(
            f"Resource catalog not found at {CATALOG_PATH}.",
            hint="Run: python3 scripts/build_resource_catalog.py",
        )
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ResourceCatalogError(
            f"Resource catalog is unreadable: {exc}",
            hint="Rebuild with: python3 scripts/build_resource_catalog.py",
        ) from exc
    if not isinstance(data, list):
        raise ResourceCatalogError("Resource catalog must be a JSON array of records.")
    return data


def _catalog_validator():
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    return importlib.import_module("validate_catalog_file")


def _evals_runner():
    evals_dir = str(ROOT / "evals")
    for path in (evals_dir, str(ROOT)):
        if path not in sys.path:
            sys.path.insert(0, path)
    return importlib.import_module("run_evals")


# ---------------------------------------------------------------------------
# research
# ---------------------------------------------------------------------------


@app.command()
def research(
    question: Annotated[str, typer.Argument(help="The research question to investigate.")],
    profile: Annotated[str, typer.Option(help="Research profile name.")] = "standard",
    since: Annotated[
        datetime | None, typer.Option(formats=["%Y-%m-%d"], help="Restrict to sources published on or after this date.")
    ] = None,
    until: Annotated[
        datetime | None, typer.Option(formats=["%Y-%m-%d"], help="Restrict to sources published on or before this date.")
    ] = None,
    max_sources: Annotated[
        int | None, typer.Option("--max-sources", min=1, help="Cap on sources (cannot exceed the profile limit).")
    ] = None,
    offline: Annotated[bool, typer.Option("--offline", help="Run with fixture providers, no network.")] = False,
    output_dir: Annotated[
        str | None, typer.Option("--output-dir", help="Directory for run artifacts.")
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Print the manifest as JSON to stdout.")] = False,
) -> None:
    """Run the full research pipeline for one question."""
    import asyncio

    from arguo.orchestrator import ResearchOrchestrator

    setup_logging()
    try:
        if profile not in PROFILES:
            raise ConfigurationError(
                f"Unknown profile '{profile}'.",
                hint=f"Allowed profiles: {', '.join(sorted(PROFILES))}",
            )
        settings = Settings.from_env()
        orchestrator = ResearchOrchestrator(
            settings, PROFILES[profile], offline=offline
        )
        manifest = asyncio.run(
            orchestrator.run(
                question=question,
                since=since.date() if since else None,
                until=until.date() if until else None,
                max_sources=max_sources,
                output_dir=output_dir,
            )
        )
    except EvidenceLedgerError as exc:
        _fail(exc)
        return

    if json_output:
        typer.echo(manifest.model_dump_json(indent=2))
        return

    artifacts_dir = ""
    for stage in manifest.stages:
        if stage.stage == "J-reporting" and stage.details.get("artifacts_dir"):
            artifacts_dir = str(stage.details["artifacts_dir"])
    typer.echo(f"Research run complete: {manifest.run_id}")
    typer.echo(f"Profile: {manifest.profile} (offline: {manifest.offline_mode})")
    typer.echo("Stages:")
    for stage in manifest.stages:
        typer.echo(f"  {stage.stage}: {stage.status} ({stage.duration_ms} ms)")
    typer.echo(
        f"Sources: {manifest.sources_retrieved}, evidence: {manifest.evidence_records}, "
        f"rounds: {manifest.search_rounds_used}, model calls: {manifest.model_calls}"
    )
    if manifest.warnings:
        typer.echo("Warnings:")
        for warning in manifest.warnings:
            typer.echo(f"  - {warning}")
    if artifacts_dir:
        typer.echo(f"Artifacts: {artifacts_dir}")


# ---------------------------------------------------------------------------
# resources
# ---------------------------------------------------------------------------


@resources_app.command("search")
def resources_search(
    query: Annotated[str, typer.Argument(help="Case-insensitive substring to match.")],
    category: Annotated[str | None, typer.Option(help="Filter by catalog category key.")] = None,
    limit: Annotated[int, typer.Option(min=1, help="Maximum records to print.")] = 20,
) -> None:
    """Search the resource catalog by name, description, and tags."""
    try:
        records = _load_catalog()
    except ResourceCatalogError as exc:
        _fail(exc)
        return
    query_lower = query.lower()
    matches = []
    for record in records:
        if category and record.get("category") != category:
            continue
        haystack = " ".join(
            [
                str(record.get("name", "")),
                str(record.get("description", "")),
                " ".join(str(t) for t in record.get("tags", []) or []),
            ]
        ).lower()
        if query_lower in haystack:
            matches.append(record)
    typer.echo(f"{len(matches)} matching record(s)")
    for record in matches[: max(0, limit)]:
        typer.echo(
            f"  {record.get('id')}  {record.get('name')}  "
            f"({record.get('category')})  {record.get('canonical_url')}"
        )


@resources_app.command("list")
def resources_list(
    category: Annotated[str | None, typer.Option(help="Filter by catalog category key.")] = None,
    limit: Annotated[int, typer.Option(min=1, help="Maximum records to print.")] = 50,
) -> None:
    """List catalog records, optionally filtered by category."""
    try:
        records = _load_catalog()
    except ResourceCatalogError as exc:
        _fail(exc)
        return
    shown = 0
    for record in records:
        if category and record.get("category") != category:
            continue
        if shown >= limit:
            typer.echo("  ... (more records omitted, raise --limit to see them)")
            break
        typer.echo(
            f"  {record.get('id')}  {record.get('name')}  ({record.get('category')})"
        )
        shown += 1
    typer.echo(f"{shown} record(s) listed")


@resources_app.command("validate")
def resources_validate(
    file: Annotated[
        str | None, typer.Argument(help="Validate one JSONL file, or every file in data/resources when omitted.")
    ] = None,
) -> None:
    """Validate resource JSONL files with the catalog schema rules."""
    validator = _catalog_validator()
    paths = []
    if file:
        paths.append(Path(file))
    else:
        if not RESOURCES_DIR.is_dir():
            typer.echo(f"Error: resources directory not found: {RESOURCES_DIR}", err=True)
            raise typer.Exit(code=1)
        paths = sorted(RESOURCES_DIR.glob("*.jsonl"))
    if not paths:
        typer.echo("No JSONL files found to validate.")
        raise typer.Exit(code=1)
    failed = False
    total = 0
    for path in paths:
        count, categories, errors = validator.validate_file(path)
        total += count
        status = "PASS" if not errors else f"FAIL ({len(errors)} error(s))"
        typer.echo(f"{path.name}: {count} records: {status}")
        if errors:
            failed = True
            for error in errors[:10]:
                typer.echo(f"  - {error}", err=True)
    typer.echo(f"Validated {len(paths)} file(s), {total} record(s).")
    raise typer.Exit(code=1 if failed else 0)


@resources_app.command("stats")
def resources_stats() -> None:
    """Show catalog record, category, region, and verification counts."""
    try:
        records = _load_catalog()
    except ResourceCatalogError as exc:
        _fail(exc)
        return
    if STATS_PATH.is_file():
        try:
            stats = json.loads(STATS_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            stats = None
        if isinstance(stats, dict):
            typer.echo(f"Records: {stats.get('total_records', len(records))}")
            typer.echo(f"Categories: {stats.get('category_count', 'unknown')}")
            regions = stats.get("regions", {})
            top_regions = list(regions.items())[:5]
            if top_regions:
                typer.echo("Top regions: " + ", ".join(f"{k} ({v})" for k, v in top_regions))
            statuses = stats.get("verification_status", {})
            typer.echo(
                "Verification status: "
                + ", ".join(f"{k}: {v}" for k, v in sorted(statuses.items()))
            )
            return
    categories = sorted({str(r.get("category")) for r in records})
    regions: dict[str, int] = {}
    statuses: dict[str, int] = {}
    for record in records:
        region = str(record.get("region", "unknown"))
        regions[region] = regions.get(region, 0) + 1
        status = str(record.get("verification_status", "unknown"))
        statuses[status] = statuses.get(status, 0) + 1
    typer.echo(f"Records: {len(records)}")
    typer.echo(f"Categories: {len(categories)}")
    top_regions = sorted(regions.items(), key=lambda kv: -kv[1])[:5]
    if top_regions:
        typer.echo("Top regions: " + ", ".join(f"{k} ({v})" for k, v in top_regions))
    typer.echo(
        "Verification status: " + ", ".join(f"{k}: {v}" for k, v in sorted(statuses.items()))
    )


# ---------------------------------------------------------------------------
# config check
# ---------------------------------------------------------------------------


@config_app.command("check")
def config_check() -> None:
    """Validate configuration resolved from the environment; never prints secrets."""
    try:
        settings = Settings.from_env()
    except EvidenceLedgerError as exc:
        _fail(exc)
        return
    typer.echo(f"Search provider: {settings.search_provider}")
    typer.echo(f"TAVILY_API_KEY set: {bool(settings.tavily_api_key)}")
    typer.echo(f"Model provider: {settings.model_provider}")
    typer.echo(f"Model base URL set: {bool(settings.model_base_url)}")
    typer.echo(f"Model name set: {bool(settings.model_name)}")
    typer.echo(f"Model API key set: {bool(settings.model_api_key)}")
    typer.echo(f"Profile: {settings.profile}")
    typer.echo(f"Output directory: {settings.output_dir}")
    typer.echo(f"Cache directory: {settings.cache_dir}")
    offline_ready = OFFLINE_FIXTURE_PATH.is_file()
    typer.echo(
        "Offline search fixtures: "
        + ("file present" if offline_ready else "built-in defaults will be used")
    )


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------


@app.command()
def doctor(
    ping: Annotated[bool, typer.Option("--ping", help="Also attempt a live network check.")] = False,
) -> None:
    """Check the installation: python, settings, catalog, cache, offline readiness."""
    import httpx

    failures = 0
    results: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str) -> None:
        nonlocal failures
        if not ok:
            failures += 1
        results.append((name, ok, detail))

    version_ok = sys.version_info >= (3, 11)
    check(
        "python",
        version_ok,
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        + ("" if version_ok else " (3.11+ required)"),
    )
    try:
        settings = Settings.from_env()
        check("settings", True, f"profile '{settings.profile}' loaded")
    except EvidenceLedgerError as exc:
        settings = None
        check("settings", False, exc.user_message().replace("\n", " "))
    if settings is not None:
        check(
            "search-provider-key",
            True,
            "TAVILY_API_KEY present" if settings.tavily_api_key else "TAVILY_API_KEY absent (offline mode still works)",
        )
        model_ready = bool(settings.model_base_url and settings.model_name)
        check(
            "model-config",
            True,
            "model endpoint configured"
            if model_ready
            else "model endpoint not configured (heuristic mode)",
        )
        try:
            cache = ResponseCache(settings.cache_dir, settings.cache_ttl_s)
            probe = cache.dir / "doctor-probe.tmp"
            cache.dir.mkdir(parents=True, exist_ok=True)
            probe.write_text("probe", encoding="utf-8")
            probe.unlink()
            check("cache-dir", True, f"{cache.dir} is writable")
        except OSError as exc:
            check("cache-dir", False, f"not writable: {exc}")
    if CATALOG_PATH.is_file():
        try:
            records = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            categories = {str(r.get("category")) for r in records if isinstance(r, dict)}
            check("catalog", True, f"{len(records)} records across {len(categories)} categories")
        except (OSError, ValueError) as exc:
            check("catalog", False, f"unreadable: {exc}")
    else:
        check(
            "catalog",
            False,
            f"missing at {CATALOG_PATH}; run: python3 scripts/build_resource_catalog.py",
        )
    if OFFLINE_FIXTURE_PATH.is_file():
        check("offline-mode", True, f"fixture file present: {OFFLINE_FIXTURE_PATH.name}")
    else:
        check("offline-mode", True, "built-in default fixtures will be used")
    if ping:
        try:
            response = httpx.get("https://example.org", timeout=5.0)
            check("ping", response.status_code < 500, f"example.org returned HTTP {response.status_code}")
        except httpx.HTTPError as exc:
            check("ping", False, f"network check failed: {type(exc).__name__}")

    for name, ok, detail in results:
        marker = "ok  " if ok else "FAIL"
        typer.echo(f"[{marker}] {name}: {detail}")
    if failures:
        typer.echo(f"Doctor found {failures} failing check(s).")
        raise typer.Exit(code=1)
    typer.echo("Doctor: all checks passed.")


# ---------------------------------------------------------------------------
# cache clear
# ---------------------------------------------------------------------------


@cache_app.command("clear")
def cache_clear() -> None:
    """Delete every entry in the response cache directory."""
    try:
        settings = Settings.from_env()
    except EvidenceLedgerError as exc:
        _fail(exc)
        return
    cache = ResponseCache(settings.cache_dir, settings.cache_ttl_s)
    removed = cache.clear()
    typer.echo(f"Cleared {removed} cache entr(y/ies) from {cache.dir}")


# ---------------------------------------------------------------------------
# eval run
# ---------------------------------------------------------------------------


@eval_app.command("run")
def eval_run(
    offline: Annotated[bool, typer.Option("--offline/--live", help="Offline uses fixture providers.")] = True,
    cases_dir: Annotated[str, typer.Option(help="Directory containing eval case JSON files.")] = "evals/cases",
    output_dir: Annotated[str | None, typer.Option(help="Directory for the eval report.")] = None,
    limit: Annotated[int | None, typer.Option("--limit", min=1, help="Only run the first N cases.")] = None,
) -> None:
    """Run the structural evaluation harness over evals/cases."""
    setup_logging()
    runner = _evals_runner()
    try:
        report_path = runner.run_evals(
            cases_dir=cases_dir, offline=offline, limit=limit, output_dir=output_dir
        )
    except EvidenceLedgerError as exc:
        _fail(exc)
        return
    typer.echo(f"Eval report written: {report_path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
