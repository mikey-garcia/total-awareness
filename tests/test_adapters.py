import sqlite3
from core import World, run_adapter
from db import SCHEMA, load
from protocol import observation


class FakeAdapter:
    def observations(self):
        yield observation("fake", "one", {"value": 1})
        yield observation("fake", "two", {"value": 2})


def test_run_adapter_updates_world():
    world = World(); run_adapter(FakeAdapter(), world)
    assert set(world.entities) == {"one", "two"}


def test_run_adapter_optionally_records():
    world = World(); conn = sqlite3.connect(":memory:"); conn.executescript(SCHEMA)
    run_adapter(FakeAdapter(), world, conn)
    assert [obs["id"] for obs in load(conn)] == ["one", "two"]


def test_run_adapter_emits_each_observation():
    world = World(); seen = []
    run_adapter(FakeAdapter(), world, on_observation=seen.append)
    assert [obs["id"] for obs in seen] == ["one", "two"]
