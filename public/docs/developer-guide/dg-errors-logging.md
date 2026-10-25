---
title: Errors and Logging
description: The typed exception hierarchy with exit codes, structured logging setup, and secret redaction.
group: developer-guide
slug: dg-errors-logging
order: 9
---

Every failure mode has a dedicated class in arguo.exceptions. Each carries an optional hint string, user_message() appends it after the base message, and each class documents the exit code the CLI uses.

| Class | Exit code | Meaning |
| --- | --- | --- |
| EvidenceLedgerError | 1 | Base class for all toolkit errors |
| ConfigurationError | 2 | Missing or invalid configuration, such as a missing API key or bad profile |
| ProviderError | 3 | A search or model provider failed or returned invalid data |
| RateLimitError | 4 | Provider rate limit hit after retries (subclass of ProviderError) |
| RetrievalError | 5 | A page could not be retrieved or was rejected by safety limits |
| UnsafeURLError | 6 | URL rejected by the SSRF guard or scheme allowlist (subclass of RetrievalError) |
| InvalidSourceError | 7 | A source record failed validation or does not support its claim |
| ModelOutputError | 8 | Model output failed schema validation after retries (subclass of ProviderError) |
| InsufficientEvidenceError | 9 | The evidence base cannot support the requested output; a normal research outcome |
| ReportGenerationError | 10 | Report assembly failed, for example a missing required artifact |
| BudgetExceededError | 11 | A configured budget of time, bytes, or calls was exhausted |
| ResourceCatalogError | 12 | The resource catalog is missing, unreadable, or failed validation |
| PromptInjectionSuspectedError | 13 | Retrieved content contained instruction-like patterns and the caller asked to fail closed |

Structured logging lives in arguo.utilities.logging. setup_logging(level="INFO", json_mode=False) configures the arguo root logger once: it writes to stderr, uses JsonFormatter with ts, level, logger, message, and exception keys when json_mode is True, and the plain "%(levelname)s %(name)s: %(message)s" format otherwise. Repeated calls do not add handlers. get_logger(name) returns a logger and attaches SecretRedactingFilter if it is not already present, so module loggers stay safe even before setup_logging runs.

Secret redaction is registry based. The module-level REGISTRY is a SecretRegistry holding known secret values; register(value) stores strings of at least 6 characters, deduplicated. The filter scrubs every log message and every argument tuple, replacing occurrences with [REDACTED]. scrub_text and scrub_obj are also available for explicit use on strings, dicts, lists, and tuples. Both provider implementations register their API keys at construction time, so key material never reaches log output or exception messages.
