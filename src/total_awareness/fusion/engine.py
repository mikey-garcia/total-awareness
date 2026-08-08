from __future__ import annotations

from total_awareness.core.models import Observation, ObservationType
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

    def ingest(self, obs: Observation):
        if obs.type is ObservationType.POSE:
            return self.world.upsert_from_observation(obs, kind="observer", confidence=1.0)
        if obs.type is ObservationType.VISUAL_DETECTION:
            return self.world.upsert_from_observation(
                obs,
                kind=str(obs.payload.get("class", "unknown")),
                confidence=obs.confidence,
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
