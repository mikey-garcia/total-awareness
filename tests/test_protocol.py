from total_awareness.protocol import message, validate


def test_message_is_plain_json_shape():
    value = message(sensor="pi1.wifi", type="wifi_device", id="wifi:aa", data={"rssi": -57})
    assert set(value) == {"time", "sensor", "type", "id", "data"}
    assert validate(value) is value


def test_protocol_rejects_surprise_top_level_fields():
    value = message(sensor="pi1.wifi", type="wifi_device")
    value["mystery"] = True
    try:
        validate(value)
    except ValueError:
        pass
    else:
        raise AssertionError("protocol accepted an undocumented top-level field")
