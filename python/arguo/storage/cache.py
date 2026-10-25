"""File-based JSON response cache with TTL and corrupt-file tolerance.

Used for HTTP fetches and any other run-scoped payload worth reusing. All
operations treat unreadable or malformed cache files as cache misses instead
of raising, so a damaged cache directory never breaks a research run.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from arguo.utilities.logging import get_logger

logger = get_logger("arguo.storage.cache")


def cache_key(key: str) -> str:
    """Return the sha256 hex digest used as the on-disk file name for key."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class ResponseCache:
    """Content-addressed JSON cache stored as one file per key.

    Args:
        dir: Directory that holds ``{sha256}.json`` entries. Created lazily.
        ttl_s: Maximum age in seconds for a stored value to count as fresh.
    """

    def __init__(self, dir: Path, ttl_s: int) -> None:  # noqa: A002 - spec name
        self.dir = Path(dir)
        self.ttl_s = ttl_s

    def _path_for(self, key: str) -> Path:
        return self.dir / f"{cache_key(key)}.json"

    def get(self, key: str) -> Any | None:
        """Return the cached value for key, or None on miss, expiry, or damage.

        Corrupt JSON, missing fields, and unparsable timestamps are all
        treated as a miss; this method never raises for bad cache content.
        """
        path = self._path_for(key)
        if not path.is_file():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            stored_at = payload["stored_at"]
            value = payload["value"]
        except (OSError, ValueError, KeyError, TypeError) as exc:
            logger.debug("cache miss (unreadable entry) for key %s: %s", key, exc)
            return None
        try:
            stored_dt = datetime.fromisoformat(str(stored_at))
            if stored_dt.tzinfo is None:
                stored_dt = stored_dt.replace(tzinfo=UTC)
            age_s = (datetime.now(UTC) - stored_dt).total_seconds()
        except ValueError as exc:
            logger.debug("cache miss (bad timestamp) for key %s: %s", key, exc)
            return None
        if age_s > self.ttl_s:
            return None
        return value

    def put(self, key: str, value: Any) -> None:
        """Store value under key. Storage failures are logged, never raised.

        Values must be JSON serializable; callers store plain data structures.
        """
        try:
            self.dir.mkdir(parents=True, exist_ok=True)
            entry = {
                "stored_at": datetime.now(UTC).isoformat(timespec="seconds"),
                "value": value,
            }
            tmp_path = self._path_for(key).with_suffix(".tmp")
            tmp_path.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
            tmp_path.replace(self._path_for(key))
        except (OSError, ValueError, TypeError) as exc:
            logger.warning("cache write failed for key %s: %s", key, exc)

    def clear(self) -> int:
        """Delete every cache entry in the directory. Returns count removed."""
        if not self.dir.is_dir():
            return 0
        removed = 0
        for path in self.dir.glob("*.json"):
            try:
                path.unlink()
                removed += 1
            except OSError as exc:
                logger.warning("cache clear could not remove %s: %s", path, exc)
        return removed

    def stats(self) -> dict:
        """Return {"entries", "oldest", "newest"} for the cache directory.

        oldest and newest are ISO timestamps or None when the cache is empty
        or its timestamps are unreadable. Unreadable files still count as
        entries so callers can notice a damaged cache.
        """
        entries = 0
        timestamps: list[datetime] = []
        if self.dir.is_dir():
            for path in self.dir.glob("*.json"):
                entries += 1
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                    stored_dt = datetime.fromisoformat(str(payload["stored_at"]))
                    timestamps.append(stored_dt)
                except (OSError, ValueError, KeyError, TypeError):
                    continue
        oldest = min(timestamps).isoformat() if timestamps else None
        newest = max(timestamps).isoformat() if timestamps else None
        return {"entries": entries, "oldest": oldest, "newest": newest}
