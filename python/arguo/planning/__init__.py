"""Planning: research question decomposition into subquestions and queries."""

from __future__ import annotations

from arguo.config import ProfileConfig
from arguo.models import ResearchPlan
from arguo.planning.heuristic import heuristic_plan
from arguo.planning.llm import PROMPT_VERSION, build_planning_prompt, llm_plan
from arguo.providers.base import ModelAdapter

__all__ = [
    "make_plan",
    "heuristic_plan",
    "build_planning_prompt",
    "llm_plan",
    "PROMPT_VERSION",
]


async def make_plan(
    question: str,
    profile: ProfileConfig,
    adapter: ModelAdapter | None,
    offline: bool = False,
) -> ResearchPlan:
    """Pick the LLM planner when available, else the deterministic heuristic.

    The heuristic planner runs when offline is True or no adapter is given.
    Otherwise the model-assisted planner runs and its output is validated.
    """
    if offline or adapter is None:
        return heuristic_plan(question, profile)
    return await llm_plan(question, profile, adapter)
