from total_awareness.core import World
from total_awareness.db import connect, load, save
from total_awareness.hardware.kismet import normalize


def _wifi(rssi: int):
    value = normalize(
        {
            "mac": "AA:BB:CC:DD:EE:FF",
            "type": "AP",
            "ssid": "lab",
            "vendor": "Example",
            "channel": 6,
            "signal_dbm": rssi,
        }
    )
    assert value is not None
    return value


def test_kismet_updates_one_stable_entity():
    world = World()
    first = world.observe(_wifi(-70))
    second = world.observe(_wifi(-51))

    assert first["id"] == second["id"] == "wifi:aa:bb:cc:dd:ee:ff"
    assert len(world.entities) == 1
    assert second["data"]["kind"] == "access_point"
    assert second["data"]["rssi"] == -51
    assert second["data"]["name"] == "lab"


def test_database_preserves_observation_order(tmp_path):
    conn = connect(tmp_path / "events.db")
    first = _wifi(-70)
    second = _wifi(-51)
    save(conn, first)
    save(conn, second)

    assert load(conn) == [first, second]
    conn.close()


def test_recording_and_replay_do_not_change_world_state(tmp_path):
    observations = [_wifi(-70), _wifi(-51)]
    direct = World.replay(observations)

    conn = connect(tmp_path / "events.db")
    for observation in observations:
        save(conn, observation)
    recorded = World.replay(load(conn))
    conn.close()

    assert recorded.entities == direct.entities
