"""Search support: provider-neutral deduplication and offline fixture provider."""

from arguo.search.dedupe import dedupe_results
from arguo.search.offline import OfflineSearchProvider

__all__ = ["dedupe_results", "OfflineSearchProvider"]
