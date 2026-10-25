"""Date parsing and formatting with explicit unknown handling.

Unknown dates must remain unknown. This module never guesses a year from a
partial string without saying so.
"""

from __future__ import annotations

import re
from datetime import date, datetime

_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_YEAR_RE = re.compile(r"^\d{4}$")
_MONTH_NAMES = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_SHORT_MONTHS = {m[:3]: n for m, n in _MONTH_NAMES.items()}


def parse_date_lenient(value: str | None) -> date | None:
    """Parse common date formats. Returns None for unknown or invalid input.

    Supported: ISO 8601 (date or datetime), YYYY, month-name D, YYYY,
    RFC 2822 style dates. Anything else returns None rather than guessing.
    """
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    match = _ISO_RE.match(value)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    if _YEAR_RE.match(value):
        try:
            return date(int(value), 1, 1)
        except ValueError:
            return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        from email.utils import parsedate_to_datetime

        parsed = parsedate_to_datetime(value)
        if parsed is not None:
            return parsed.date()
    except (TypeError, ValueError):
        pass
    lowered = value.lower().replace(",", " ").split()
    if len(lowered) >= 3:
        month_token = lowered[0][:3]
        month = _SHORT_MONTHS.get(month_token)
        if month:
            try:
                day = int(lowered[1])
                year = int(lowered[2])
                return date(year, month, day)
            except ValueError:
                return None
    return None


def coerce_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return parse_date_lenient(value)


def format_date_or_unknown(value: str | date | None, unknown_label: str = "date unknown") -> str:
    """Render a date for reports. Unknown stays explicitly unknown."""
    parsed = coerce_date(value)
    if parsed is None:
        return unknown_label
    return parsed.isoformat()
