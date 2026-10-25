"""Run-scoped identifiers."""

from __future__ import annotations

import uuid


def new_id(prefix: str) -> str:
    """Generate a readable run-scoped id such as E-3f9c2a1b."""
    token = uuid.uuid4().hex[:8]
    return f"{prefix}-{token}"


def sequential_id(prefix: str, n: int) -> str:
    """Generate a stable sequential id such as S3 or C12."""
    return f"{prefix}{n}"
