from total_awareness.db import connect, load_observations, store_observation
from total_awareness.protocol import message


def test_protocol_observations_round_trip_in_order(tmp_path):
    conn = connect(tmp_path / "awareness.db")
    first = message(sensor="pi1.wifi", type="wifi_device", id="wifi:aa", data={"rssi": -42}, time="2026-08-09T18:00:00+00:00")
    second = message(sensor="pi1.wifi", type="wifi_device", id="wifi:bb", data={"rssi": -55}, time="2026-08-09T18:00:01+00:00")

    try:
        store_observation(conn, first)
        store_observation(conn, second)
        assert load_observations(conn) == [first, second]
    finally:
        conn.close()


def test_store_rejects_non_protocol_dict(tmp_path):
    conn = connect(tmp_path / "awareness.db")
    try:
        try:
            store_observation(conn, {"sensor": "pi1.wifi"})
        except ValueError:
            pass
        else:
            raise AssertionError("invalid observation should not be stored")

        assert load_observations(conn) == []
    finally:
        conn.close()
