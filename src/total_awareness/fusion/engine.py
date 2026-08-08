from __future__ import annotations

import math

from total_awareness.core.models import Observation, ObservationType, Vec3
from total_awareness.core.world import WorldModel


class FusionEngine:
    """Deliberately conservative baseline fusion engine.

    V0 uses stable subject keys when available. Cross-modal association is exposed as
    a separate step rather than silently merging identities. Future implementations
    can replace this with factor-graph / probabilistic association without changing
    collector contracts or the event log.
    """

    def __init__(self, world: WorldModel | None = None) -> None:
        self.world = world or WorldModel()
        self._observer_position: Vec3 | None = None

    def ingest(self, obs: Observation):
        if obs.type is ObservationType.POSE:
            if obs.position is not None and obs.subject_key == "observer:self":
                self._observer_position = obs.position
            return self.world.upsert_from_observation(obs, kind="observer", confidence=1.0)
        if obs.type is ObservationType.VISUAL_DETECTION:
            inferred_position = None
            range_hint = obs.payload.get("range_hint_m")
            if (
                self._observer_position is not None
                and obs.bearing_deg is not None
                and isinstance(range_hint, (int, float))
            ):
                angle = math.radians(obs.bearing_deg)
                inferred_position = Vec3(
                    x=self._observer_position.x + float(range_hint) * math.cos(angle),
                    y=self._observer_position.y + float(range_hint) * math.sin(angle),
                    z=self._observer_position.z,
                )
            return self.world.upsert_from_observation(
                obs,
                kind=str(obs.payload.get("class", "unknown")),
                confidence=obs.confidence,
                inferred_position=inferred_position,
            )
        if obs.type is ObservationType.RF_DETECTION:
            return self.world.upsert_from_observation(
                obs,
                kind=str(obs.payload.get("kind_hint", "rf_device")),
                confidence=obs.confidence,
            )
        if obs.type is ObservationType.CSI_ACTIVITY:
            return self.world.upsert_from_observation(obs, kind="presence_region", confidence=obs.confidence)
        return self.world.upsert_from_observation(obs, kind="unknown", confidence=obs.confidence)
