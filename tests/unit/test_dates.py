"""Tests for arguo.utilities.dates: unknown stays unknown."""

from __future__ import annotations

from datetime import date

from arguo.utilities.dates import (
    coerce_date,
    format_date_or_unknown,
    parse_date_lenient,
)


def test_parses_iso_date() -> None:
    assert parse_date_lenient("2024-06-01") == date(2024, 6, 1)


def test_parses_iso_datetime_with_z_suffix() -> None:
    assert parse_date_lenient("2024-06-01T12:30:00Z") == date(2024, 6, 1)


def test_parses_year_only_as_january_first() -> None:
    assert parse_date_lenient("2024") == date(2024, 1, 1)


def test_parses_month_name_dates() -> None:
    assert parse_date_lenient("March 5, 2024") == date(2024, 3, 5)
    assert parse_date_lenient("June 1, 2024") == date(2024, 6, 1)


def test_parses_rfc_2822_dates() -> None:
    assert parse_date_lenient("Sat, 01 Jun 2024 12:00:00 GMT") == date(2024, 6, 1)


def test_garbage_returns_none() -> None:
    assert parse_date_lenient("not a date") is None
    assert parse_date_lenient("2024-02-31") is None


def test_empty_and_none_return_none() -> None:
    assert parse_date_lenient("") is None
    assert parse_date_lenient(None) is None
    assert parse_date_lenient("   ") is None


def test_coerce_date_passes_dates_through() -> None:
    day = date(2023, 3, 4)
    assert coerce_date(day) is day
    assert coerce_date("2023-03-04") == day


def test_format_date_or_unknown_with_none() -> None:
    assert format_date_or_unknown(None) == "date unknown"
    assert format_date_or_unknown("garbage") == "date unknown"
    assert format_date_or_unknown("2024-06-01") == "2024-06-01"
