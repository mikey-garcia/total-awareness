from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from total_awareness.protocol import validate


@dataclass
class World:
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)

    def observe(self, observation: dict[str, Any]) -> dict[str, Any]:
        obs = validate(observation)
        entity_id = obs["id"] or f"{obs['type']}:{len(self.entities) + 1}"
        entity = self.entities.setdefault(
            entity_id,
            {"id": entity_id, "type": obs["type"], "data": {}},
        )
        entity["type"] = obs["type"]
        entity["data"].update(obs["data"])
        entity["last_seen"] = obs["time"]
        entity["sensor"] = obs["sensor"]
        return entity

    def snapshot(self) -> list[dict[str, Any]]:
        return sorted(self.entities.values(), key=lambda entity: entity["id"])

    @classmethod
    def replay(cls, observations: Iterable[dict[str, Any]]) -> "World":
        world = cls()
        for observation in observations:
            world.observe(observation)
        return world
