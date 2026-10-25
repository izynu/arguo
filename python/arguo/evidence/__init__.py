"""Evidence: the ledger store and the collection pipeline that feeds it."""

from arguo.evidence.collector import collect, split_passages
from arguo.evidence.ledger import EvidenceLedger

__all__ = ["EvidenceLedger", "collect", "split_passages"]
