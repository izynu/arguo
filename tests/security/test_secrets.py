"""Security tests: secret handling and log redaction."""

from __future__ import annotations

import logging
from io import StringIO

from typer.testing import CliRunner

from arguo.cli import app
from arguo.config import Settings
from arguo.storage.cache import cache_key
from arguo.utilities.logging import (
    REGISTRY,
    SecretRedactingFilter,
    SecretRegistry,
)

SECRET = "sk-secret-value-123"
runner = CliRunner()


def test_registry_scrubs_registered_secret_from_text() -> None:
    registry = SecretRegistry()
    registry.register(SECRET)
    scrubbed = registry.scrub_text(
        f"provider call failed with key {SECRET} present"
    )
    assert SECRET not in scrubbed
    assert "[REDACTED]" in scrubbed


def test_global_registry_scrubs_nested_structures() -> None:
    REGISTRY.register(SECRET)
    payload = {"note": f"key={SECRET}", "items": [SECRET, "safe"]}
    scrubbed = REGISTRY.scrub_obj(payload)
    assert SECRET not in repr(scrubbed)
    assert "safe" in repr(scrubbed)


def test_log_handler_output_is_redacted(caplog) -> None:  # noqa: ARG001
    REGISTRY.register(SECRET)
    logger = logging.getLogger("arguo.test.secrets")
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(SecretRedactingFilter())
    logger.addHandler(handler)
    try:
        logger.warning("request used key %s during fetch", SECRET)
    finally:
        logger.removeHandler(handler)
    output = stream.getvalue()
    assert SECRET not in output
    assert "[REDACTED]" in output


def test_short_values_are_not_treated_as_secrets() -> None:
    registry = SecretRegistry()
    registry.register("abc")  # below the 6 character threshold
    assert registry.scrub_text("abc stays") == "abc stays"


def test_config_check_prints_booleans_never_values() -> None:
    result = runner.invoke(
        app, ["config", "check"], env={"TAVILY_API_KEY": SECRET}
    )
    assert result.exit_code == 0
    assert "TAVILY_API_KEY set: True" in result.output
    assert SECRET not in result.output


def test_settings_store_but_do_not_echo_the_key() -> None:
    settings = Settings.from_env(env={"TAVILY_API_KEY": SECRET})
    assert settings.tavily_api_key == SECRET
    # The fields the CLI prints are flags and names only.
    assert settings.search_provider in ("tavily", "offline")
    assert settings.model_base_url is None


def test_cache_keys_hash_secrets_away() -> None:
    digest = cache_key(f"fetch:url-with-{SECRET}")
    assert SECRET not in digest
    assert len(digest) == 64
