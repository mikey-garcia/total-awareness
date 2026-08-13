from core import World
from protocol import observation


def test_world_owns_observation_and_snapshot_behavior():
    world = World()
    world.observe(observation("test", "b", {"value": 1}, "2026-08-09T00:00:00+00:00"))
    world.observe(observation("test", "a", {"value": 2}, "2026-08-09T00:00:01+00:00"))
    assert [entity["id"] for entity in world.snapshot()] == ["a", "b"]
