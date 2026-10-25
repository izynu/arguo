"""Provider contracts: search providers and model adapters.

Contract for every provider and adapter in this package:

- Construction must be free of network activity. Clients, connections, and
  credentials are only used inside async methods.
- Async methods must be safe to call under asyncio.run.
- Failures raise the typed exceptions from arguo.exceptions, never
  bare Exception or provider SDK types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from arguo.exceptions import ModelOutputError
from arguo.models import NormalizedResult


class SearchProvider(ABC):
    """A provider that turns a query into normalized web results."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable provider identifier used in provenance records."""

    @abstractmethod
    async def search(self, query: str, max_results: int) -> list[NormalizedResult]:
        """Run one search and return at most max_results normalized items."""

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return f"{type(self).__name__}(name={self.name!r})"


class ModelAdapter(ABC):
    """A chat-completion style model behind a strict, typed interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable adapter identifier used in run manifests."""

    @abstractmethod
    async def complete_json(
        self,
        prompt: str,
        schema_hint: str,
        system: str | None = None,
    ) -> dict:
        """Return the model answer parsed as a JSON object.

        schema_hint describes the expected JSON shape so the adapter can ask
        the model for a conforming object. Implementations must raise
        ModelOutputError when no valid JSON object can be recovered.
        """

    @abstractmethod
    async def complete_text(self, prompt: str, system: str | None = None) -> str:
        """Return the model answer as plain text."""

    def __repr__(self) -> str:  # pragma: no cover - diagnostic only
        return f"{type(self).__name__}(name={self.name!r})"


class NullModelAdapter(ModelAdapter):
    """Placeholder adapter for offline and heuristic runs.

    Constructing it performs no network activity. Calling it fails loudly so
    that a run configured without a model never silently produces model-made
    claims: the pipeline falls back to heuristic implementations instead.
    """

    @property
    def name(self) -> str:
        return "null"

    async def complete_json(
        self,
        prompt: str,
        schema_hint: str,
        system: str | None = None,
    ) -> dict:
        raise ModelOutputError(
            "No model adapter is configured: offline or heuristic mode is active.",
            hint=(
                "Set ARGUO_MODEL_BASE_URL, ARGUO_MODEL_NAME, and "
                "ARGUO_MODEL_API_KEY to enable model calls, or keep "
                "offline mode and accept heuristic planning and review."
            ),
        )

    async def complete_text(self, prompt: str, system: str | None = None) -> str:
        raise ModelOutputError(
            "No model adapter is configured: offline or heuristic mode is active.",
            hint=(
                "Set ARGUO_MODEL_BASE_URL, ARGUO_MODEL_NAME, and "
                "ARGUO_MODEL_API_KEY to enable model calls, or keep "
                "offline mode and accept heuristic drafting."
            ),
        )
