import sqlite3

import pytest

from total_awareness import db
from total_awareness.core import World, ingest, replay
from total_awareness.protocol import message, validate


def observation(**overrides):
    values = {
        "sensor": "test:sensor",
        "type": "wifi.device",
        "id": "wifi:aa:bb:cc:dd:ee:ff",
        "data": {"signal_dbm": -55},
        "time": "2026-08-09T12:00:00+00:00",
    }
    values.update(overrides)
    return message(**values)


def test_protocol_is_exactly_five_keys():
    obs = observation()
    assert set(obs) == {"time", "sensor", "type", "id", "data"}
    assert validate(obs) is obs


def test_protocol_rejects_extra_keys():
    obs = observation()
    obs["surprise"] = True
    with pytest.raises(ValueError):
        validate(obs)


def test_ingest_updates_stable_entity():
    world = World()
    ingest(world, observation(data={"signal_dbm": -70}))
    entity = ingest(world, observation(data={"signal_dbm": -45, "channel": 6}))

    assert len(world.entities) == 1
    assert entity["data"] == {"signal_dbm": -45, "channel": 6}


def test_db_round_trip_preserves_observation_order():
    conn = sqlite3.connect(":memory:")
    conn.executescript(db.SCHEMA)
    first = observation(id="wifi:first")
    second = observation(id="wifi:second", time="2026-08-09T12:00:01+00:00")

    db.save(conn, first)
    db.save(conn, second)

    assert db.load(conn) == [first, second]


def test_recording_does_not_change_world_state():
    observations = [
        observation(data={"signal_dbm": -70}),
        observation(data={"signal_dbm": -42, "channel": 11}),
    ]

    direct = replay(observations)

    conn = sqlite3.connect(":memory:")
    conn.executescript(db.SCHEMA)
    for obs in observations:
        db.save(conn, obs)
    recorded = replay(db.load(conn))

    assert recorded.entities == direct.entities
