"""Shared utilities: URL normalization, date handling, ids, logging, text."""

from arguo.utilities.dates import coerce_date, format_date_or_unknown, parse_date_lenient
from arguo.utilities.ids import new_id, sequential_id
from arguo.utilities.logging import SecretRedactingFilter, get_logger, setup_logging
from arguo.utilities.text import (
    normalize_whitespace,
    token_overlap,
    truncate_chars,
)
from arguo.utilities.urls import (
    get_registrable_domain,
    is_probably_same_url,
    normalize_url,
)

__all__ = [
    "coerce_date",
    "format_date_or_unknown",
    "parse_date_lenient",
    "new_id",
    "sequential_id",
    "get_logger",
    "setup_logging",
    "SecretRedactingFilter",
    "normalize_whitespace",
    "truncate_chars",
    "token_overlap",
    "get_registrable_domain",
    "is_probably_same_url",
    "normalize_url",
]
