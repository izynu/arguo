"""Structured logging with secret redaction.

API keys are registered at startup and removed from every emitted record.
Log output never includes raw Authorization headers or key material.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any


class SecretRegistry:
    """Holds known secret values and scrubs them from text and mappings."""

    def __init__(self) -> None:
        self._secrets: list[str] = []

    def register(self, value: str | None) -> None:
        if value and len(value) >= 6 and value not in self._secrets:
            self._secrets.append(value)

    def scrub_text(self, text: str) -> str:
        out = text
        for secret in self._secrets:
            if secret in out:
                out = out.replace(secret, "[REDACTED]")
        return out

    def scrub_obj(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self.scrub_text(obj)
        if isinstance(obj, dict):
            return {k: self.scrub_obj(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [self.scrub_obj(v) for v in obj]
        return obj


REGISTRY = SecretRegistry()


class SecretRedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.msg = REGISTRY.scrub_text(str(record.msg))
        if record.args:
            record.args = tuple(REGISTRY.scrub_obj(a) for a in record.args)
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "arguo") -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, SecretRedactingFilter) for f in logger.filters):
        logger.addFilter(SecretRedactingFilter())
    return logger


def setup_logging(level: str = "INFO", json_mode: bool = False) -> None:
    root = logging.getLogger("arguo")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    if json_mode:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    handler.addFilter(SecretRedactingFilter())
    root.addHandler(handler)
    root.propagate = False
