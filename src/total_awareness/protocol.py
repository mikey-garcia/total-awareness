from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

REQUIRED = {"time", "sensor", "type", "id", "data"}


def observation(sensor: str, type: str, id: str | None = None, data: dict[str, Any] | None = None, time: str | None = None) -> dict[str, Any]:
    return {
        "time": time or datetime.now(timezone.utc).isoformat(),
        "sensor": sensor,
        "type": type,
        "id": id,
        "data": data or {},
    }


def validate(obs: dict[str, Any]) -> dict[str, Any]:
    if set(obs) != REQUIRED:
        raise ValueError(f"observation must contain exactly {sorted(REQUIRED)}")
    if not obs["sensor"] or not obs["type"] or not isinstance(obs["data"], dict):
        raise ValueError("invalid observation")
    if obs["id"] is not None and not isinstance(obs["id"], str):
        raise ValueError("observation id must be a string or null")
    return obs


# Backwards-compatible name for callers outside the package.
message = observation
