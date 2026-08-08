from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


class Modality(StrEnum):
    WIFI = "wifi"
    BLE = "ble"
    VISION = "vision"
    POSE = "pose"
    CSI = "csi"
    SDR = "sdr"
    GENERIC = "generic"


class ObservationType(StrEnum):
    RF_DETECTION = "rf_detection"
    VISUAL_DETECTION = "visual_detection"
    POSE = "pose"
    CSI_ACTIVITY = "csi_activity"
    GENERIC = "generic"


class Vec3(BaseModel):
    x: float
    y: float
    z: float = 0.0


class Observation(BaseModel):
    """Immutable fact emitted by a collector."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sensor_id: str
    modality: Modality
    type: ObservationType
    subject_key: str | None = None
    position: Vec3 | None = None
    bearing_deg: float | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    uncertainty: dict[str, float] = Field(default_factory=dict)
    payload: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    observation_id: UUID
    weight: float = Field(ge=0.0, le=1.0)
    reason: str


class Entity(BaseModel):
    """Mutable hypothesis inferred from observations."""

    id: str
    kind: str = "unknown"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    position: Vec3 | None = None
    stationary: bool | None = None
    aliases: set[str] = Field(default_factory=set)
    evidence: list[Evidence] = Field(default_factory=list)
    first_seen: datetime
    last_seen: datetime
    attributes: dict[str, Any] = Field(default_factory=dict)


class Explanation(BaseModel):
    entity: Entity
    observations: list[Observation]
