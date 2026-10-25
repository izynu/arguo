#!/usr/bin/env python3
"""Structural evaluation harness for Arguo research runs.

Loads case files from evals/cases/*.json, runs the orchestrator for each
case (offline by default, using per-case fixtures when provided), and
records structural metrics only:

- citation validity: the audit found zero errors for the case
- unsupported-claim rate: claims without linked evidence, over all claims
- source diversity: count of distinct source domains
- search rounds used and wall-clock runtime

The metrics measure pipeline structure, not factual accuracy. Every report
this script writes says so explicitly; no quality scores are fabricated.

Usage:
    python3 evals/run_evals.py --offline [--limit N] [--cases-dir DIR]
    python3 evals/run_evals.py --live   (requires TAVILY_API_KEY and model env)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

_REPO_ROOT = Path(__file__).resolve().parents[1]
_PYTHON_DIR = _REPO_ROOT / "python"
for _path in (str(_PYTHON_DIR),):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from arguo.config import PROFILES, Settings  # noqa: E402
from arguo.exceptions import ConfigurationError, EvidenceLedgerError  # noqa: E402
from arguo.orchestrator import ResearchOrchestrator  # noqa: E402
from arguo.utilities.logging import setup_logging  # noqa: E402

METRICS_NOTE = (
    "Metrics are structural only (citation consistency, claim support "
    "linkage, source diversity, rounds, runtime). They do not measure the "
    "factual accuracy of report content."
)

_REQUIRED_CASE_FIELDS = ("id", "question", "category", "objective", "expected_behavior")


def load_cases(cases_dir: str | Path) -> list[dict]:
    """Load and validate all case files; raise ConfigurationError on bad input."""
    directory = Path(cases_dir)
    if not directory.is_dir():
        raise ConfigurationError(
            f"Eval cases directory not found: {directory}",
            hint="Pass --cases-dir pointing at a directory of case JSON files.",
        )
    cases: list[dict] = []
    seen_ids: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConfigurationError(f"Case file {path.name} is unreadable: {exc}") from exc
        items = data.get("cases") if isinstance(data, dict) else None
        if not isinstance(items, list):
            raise ConfigurationError(
                f"Case file {path.name} must be an object with a 'cases' array."
            )
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise ConfigurationError(
                    f"Case file {path.name}, case {index}: case must be an object."
                )
            missing = [field for field in _REQUIRED_CASE_FIELDS if not item.get(field)]
            if missing:
                raise ConfigurationError(
                    f"Case file {path.name}, case {index}: missing fields "
                    f"{', '.join(missing)}."
                )
            case_id = str(item["id"])
            if case_id in seen_ids:
                raise ConfigurationError(f"Duplicate case id '{case_id}' in {path.name}.")
            seen_ids.add(case_id)
            case = dict(item)
            case["_source_file"] = path.name
            fixtures = case.get("fixtures")
            if fixtures is not None and not isinstance(fixtures, dict):
                raise ConfigurationError(
                    f"Case {case_id}: 'fixtures' must be an object mapping "
                    "query substrings to result lists."
                )
            cases.append(case)
    if not cases:
        raise ConfigurationError(
            f"No eval cases found in {directory}",
            hint="Add case JSON files with a 'cases' array.",
        )
    return cases


def _distinct_domains(urls: list[str]) -> int:
    hosts = set()
    for url in urls:
        host = (urlparse(url).hostname or "").lower().rstrip(".")
        if host:
            hosts.add(host)
    return len(hosts)


def run_case(
    case: dict,
    offline: bool,
    artifacts_root: Path,
    profile_name: str = "quick",
) -> dict:
    """Run one case end to end and compute its structural metrics."""
    settings = Settings.from_env(env={} if offline else None)
    profile = PROFILES[profile_name]
    fixtures = case.get("fixtures") or None
    if fixtures is not None:
        fixtures = {str(key).lower(): value for key, value in fixtures.items()}
    case_dir = artifacts_root / str(case["id"])
    orchestrator = ResearchOrchestrator(
        settings, profile, offline=offline, search_fixtures=fixtures
    )
    started = time.monotonic()
    manifest = asyncio.run(
        orchestrator.run(case["question"], output_dir=case_dir)
    )
    runtime_s = round(time.monotonic() - started, 3)

    audit: dict = {}
    sources: list[dict] = []
    claims: list[dict] = []
    try:
        audit = json.loads((case_dir / "audit.json").read_text(encoding="utf-8"))
        sources = json.loads((case_dir / "sources.json").read_text(encoding="utf-8")).get("sources", [])
        claims = json.loads((case_dir / "evidence.json").read_text(encoding="utf-8")).get("claims", [])
    except (OSError, ValueError) as exc:
        return {
            "id": case["id"],
            "status": "artifact-error",
            "error": f"could not read artifacts: {exc}",
        }

    error_count = sum(1 for issue in audit.get("issues", []) if issue.get("severity") == "error")
    unsupported = sum(1 for claim in claims if not claim.get("evidence_ids"))
    urls = [str(source.get("url", "")) for source in sources]
    stage_statuses = {stage.stage: stage.status for stage in manifest.stages}

    return {
        "id": case["id"],
        "question": case["question"],
        "category": case["category"],
        "objective": case["objective"],
        "expected_behavior": case["expected_behavior"],
        "source_file": case.get("_source_file"),
        "fixtures_used": bool(fixtures),
        "run_id": manifest.run_id,
        "offline": manifest.offline_mode,
        "stage_statuses": stage_statuses,
        "metrics": {
            "citation_valid": error_count == 0,
            "audit_error_count": error_count,
            "audit_warning_count": sum(
                1 for issue in audit.get("issues", []) if issue.get("severity") == "warning"
            ),
            "unsupported_claim_rate": round(unsupported / len(claims), 4) if claims else None,
            "claims": len(claims),
            "sources": len(sources),
            "evidence": manifest.evidence_records,
            "source_diversity_domains": _distinct_domains(urls),
            "rounds_used": manifest.search_rounds_used,
            "model_calls": manifest.model_calls,
            "runtime_s": runtime_s,
        },
        "artifacts_dir": str(case_dir),
        "notes": case.get("notes"),
    }


def run_evals(
    cases_dir: str | Path = "evals/cases",
    offline: bool = True,
    limit: int | None = None,
    output_dir: str | Path | None = None,
    profile_name: str = "quick",
) -> Path:
    """Run all cases and write a timestamped report. Returns the report path."""
    setup_logging()
    if not offline:
        settings = Settings.from_env()
        settings.validate_for_research(False)
    cases = load_cases(cases_dir)
    if limit is not None:
        cases = cases[: max(0, int(limit))]
    if not cases:
        raise ConfigurationError("--limit produced an empty case list.")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    base = Path(output_dir) if output_dir else _REPO_ROOT / "evals" / "reports"
    artifacts_root = base / f"run-{timestamp}" / "artifacts"
    report_path = base / f"run-{timestamp}.json"
    artifacts_root.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for case in cases:
        try:
            results.append(run_case(case, offline, artifacts_root, profile_name))
        except EvidenceLedgerError as exc:
            results.append(
                {
                    "id": case["id"],
                    "status": "error",
                    "error": exc.user_message(),
                }
            )

    valid = sum(1 for r in results if r.get("metrics", {}).get("citation_valid"))
    unsupported_rates = [
        r["metrics"]["unsupported_claim_rate"]
        for r in results
        if r.get("metrics", {}).get("unsupported_claim_rate") is not None
    ]
    runtimes = [r["metrics"]["runtime_s"] for r in results if r.get("metrics")]
    summary = {
        "total_cases": len(results),
        "citation_valid_cases": valid,
        "cases_with_audit_errors": len(results) - valid,
        "mean_unsupported_claim_rate": (
            round(sum(unsupported_rates) / len(unsupported_rates), 4)
            if unsupported_rates
            else None
        ),
        "total_runtime_s": round(sum(runtimes), 3) if runtimes else 0.0,
        "profile": profile_name,
        "mode": "offline" if offline else "live",
    }
    report = {
        "generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "metrics_note": METRICS_NOTE,
        "summary": summary,
        "cases": results,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Structural evals for Arguo.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", dest="offline", action="store_true", default=True,
                      help="Run with fixture providers (default).")
    mode.add_argument("--live", dest="offline", action="store_false",
                      help="Run with live providers; requires API keys in the environment.")
    parser.add_argument("--cases-dir", default="evals/cases")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--limit", type=int, default=None, help="Only run the first N cases.")
    parser.add_argument("--profile", default="quick", choices=sorted(PROFILES))
    args = parser.parse_args(argv)

    try:
        report_path = run_evals(
            cases_dir=args.cases_dir,
            offline=args.offline,
            limit=args.limit,
            output_dir=args.output_dir,
            profile_name=args.profile,
        )
    except ConfigurationError as exc:
        print(f"Error: {exc.user_message()}", file=sys.stderr)
        return exc.exit_code
    print(f"Eval report written: {report_path}")
    try:
        report = json.loads(Path(report_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 1
    summary = report.get("summary", {})
    print(
        f"Cases: {summary.get('total_cases')}, citation-valid: "
        f"{summary.get('citation_valid_cases')}, with audit errors: "
        f"{summary.get('cases_with_audit_errors')}, runtime: "
        f"{summary.get('total_runtime_s')}s"
    )
    print(f"Mode: {summary.get('mode')} (profile {summary.get('profile')})")
    print(METRICS_NOTE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
