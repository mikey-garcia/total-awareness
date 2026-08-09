from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from total_awareness.protocol import validate


@dataclass
class World:
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)


def ingest(world: World, observation: dict[str, Any]) -> dict[str, Any]:
    obs = validate(observation)
    entity_id = obs["id"] or f"{obs['type']}:{len(world.entities) + 1}"
    current = world.entities.get(entity_id, {"id": entity_id, "type": obs["type"], "data": {}})
    current["type"] = obs["type"]
    current["data"].update(obs["data"])
    current["last_seen"] = obs["time"]
    current["sensor"] = obs["sensor"]
    world.entities[entity_id] = current
    return current


def replay(observations: list[dict[str, Any]]) -> World:
    world = World()
    for observation in observations:
        ingest(world, observation)
    return world
