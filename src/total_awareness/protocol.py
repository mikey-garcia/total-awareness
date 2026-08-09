"""The one boundary format used by sensors, storage, core, and API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

REQUIRED = {"time", "sensor", "type", "id", "data"}


def message(*, sensor: str, type: str, id: str | None = None, data: dict[str, Any] | None = None, time: str | None = None) -> dict[str, Any]:
    """Create a canonical Total Awareness observation dictionary."""
    return {
        "time": time or datetime.now(timezone.utc).isoformat(),
        "sensor": sensor,
        "type": type,
        "id": id,
        "data": data or {},
    }


def validate(value: dict[str, Any]) -> dict[str, Any]:
    """Fail early at system boundaries; otherwise keep the protocol boring."""
    if set(value) != REQUIRED:
        missing = REQUIRED - set(value)
        extra = set(value) - REQUIRED
        raise ValueError(f"invalid observation keys; missing={sorted(missing)}, extra={sorted(extra)}")
    if not isinstance(value["sensor"], str) or not value["sensor"]:
        raise ValueError("sensor must be a non-empty string")
    if not isinstance(value["type"], str) or not value["type"]:
        raise ValueError("type must be a non-empty string")
    if value["id"] is not None and not isinstance(value["id"], str):
        raise ValueError("id must be a string or null")
    if not isinstance(value["data"], dict):
        raise ValueError("data must be an object")
    return value
