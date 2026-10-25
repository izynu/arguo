"""The evidence ledger: the run-scoped store of sources, evidence, and claims.

The ledger assigns sequential ids (S1, E1, C1), enforces referential integrity
on links, and computes corroboration groups that separate genuinely
independent domains from probable syndication. Serialization preserves
explicit nulls so "unknown" never silently becomes "missing".
"""

from __future__ import annotations

import json
import re
from typing import Any

from arguo.exceptions import InvalidSourceError
from arguo.models import (
    ClaimRecord,
    EvidenceRecord,
    Relevance,
    SourceRecord,
    SourceType,
    SupportRelation,
    utc_now_iso,
)
from arguo.utilities.logging import get_logger
from arguo.utilities.text import token_overlap
from arguo.utilities.urls import get_registrable_domain

logger = get_logger("arguo.evidence.ledger")

_ID_RE = re.compile(r"^[A-Za-z]+(\d+)$")
_JACCARD_SYNDICATION_THRESHOLD = 0.85
_SYNDICATION_NOTE = "possible syndication or shared upstream source"


def _id_number(record_id: str) -> int:
    match = _ID_RE.match(record_id or "")
    return int(match.group(1)) if match else 0


class EvidenceLedger:
    """In-memory evidence store for one research run.

    All ids are assigned sequentially per ledger instance, so a fresh ledger
    starts at S1, E1, C1 regardless of any other instance.
    """

    def __init__(self) -> None:
        self._sources: list[SourceRecord] = []
        self._evidence: list[EvidenceRecord] = []
        self._claims: list[ClaimRecord] = []
        self._source_index: dict[str, SourceRecord] = {}
        self._evidence_index: dict[str, EvidenceRecord] = {}
        self._claim_index: dict[str, ClaimRecord] = {}
        self._source_n = 0
        self._evidence_n = 0
        self._claim_n = 0

    # ------------------------------------------------------------------
    # Record creation
    # ------------------------------------------------------------------

    def add_source(
        self,
        url: str,
        *,
        title: str | None = None,
        final_url: str | None = None,
        publisher: str | None = None,
        author: str | None = None,
        source_type: SourceType = SourceType.UNKNOWN,
        published_at: str | None = None,
        updated_at: str | None = None,
        event_or_observation_date: str | None = None,
        retrieved_at: str | None = None,
        content_type: str | None = None,
        content_hash: str | None = None,
        license: str | None = None,
        provider: str | None = None,
        snippets: list[str] | None = None,
        access_note: str | None = None,
        domains_seen_in: list[str] | None = None,
    ) -> SourceRecord:
        """Register a source and return it with an auto-assigned S{n} id."""
        self._source_n += 1
        record = SourceRecord(
            source_id=f"S{self._source_n}",
            url=url,
            final_url=final_url,
            title=title,
            publisher=publisher,
            author=author,
            source_type=source_type,
            published_at=published_at,
            updated_at=updated_at,
            event_or_observation_date=event_or_observation_date,
            retrieved_at=retrieved_at or utc_now_iso(),
            content_type=content_type,
            content_hash=content_hash,
            license=license,
            provider=provider,
            snippets=list(snippets) if snippets else [],
            access_note=access_note,
            domains_seen_in=list(domains_seen_in) if domains_seen_in else [],
        )
        self._sources.append(record)
        self._source_index[record.source_id] = record
        return record

    def add_evidence(
        self,
        source_id: str,
        source_url: str,
        relevant_passage: str,
        *,
        claim_ids: list[str] | None = None,
        source_title: str | None = None,
        passage_locator: str | None = None,
        source_type: SourceType = SourceType.UNKNOWN,
        author_or_publisher: str | None = None,
        published_at: str | None = None,
        updated_at: str | None = None,
        event_or_observation_date: str | None = None,
        retrieved_at: str | None = None,
        supports_or_contradicts: SupportRelation = SupportRelation.SUPPORTS,
        relevance: Relevance = Relevance.DIRECT,
        methodology_notes: str | None = None,
        independence_group: str | None = None,
        limitations: list[str] | None = None,
        content_hash: str | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> EvidenceRecord:
        """Register an evidentiary passage; the source_id must already exist."""
        if source_id not in self._source_index:
            raise InvalidSourceError(
                f"Cannot add evidence: source '{source_id}' is not in the ledger.",
                hint="Add the source with add_source() before adding evidence for it.",
            )
        self._evidence_n += 1
        record = EvidenceRecord(
            evidence_id=f"E{self._evidence_n}",
            claim_ids=list(claim_ids) if claim_ids else [],
            source_id=source_id,
            source_url=source_url,
            source_title=source_title,
            relevant_passage=relevant_passage,
            passage_locator=passage_locator,
            source_type=source_type,
            author_or_publisher=author_or_publisher,
            published_at=published_at,
            updated_at=updated_at,
            event_or_observation_date=event_or_observation_date,
            retrieved_at=retrieved_at or utc_now_iso(),
            supports_or_contradicts=supports_or_contradicts,
            relevance=relevance,
            methodology_notes=methodology_notes,
            independence_group=independence_group,
            limitations=list(limitations) if limitations else [],
            content_hash=content_hash,
            provenance=dict(provenance) if provenance else {},
        )
        self._evidence.append(record)
        self._evidence_index[record.evidence_id] = record
        return record

    def add_claim(
        self,
        text: str,
        *,
        subquestion_id: str | None = None,
        claim_kind: str = "unknown",
        evidence_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        notes: str | None = None,
    ) -> ClaimRecord:
        """Register a claim and return it with an auto-assigned C{n} id."""
        self._claim_n += 1
        record = ClaimRecord(
            claim_id=f"C{self._claim_n}",
            text=text,
            evidence_ids=list(evidence_ids) if evidence_ids else [],
            source_ids=list(source_ids) if source_ids else [],
            subquestion_id=subquestion_id,
            claim_kind=claim_kind,  # type: ignore[arg-type]
            notes=notes,
        )
        self._claims.append(record)
        self._claim_index[record.claim_id] = record
        return record

    # ------------------------------------------------------------------
    # Linking
    # ------------------------------------------------------------------

    def link(self, claim_id: str, evidence_id: str) -> None:
        """Link a claim and an evidence record in both directions.

        Raises InvalidSourceError when either id is unknown. Linking twice is
        a no-op rather than a duplicate.
        """
        claim = self._claim_index.get(claim_id)
        evidence = self._evidence_index.get(evidence_id)
        if claim is None:
            raise InvalidSourceError(f"Cannot link: claim '{claim_id}' does not exist.")
        if evidence is None:
            raise InvalidSourceError(f"Cannot link: evidence '{evidence_id}' does not exist.")
        if evidence_id not in claim.evidence_ids:
            claim.evidence_ids.append(evidence_id)
        if claim_id not in evidence.claim_ids:
            evidence.claim_ids.append(claim_id)
        if evidence.source_id and evidence.source_id not in claim.source_ids:
            claim.source_ids.append(evidence.source_id)

    # ------------------------------------------------------------------
    # Views
    # ------------------------------------------------------------------

    def sources(self) -> list[SourceRecord]:
        """Return the source records in insertion order (defensive copy)."""
        return list(self._sources)

    def evidence(self) -> list[EvidenceRecord]:
        """Return the evidence records in insertion order (defensive copy)."""
        return list(self._evidence)

    def claims(self) -> list[ClaimRecord]:
        """Return the claim records in insertion order (defensive copy)."""
        return list(self._claims)

    def get_source(self, source_id: str) -> SourceRecord | None:
        return self._source_index.get(source_id)

    def get_evidence(self, evidence_id: str) -> EvidenceRecord | None:
        return self._evidence_index.get(evidence_id)

    def get_claim(self, claim_id: str) -> ClaimRecord | None:
        return self._claim_index.get(claim_id)

    def sources_by_domain(self) -> dict[str, list[SourceRecord]]:
        """Group sources by registrable domain of their URL.

        Sources whose URL has no computable registrable domain are grouped
        under the empty string so nothing disappears silently.
        """
        grouped: dict[str, list[SourceRecord]] = {}
        for source in self._sources:
            try:
                domain = get_registrable_domain(source.url)
            except ValueError:
                domain = ""
            grouped.setdefault(domain, []).append(source)
        return grouped

    def known_source_urls(self) -> set[str]:
        """Return the set of exact source URLs already in the ledger."""
        return {source.url for source in self._sources}

    # ------------------------------------------------------------------
    # Corroboration analysis
    # ------------------------------------------------------------------

    def corroboration_groups(self) -> dict[str, dict[str, Any]]:
        """Compute per-claim corroboration: independent domains and syndication.

        For every claim the returned dict carries:
        - claim_id and text
        - evidence_ids considered
        - independent_domains: distinct independence groups (registrable
          domains) among the supporting evidence
        - distinct_independent_domains: the count of those
        - syndication_suspected: True when two or more passages share token
          Jaccard >= 0.85
        - syndication_groups: lists of evidence ids grouped as probable
          syndication; those evidence records get an explicit limitation note
          and a shared syndication independence group.

        Suspected syndication is recorded, never deleted: passages stay in
        the ledger with their limitation visible to the report stage.
        """
        results: dict[str, dict[str, Any]] = {}
        for claim in self._claims:
            records = [
                self._evidence_index[eid]
                for eid in claim.evidence_ids
                if eid in self._evidence_index
            ]
            initial_groups: list[str | None] = []
            for record in records:
                if record.independence_group:
                    initial_groups.append(record.independence_group)
                    continue
                try:
                    initial_groups.append(get_registrable_domain(record.source_url))
                except ValueError:
                    initial_groups.append(None)
            independent_domains = sorted({g for g in initial_groups if g})

            clusters = self._syndication_clusters(records)
            syndication_groups: list[list[str]] = []
            for cluster in clusters:
                if len(cluster) < 2:
                    continue
                member_ids = sorted(r.evidence_id for r in cluster)
                syndication_groups.append(member_ids)
                shared_group = f"syndication:{member_ids[0]}"
                for record in cluster:
                    if _SYNDICATION_NOTE not in record.limitations:
                        record.limitations.append(_SYNDICATION_NOTE)
                    record.independence_group = shared_group
                cluster_ids = {r.evidence_id for r in cluster}
                # A domain only counts as independent corroboration when some
                # evidence from it sits outside the suspected syndication set.
                for domain in self._cluster_domains(cluster):
                    has_outside_member = any(
                        record.evidence_id not in cluster_ids
                        and initial_groups[i] == domain
                        for i, record in enumerate(records)
                    )
                    if not has_outside_member and domain in independent_domains:
                        independent_domains.remove(domain)

            results[claim.claim_id] = {
                "claim_id": claim.claim_id,
                "text": claim.text,
                "evidence_ids": list(claim.evidence_ids),
                "independent_domains": independent_domains,
                "distinct_independent_domains": len(independent_domains),
                "syndication_suspected": bool(syndication_groups),
                "syndication_groups": syndication_groups,
            }
        return results

    @staticmethod
    def _cluster_domains(cluster: list[EvidenceRecord]) -> set[str]:
        domains: set[str] = set()
        for record in cluster:
            try:
                domains.add(get_registrable_domain(record.source_url))
            except ValueError:
                continue
        return domains

    @staticmethod
    def _syndication_clusters(records: list[EvidenceRecord]) -> list[list[EvidenceRecord]]:
        """Cluster records whose passages share token Jaccard >= 0.85."""
        n = len(records)
        parent = list(range(n))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def union(i: int, j: int) -> None:
            parent[find(i)] = find(j)

        for i in range(n):
            for j in range(i + 1, n):
                score = token_overlap(records[i].relevant_passage, records[j].relevant_passage)
                if score >= _JACCARD_SYNDICATION_THRESHOLD:
                    union(i, j)

        clusters: dict[int, list[EvidenceRecord]] = {}
        for i in range(n):
            clusters.setdefault(find(i), []).append(records[i])
        return list(clusters.values())

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, list[dict[str, Any]]]:
        """Return {"sources", "evidence", "claims"} as plain dicts with nulls kept."""
        return {
            "sources": [s.model_dump() for s in self._sources],
            "evidence": [e.model_dump() for e in self._evidence],
            "claims": [c.model_dump() for c in self._claims],
        }

    def to_json(self) -> str:
        """Serialize the ledger to JSON with sorted keys and explicit nulls."""
        return json.dumps(self.to_dict(), sort_keys=True, indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EvidenceLedger:
        """Rebuild a ledger from to_dict output, restoring id counters."""
        ledger = cls()
        for source_data in data.get("sources", []):
            record = SourceRecord.model_validate(source_data)
            ledger._sources.append(record)
            ledger._source_index[record.source_id] = record
        for evidence_data in data.get("evidence", []):
            record = EvidenceRecord.model_validate(evidence_data)
            ledger._evidence.append(record)
            ledger._evidence_index[record.evidence_id] = record
        for claim_data in data.get("claims", []):
            record = ClaimRecord.model_validate(claim_data)
            ledger._claims.append(record)
            ledger._claim_index[record.claim_id] = record
        ledger._source_n = max((_id_number(s.source_id) for s in ledger._sources), default=0)
        ledger._evidence_n = max((_id_number(e.evidence_id) for e in ledger._evidence), default=0)
        ledger._claim_n = max((_id_number(c.claim_id) for c in ledger._claims), default=0)
        return ledger
