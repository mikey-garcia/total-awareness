from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

REQUIRED = {"time", "sensor", "id", "data"}


def observation(sensor: str, id: str, data: dict[str, Any] | None = None, time: str | None = None) -> dict[str, Any]:
    return {
        "time": time or datetime.now(timezone.utc).isoformat(),
        "sensor": sensor,
        "id": id,
        "data": data or {},
    }


def validate(obs: dict[str, Any]) -> dict[str, Any]:
    if set(obs) != REQUIRED:
        raise ValueError(f"observation must contain exactly {sorted(REQUIRED)}")
    if not obs["sensor"] or not isinstance(obs["id"], str) or not obs["id"] or not isinstance(obs["data"], dict):
        raise ValueError("invalid observation")
    return obs


message = observation
