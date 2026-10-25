---
title: Providers and Model Adapters
description: The SearchProvider and ModelAdapter contracts, the built-in Tavily and OpenAI-compatible implementations, and how to add your own.
group: developer-guide
slug: dg-providers
order: 5
---

Provider contracts live in arguo.providers.base. Every implementation must follow three rules stated in that module: construction performs no network activity, async methods are safe under asyncio.run, and failures raise typed exceptions from arguo.exceptions, never bare Exception or SDK types.

SearchProvider declares a name property and async search(query: str, max_results: int) -> list[NormalizedResult]. ModelAdapter declares a name property, async complete_json(prompt: str, schema_hint: str, system: str | None = None) -> dict, and async complete_text(prompt: str, system: str | None = None) -> str.

TavilySearchProvider(api_key, timeout_s=15.0, max_retries=2) POSTs to https://api.tavily.com/search with the key in the payload and search_depth "basic". Parsing is tolerant: _parse_tavily_item maps any missing or mistyped optional field to None instead of dropping the result, and a non-string url degrades to an empty string that downstream URL validation filters out. HTTP 429, 5xx, and transport errors are retried with exponential backoff of 0.5s, 1s, 2s, capped at 4s. After retries are exhausted, 429 maps to RateLimitError and everything else to ProviderError. An empty query raises ProviderError. The api key is registered with the secret registry at construction and never logged.

OpenAICompatibleAdapter(base_url, api_key, model, temperature=0.2, timeout_s=60.0, max_retries=2) builds the endpoint by appending /chat/completions unless base_url already ends with it. complete_json sends response_format {"type": "json_object"} and parses with parse_model_json, which makes exactly one repair attempt by stripping a surrounding markdown code fence before raising ModelOutputError. HTTP 401 raises ConfigurationError with an ARGUO_MODEL_API_KEY hint, 429 retries then raises RateLimitError, and 5xx and transport errors retry with the same backoff schedule. Its name is "openai-compatible:{model}".

NullModelAdapter is the offline placeholder: both methods raise ModelOutputError with a hint about enabling model calls, so a run without a model falls back to heuristic planning and review instead of producing model-made claims silently.

To write a custom provider: subclass SearchProvider or ModelAdapter, return a stable name, keep __init__ free of network activity, register credentials with REGISTRY from utilities.logging, map failures to typed exceptions, and return NormalizedResult items so dedupe and collection work unchanged.

```python
class MySearch(SearchProvider):
    @property
    def name(self) -> str:
        return "my-provider"

    async def search(self, query, max_results):
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url, params={"q": query})
        if resp.status_code == 429:
            raise RateLimitError("rate limited")
        return [_to_normalized(item) for item in resp.json()["hits"]]
```
