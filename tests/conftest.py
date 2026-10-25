"""Shared fixtures for the Arguo test suite.

The sample ledger keeps everything in one place: two sources on different
registrable domains (example.org and example.net), three evidence passages,
and two claims linked with ledger.link. C1 draws on two passages from the two
different domains, C2 draws on one passage. The passages are written so the
numeric contradiction scan finds no conflict inside the shared fixture; the
dedicated contradiction tests build their own conflicting numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arguo.config import PROFILES
from arguo.evidence.ledger import EvidenceLedger
from arguo.models import Relevance, SourceType
from arguo.planning.heuristic import heuristic_plan

QUESTION = (
    "Does urban tree cover reduce summer heat in cities according to "
    "climate records?"
)


@pytest.fixture
def ledger() -> EvidenceLedger:
    """Ledger with S1/S2 (example.org, example.net), E1/E2/E3, C1/C2.

    C1 links E1 (example.org) and E2 (example.net), so its corroboration
    spans two independent domains. C2 links E3 (example.org) only.
    """
    ledger = EvidenceLedger()
    s1 = ledger.add_source(
        url="https://example.org/tree-cover",
        title="Example fixture: urban tree canopy data",
        publisher="Example fixture publisher",
        published_at="2024-05-01",
        source_type=SourceType.PRIMARY,
        snippets=["Tree canopy covered 22 percent of the study area."],
    )
    s2 = ledger.add_source(
        url="https://example.net/urban-heat",
        title="Example fixture: city heat measurements",
        publisher="Example fixture publisher two",
        published_at=None,
        source_type=SourceType.SECONDARY,
        snippets=["Measurements show a cooling effect near parks."],
    )
    ledger.add_evidence(
        source_id=s1.source_id,
        source_url=s1.url,
        relevant_passage=(
            "Tree canopy covered 22 percent of the study area according to "
            "the demonstration dataset."
        ),
        source_title=s1.title,
        published_at=s1.published_at,
        relevance=Relevance.DIRECT,
        provenance={"subquestion_id": "SQ1", "token_overlap": 0.4},
    )
    ledger.add_evidence(
        source_id=s2.source_id,
        source_url=s2.url,
        relevant_passage=(
            "Measurements show a cooling effect near parks in the "
            "demonstration dataset."
        ),
        published_at=None,
        relevance=Relevance.DIRECT,
        provenance={"subquestion_id": "SQ1", "token_overlap": 0.3},
    )
    ledger.add_evidence(
        source_id=s1.source_id,
        source_url=s1.url,
        relevant_passage=(
            "The same demonstration dataset measured a stronger cooling "
            "effect in one district."
        ),
        published_at="2024-05-01",
        relevance=Relevance.DIRECT,
        provenance={"subquestion_id": "SQ2", "token_overlap": 0.2},
    )
    c1 = ledger.add_claim(
        text=(
            "Tree canopy covered 22 percent of the study area according to "
            "the demonstration dataset."
        )
    )
    c2 = ledger.add_claim(text="The cooling effect near parks is measurable.")
    ledger.link(c1.claim_id, "E1")
    ledger.link(c1.claim_id, "E2")
    ledger.link(c2.claim_id, "E3")
    return ledger


@pytest.fixture
def plan():
    """Deterministic heuristic plan for the fixed question (standard profile)."""
    return heuristic_plan(QUESTION, PROFILES["standard"])


@pytest.fixture
def tmp_catalog(tmp_path: Path) -> Path:
    """Write a tiny three-record catalog to tmp_path/catalog/catalog.json."""
    records = [
        {
            "id": "example-stats-office",
            "name": "Example Stats Office",
            "category": "government-statistics",
            "canonical_url": "https://example.org/stats",
            "region": "global",
            "verification_status": "documented",
            "description": "A demonstration statistics source for tests only.",
            "tags": ["demo", "statistics"],
        },
        {
            "id": "example-archive",
            "name": "Example Archive",
            "category": "history-archives",
            "canonical_url": "https://example.net/archive",
            "region": "global",
            "verification_status": "documented",
            "description": "A demonstration archive source for tests only.",
            "tags": ["demo", "history"],
        },
        {
            "id": "example-preprint-server",
            "name": "Example Preprint Server",
            "category": "preprints",
            "canonical_url": "https://example.org/preprints",
            "region": "global",
            "verification_status": "documented",
            "description": "A demonstration preprint source for tests only.",
            "tags": ["demo", "academic"],
        },
    ]
    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    path = catalog_dir / "catalog.json"
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return path
