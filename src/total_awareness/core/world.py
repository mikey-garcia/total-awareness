from __future__ import annotations

from .models import Entity, Evidence, Observation


class WorldModel:
    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.observations: dict[str, Observation] = {}
        self.subject_index: dict[str, str] = {}
        self._next_id = 1

    def remember(self, obs: Observation) -> None:
        self.observations[str(obs.id)] = obs

    def allocate_entity_id(self) -> str:
        entity_id = f"E{self._next_id:04d}"
        self._next_id += 1
        return entity_id

    def upsert_from_observation(self, obs: Observation, *, kind: str, confidence: float) -> Entity:
        self.remember(obs)
        entity_id = self.subject_index.get(obs.subject_key or "")
        if entity_id is None:
            entity_id = self.allocate_entity_id()
            entity = Entity(
                id=entity_id,
                kind=kind,
                confidence=confidence,
                position=obs.position,
                aliases={obs.subject_key} if obs.subject_key else set(),
                evidence=[],
                first_seen=obs.timestamp,
                last_seen=obs.timestamp,
            )
            self.entities[entity_id] = entity
            if obs.subject_key:
                self.subject_index[obs.subject_key] = entity_id
        else:
            entity = self.entities[entity_id]
            entity.last_seen = obs.timestamp
            entity.confidence = 1.0 - ((1.0 - entity.confidence) * (1.0 - confidence))
            if obs.position is not None:
                entity.position = obs.position

        entity.evidence.append(
            Evidence(observation_id=obs.id, weight=obs.confidence, reason=obs.type.value)
        )
        return entity

    def explain(self, entity_id: str) -> tuple[Entity, list[Observation]]:
        entity = self.entities[entity_id]
        obs = [self.observations[str(e.observation_id)] for e in entity.evidence]
        return entity, obs
