"""Retrieval: bounded, SSRF-guarded page fetching (plus offline fixtures)."""

from arguo.retrieval.fetcher import Fetcher, FetchResult
from arguo.retrieval.offline_fetcher import OfflineFetcher

__all__ = ["Fetcher", "FetchResult", "OfflineFetcher"]
