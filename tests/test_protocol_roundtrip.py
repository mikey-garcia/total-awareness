import json
from protocol import message, validate


def test_protocol_round_trips_as_json():
    original = message(sensor="pi1.wifi", id="wifi:aa", data={"rssi": -42})
    restored = json.loads(json.dumps(original))
    assert validate(restored) == original
