"""Model-assisted planning: prompt construction and validated plan parsing.

The planning prompt is versioned so that prompt changes are traceable in run
manifests. Plan output is validated with the ResearchPlan pydantic model; any
validation failure raises ModelOutputError instead of letting malformed model
output flow into the pipeline.
"""

from __future__ import annotations

import json

from pydantic import ValidationError

from arguo.config import ProfileConfig
from arguo.exceptions import ModelOutputError
from arguo.models import ResearchPlan
from arguo.providers.base import ModelAdapter

PROMPT_VERSION = "arguo-planning-v1"

_PLANNER_SYSTEM = (
    "You are a research planner for the Arguo system. You decompose "
    "research questions into subquestions and search queries. You return "
    "strict JSON only. You never fabricate dates, sources, numbers, or facts."
)

_SCHEMA_HINT = json.dumps(
    {
        "research_question": "string",
        "domain": "string or null",
        "audience": "string or null",
        "depth": "string",
        "time_boundary": "string or null",
        "since": "YYYY-MM-DD or null",
        "until": "YYYY-MM-DD or null",
        "subquestions": [
            {
                "subquestion_id": "string such as SQ1",
                "text": "string",
                "priority": "integer 1 to 3",
                "search_queries": ["2 to 3 precise query strings"],
                "evidence_requirements": "string or null",
                "preferred_source_types": ["strings"],
                "time_constraint": "string or null",
            }
        ],
        "anticipated_limitations": ["strings"],
        "notes": "string or null",
    },
    indent=2,
)


def build_planning_prompt(question: str, profile: ProfileConfig) -> str:
    """Build the versioned planning prompt for one research question.

    The prompt instructs the model to return strict JSON matching the
    ResearchPlan shape exactly, to produce profile.subquestion_target
    subquestions with 2-3 diverse and precise queries each, to prefer primary
    sources, to include anticipated limitations, and to never fabricate dates
    or facts.
    """
    return (
        f"PROMPT_VERSION: {PROMPT_VERSION}\n"
        "\n"
        "TASK: Produce a research plan for the question below.\n"
        "\n"
        f"RESEARCH QUESTION: {question}\n"
        f"PROFILE: {profile.name} ({profile.description})\n"
        f"SUBQUESTION TARGET: exactly {profile.subquestion_target} subquestions\n"
        f"SCHOLARLY MODE: {'on: include scholarly query variants' if profile.scholarly_mode else 'off'}\n"
        f"CONTRADICTION FOCUS: "
        f"{'on: include a subquestion on evidence for and against' if profile.contradiction_focus else 'off'}\n"
        "\n"
        "OUTPUT RULES:\n"
        "1. Return STRICT JSON and nothing else: no markdown fences, no commentary.\n"
        "2. The JSON must match exactly this shape (field names verbatim):\n"
        "   research_question (string), domain (string or null), audience (string or null),\n"
        "   depth (string), time_boundary (string or null), since (YYYY-MM-DD or null),\n"
        "   until (YYYY-MM-DD or null), subquestions (array),\n"
        "   anticipated_limitations (array of strings), notes (string or null).\n"
        "3. Each item of subquestions must have exactly these fields:\n"
        "   subquestion_id (string such as SQ1), text (string), priority (integer 1 to 3),\n"
        "   search_queries (array of 2 to 3 strings), evidence_requirements (string or null),\n"
        "   preferred_source_types (array of strings), time_constraint (string or null).\n"
        "4. Produce exactly the subquestion target count. Each subquestion gets 2 to 3\n"
        "   diverse, precise search queries: vary wording, entity names, and time scope.\n"
        "   Do not repeat the same query twice.\n"
        "5. Prefer queries that lead to primary sources: official statistics, filings,\n"
        "   standards, peer-reviewed work, and first-party reports over aggregator pages.\n"
        "6. anticipated_limitations must honestly state what this plan may miss.\n"
        "7. NEVER fabricate dates or facts. If a date or fact is unknown, use null.\n"
        "   Do not guess publication years, statistics, or entity attributes.\n"
        "\n"
        f"EXPECTED JSON SHAPE HINT:\n{_SCHEMA_HINT}\n"
    )


async def llm_plan(
    question: str,
    profile: ProfileConfig,
    adapter: ModelAdapter,
) -> ResearchPlan:
    """Plan via a ModelAdapter and validate the output into a ResearchPlan.

    Sets generated_by to the adapter name so runs can be traced to the model
    that produced the plan. Raises ModelOutputError on invalid JSON, on
    ResearchPlan validation failure, or when the plan has no subquestions.
    """
    prompt = build_planning_prompt(question, profile)
    try:
        data = await adapter.complete_json(prompt, _SCHEMA_HINT, _PLANNER_SYSTEM)
    except ModelOutputError:
        raise
    except Exception as exc:  # Provider/config failures keep their own type.
        raise ModelOutputError(
            f"Planning model call failed with {type(exc).__name__}: {exc}"
        ) from exc
    try:
        plan = ResearchPlan.model_validate(data)
    except ValidationError as exc:
        first_error = exc.errors()[0] if exc.errors() else {}
        location = ".".join(str(part) for part in first_error.get("loc", []))
        message = first_error.get("msg", "unknown validation error")
        raise ModelOutputError(
            f"Planner output failed ResearchPlan validation at '{location}': {message}. "
            f"Prompt version: {PROMPT_VERSION}."
        ) from exc
    if not plan.subquestions:
        raise ModelOutputError(
            "Planner output contained no subquestions; refusing an empty plan.",
            hint=f"Prompt version: {PROMPT_VERSION}. Retry or fall back to heuristic planning.",
        )
    plan.generated_by = adapter.name
    return plan
