from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

from adapters.base import Adapter
from protocol import validate


@dataclass
class World:
    entities: dict[str, dict[str, Any]] = field(default_factory=dict)

    def observe(self, observation: dict[str, Any]) -> dict[str, Any]:
        obs = validate(observation)
        entity_id = obs["id"]
        entity = self.entities.setdefault(entity_id, {"id": entity_id, "data": {}})
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


def run_adapter(adapter: Adapter, world: World, conn=None, on_observation: Callable[[dict[str, Any]], None] | None = None) -> None:
    from db import save

    for observation in adapter.observations():
        world.observe(observation)
        if conn is not None:
            save(conn, observation)
        if on_observation is not None:
            on_observation(observation)
