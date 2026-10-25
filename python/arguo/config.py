"""Configuration, research profiles, and budget enforcement.

Settings load from environment variables with the ARGUO_ prefix plus
selected provider variables (TAVILY_API_KEY). Nothing here reads or logs
secret values.
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from arguo.exceptions import ConfigurationError


class ResearchBudget(BaseModel):
    """Hard limits for one research run. Profiles set different values."""

    max_search_rounds: int = 2
    results_per_query: int = 6
    max_sources: int = 15
    max_total_bytes: int = 8_000_000
    per_request_timeout_s: float = 20.0
    concurrency: int = 4
    max_model_output_tokens: int = 2000
    max_retries: int = 2
    max_runtime_s: float = 300.0
    max_model_calls: int = 24
    max_cost_usd: float | None = Field(
        default=None,
        description="Optional soft cost estimate cap. Best effort only, provider pricing varies.",
    )
    followup_rounds: int = 1


class ProfileConfig(BaseModel):
    """A named research profile that changes actual workflow behavior."""

    name: str
    description: str
    subquestion_target: int
    budget: ResearchBudget
    report_length: Literal["concise", "standard", "detailed"] = "standard"
    scholarly_mode: bool = False
    contradiction_focus: bool = False


def _budget(
    *, rounds: int, per_query: int, sources: int, model_calls: int,
    followups: int, runtime: float, concurrency: int = 4,
) -> ResearchBudget:
    return ResearchBudget(
        max_search_rounds=rounds,
        results_per_query=per_query,
        max_sources=sources,
        max_model_calls=model_calls,
        followup_rounds=followups,
        max_runtime_s=runtime,
        concurrency=concurrency,
    )


PROFILES: dict[str, ProfileConfig] = {
    "quick": ProfileConfig(
        name="quick",
        description="Small search plan and a concise report for fast lookups.",
        subquestion_target=3,
        budget=_budget(rounds=1, per_query=4, sources=8, model_calls=8, followups=0, runtime=120),
        report_length="concise",
    ),
    "standard": ProfileConfig(
        name="standard",
        description="Balanced coverage with source evaluation and citation auditing.",
        subquestion_target=5,
        budget=_budget(rounds=2, per_query=6, sources=15, model_calls=18, followups=1, runtime=300),
        report_length="standard",
    ),
    "deep": ProfileConfig(
        name="deep",
        description="More subquestions, multiple search rounds, explicit contradiction analysis.",
        subquestion_target=8,
        budget=_budget(rounds=3, per_query=8, sources=30, model_calls=30, followups=2, runtime=600, concurrency=6),
        report_length="detailed",
        contradiction_focus=True,
    ),
    "academic": ProfileConfig(
        name="academic",
        description="Literature oriented queries, study metadata, methods, limitations, and gaps.",
        subquestion_target=6,
        budget=_budget(rounds=2, per_query=8, sources=20, model_calls=24, followups=1, runtime=480, concurrency=4),
        report_length="detailed",
        scholarly_mode=True,
    ),
}

SearchProviderName = Literal["tavily", "offline"]
ModelProviderName = Literal["openai-compatible", "null"]


class Settings(BaseModel):
    """Runtime settings resolved from environment variables."""

    search_provider: SearchProviderName = "tavily"
    tavily_api_key: str | None = None
    model_provider: ModelProviderName = "openai-compatible"
    model_base_url: str | None = None
    model_api_key: str | None = None
    model_name: str | None = None
    model_temperature: float = 0.2
    max_model_calls: int = 24
    output_dir: Path = Path("./runs")
    cache_dir: Path = Path("./.arguo-cache")
    cache_ttl_s: int = 86_400
    user_agent: str = "Arguo/0.1 (+https://github.com/izynu/arguo)"
    profile: str = "standard"

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if env is None else env)
        profile = (env.get("ARGUO_PROFILE") or "standard").strip().lower()
        if profile not in PROFILES:
            raise ConfigurationError(
                f"Unknown ARGUO_PROFILE '{profile}'",
                hint=f"Choose one of: {', '.join(sorted(PROFILES))}",
            )
        model_provider = (env.get("ARGUO_MODEL_PROVIDER") or "openai-compatible").strip()
        if model_provider not in ("openai-compatible", "null"):
            raise ConfigurationError(
                f"Unknown ARGUO_MODEL_PROVIDER '{model_provider}'",
                hint="Use 'openai-compatible' or 'null' for offline runs.",
            )
        search_provider = (env.get("ARGUO_SEARCH_PROVIDER") or "tavily").strip().lower()
        if search_provider not in ("tavily", "offline"):
            raise ConfigurationError(
                f"Unknown ARGUO_SEARCH_PROVIDER '{search_provider}'",
                hint="Use 'tavily' or 'offline'.",
            )
        max_calls_raw = env.get("ARGUO_MAX_MODEL_CALLS") or "24"
        try:
            max_calls = int(max_calls_raw)
        except ValueError as exc:
            raise ConfigurationError(
                f"ARGUO_MAX_MODEL_CALLS must be an integer, got '{max_calls_raw}'"
            ) from exc
        return cls(
            search_provider=search_provider,  # type: ignore[arg-type]
            tavily_api_key=env.get("TAVILY_API_KEY") or None,
            model_provider=model_provider,  # type: ignore[arg-type]
            model_base_url=env.get("ARGUO_MODEL_BASE_URL") or None,
            model_api_key=env.get("ARGUO_MODEL_API_KEY") or None,
            model_name=env.get("ARGUO_MODEL_NAME") or None,
            model_temperature=float(env.get("ARGUO_MODEL_TEMPERATURE") or 0.2),
            max_model_calls=max_calls,
            output_dir=Path(env.get("ARGUO_OUTPUT_DIR") or "./runs"),
            cache_dir=Path(env.get("ARGUO_CACHE_DIR") or "./.arguo-cache"),
        )

    def validate_for_research(self, offline: bool) -> list[str]:
        """Return warnings; raise ConfigurationError for blocking problems."""
        warnings: list[str] = []
        if offline:
            warnings.append("Offline mode: fixture providers produce a demonstration run, not live research.")
            return warnings
        if self.search_provider == "tavily" and not self.tavily_api_key:
            raise ConfigurationError(
                "TAVILY_API_KEY is not set but the search provider is 'tavily'.",
                hint="Export TAVILY_API_KEY or run with --offline.",
            )
        if self.model_provider == "openai-compatible":
            if not self.model_base_url:
                raise ConfigurationError(
                    "ARGUO_MODEL_BASE_URL is not set.",
                    hint="Point it at an OpenAI-compatible /v1 endpoint, or use --offline.",
                )
            if not self.model_name:
                raise ConfigurationError(
                    "ARGUO_MODEL_NAME is not set.",
                    hint="Set the model identifier your endpoint expects, for example glm-4-flash.",
                )
            if not self.model_api_key:
                warnings.append("ARGUO_MODEL_API_KEY is empty; endpoint must allow unauthenticated access.")
        return warnings


_settings: Settings | None = None


def get_settings(env: dict[str, str] | None = None, reload: bool = False) -> Settings:
    global _settings
    if _settings is None or reload or env is not None:
        _settings = Settings.from_env(env)
    return _settings


class BudgetTracker:
    """Enforces budgets during a run. Raises BudgetExceededError when spent."""

    def __init__(self, budget: ResearchBudget, started_at: float | None = None) -> None:
        self.budget = budget
        self._started = started_at if started_at is not None else time.monotonic()
        self.search_requests = 0
        self.model_calls = 0
        self.bytes_retrieved = 0
        self.sources_seen = 0

    def elapsed(self) -> float:
        return time.monotonic() - self._started

    def check_time(self) -> None:
        from arguo.exceptions import BudgetExceededError

        if self.elapsed() > self.budget.max_runtime_s:
            raise BudgetExceededError(
                f"Runtime budget of {self.budget.max_runtime_s:.0f}s exceeded after {self.elapsed():.0f}s.",
                hint="Raise max_runtime_s in the profile or choose a smaller question scope.",
            )

    def record_search(self, n: int = 1) -> None:

        self.search_requests += n
        self.check_time()

    def record_model_call(self, n: int = 1) -> None:
        from arguo.exceptions import BudgetExceededError

        self.model_calls += n
        if self.model_calls > self.budget.max_model_calls:
            raise BudgetExceededError(
                f"Model call budget of {self.budget.max_model_calls} exceeded.",
                hint="Reduce subquestions or switch to the quick profile.",
            )

    def record_bytes(self, n: int) -> None:
        from arguo.exceptions import BudgetExceededError

        self.bytes_retrieved += n
        if self.bytes_retrieved > self.budget.max_total_bytes:
            raise BudgetExceededError(
                f"Retrieval budget of {self.budget.max_total_bytes} bytes exceeded.",
                hint="Lower results_per_query or per-request size limits.",
            )

    def record_source(self) -> None:
        from arguo.exceptions import BudgetExceededError

        self.sources_seen += 1
        if self.sources_seen > self.budget.max_sources:
            raise BudgetExceededError(
                f"Source budget of {self.budget.max_sources} exceeded.",
                hint="Raise max_sources in the profile configuration.",
            )

    def snapshot(self) -> dict:
        return {
            "search_requests": self.search_requests,
            "model_calls": self.model_calls,
            "bytes_retrieved": self.bytes_retrieved,
            "sources_seen": self.sources_seen,
            "elapsed_s": round(self.elapsed(), 1),
            "limits": self.budget.model_dump(),
        }
