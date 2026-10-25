"""OpenAI-compatible chat completion adapter.

Talks to any endpoint that implements POST {base_url}/chat/completions with
the OpenAI request and response shapes. Construction performs no network
activity; requests happen only inside async methods. The API key is never
logged and never appears in exception messages.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import Any

import httpx

from arguo.exceptions import (
    ConfigurationError,
    ModelOutputError,
    ProviderError,
    RateLimitError,
)
from arguo.providers.base import ModelAdapter
from arguo.utilities.logging import REGISTRY, get_logger

logger = get_logger("arguo.providers.model")

_BACKOFF_BASE_S = 0.5
_BACKOFF_CAP_S = 4.0

_CODE_FENCE_START = re.compile(r"^```(?:json)?\s*", re.IGNORECASE)
_CODE_FENCE_END = re.compile(r"```\s*$")


def _backoff_delay_s(attempt: int) -> float:
    """Exponential backoff: 0.5s, 1s, 2s, capped at 4s."""
    return min(_BACKOFF_BASE_S * (2 ** attempt), _BACKOFF_CAP_S)


def _strip_code_fences(text: str) -> str:
    """Remove a single surrounding markdown code fence, if present."""
    stripped = text.strip()
    stripped = _CODE_FENCE_START.sub("", stripped, count=1)
    stripped = _CODE_FENCE_END.sub("", stripped, count=1)
    return stripped.strip()


def parse_model_json(content: str) -> dict:
    """Parse model output into a JSON object with one fence-strip repair attempt.

    Raises ModelOutputError when the content is not valid JSON or is not a
    JSON object after the single repair attempt.
    """
    if not isinstance(content, str) or not content.strip():
        raise ModelOutputError(
            "Model returned empty content where JSON was expected.",
            hint="Retry the call, or check that the endpoint supports json_object responses.",
        )
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        repaired = _strip_code_fences(content)
        try:
            data = json.loads(repaired)
        except json.JSONDecodeError as exc:
            preview = content.strip()[:200]
            raise ModelOutputError(
                f"Model output is not valid JSON after one repair attempt: {exc}. "
                f"Output began with: {preview!r}"
            ) from exc
    if not isinstance(data, dict):
        raise ModelOutputError(
            f"Model output JSON is a {type(data).__name__}, not an object."
        )
    return data


class OpenAICompatibleAdapter(ModelAdapter):
    """ModelAdapter for OpenAI-compatible /chat/completions endpoints.

    Args:
        base_url: Endpoint root such as https://host/v1. /chat/completions is
            appended unless base_url already ends with it.
        api_key: Bearer token, or None for unauthenticated endpoints.
        model: Model identifier the endpoint expects.
        temperature: Sampling temperature forwarded to the endpoint.
        timeout_s: Per-request timeout in seconds.
        max_retries: Retries for HTTP 429, 5xx, and transport errors.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        model: str,
        temperature: float = 0.2,
        timeout_s: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        if not base_url or not base_url.strip():
            raise ConfigurationError(
                "OpenAICompatibleAdapter requires a non-empty base_url.",
                hint="Set ARGUO_MODEL_BASE_URL to an OpenAI-compatible /v1 endpoint.",
            )
        if not model or not model.strip():
            raise ConfigurationError(
                "OpenAICompatibleAdapter requires a non-empty model name.",
                hint="Set ARGUO_MODEL_NAME to the model identifier your endpoint expects.",
            )
        self._base_url = base_url.strip().rstrip("/")
        if not self._base_url.endswith("/chat/completions"):
            self._base_url = f"{self._base_url}/chat/completions"
        self._api_key = api_key
        self._model = model.strip()
        self._temperature = temperature
        self._timeout_s = timeout_s
        self._max_retries = max_retries
        REGISTRY.register(api_key)

    @property
    def name(self) -> str:
        return f"openai-compatible:{self._model}"

    async def complete_json(
        self,
        prompt: str,
        schema_hint: str,
        system: str | None = None,
    ) -> dict:
        """Request a JSON object and parse it with one repair attempt."""
        messages = self._messages(prompt, system)
        content = await self._complete(messages, response_format={"type": "json_object"})
        return parse_model_json(content)

    async def complete_text(self, prompt: str, system: str | None = None) -> str:
        """Request plain text completion."""
        messages = self._messages(prompt, system)
        return await self._complete(messages, response_format=None)

    def _messages(self, prompt: str, system: str | None) -> list[dict[str, str]]:
        built: list[dict[str, str]] = []
        if system:
            built.append({"role": "system", "content": system})
        built.append({"role": "user", "content": prompt})
        return built

    async def _complete(
        self,
        messages: list[dict[str, str]],
        response_format: dict[str, str] | None,
    ) -> str:
        body: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": self._temperature,
        }
        if response_format is not None:
            body["response_format"] = response_format
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        async with httpx.AsyncClient(timeout=self._timeout_s) as client:
            response = await self._post_with_retry(client, headers, body)
        try:
            payload = response.json()
            content = payload["choices"][0]["message"]["content"]
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            raise ProviderError(
                "Model endpoint returned an unexpected response shape: "
                f"{exc}; expected choices[0].message.content."
            ) from exc
        if not isinstance(content, str):
            raise ProviderError(
                f"Model endpoint returned non-string content of type "
                f"{type(content).__name__}."
            )
        return content

    async def _post_with_retry(
        self,
        client: httpx.AsyncClient,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> httpx.Response:
        """POST with retries; map 429 to RateLimitError, 401 to ConfigurationError."""
        last_status: int | None = None
        for attempt in range(self._max_retries + 1):
            try:
                response = await client.post(self._base_url, json=body, headers=headers)
            except httpx.HTTPError as exc:
                if attempt < self._max_retries:
                    logger.warning("Model endpoint transport error, retrying: %s", exc)
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise ProviderError(
                    f"Model endpoint unreachable after {self._max_retries + 1} attempts "
                    f"at {self._base_url}: {type(exc).__name__}"
                ) from exc
            if response.status_code == 429:
                last_status = response.status_code
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise RateLimitError(
                    "Model endpoint rate limited the request (HTTP 429) after "
                    f"{self._max_retries + 1} attempts.",
                    hint="Retry later or reduce max_model_calls in the budget.",
                )
            if response.status_code == 401:
                raise ConfigurationError(
                    "Model endpoint rejected credentials (HTTP 401).",
                    hint="check ARGUO_MODEL_API_KEY",
                )
            if response.status_code >= 500:
                last_status = response.status_code
                if attempt < self._max_retries:
                    await asyncio.sleep(_backoff_delay_s(attempt))
                    continue
                raise ProviderError(
                    f"Model endpoint server error (HTTP {last_status}) after "
                    f"{self._max_retries + 1} attempts."
                )
            if not response.is_success:
                raise ProviderError(
                    f"Model endpoint returned HTTP {response.status_code}: "
                    f"{response.text[:200]}"
                )
            return response
        raise ProviderError(
            f"Model request did not complete (last HTTP status: {last_status})."
        )
