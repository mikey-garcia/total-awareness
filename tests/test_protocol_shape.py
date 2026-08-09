from protocol import message


def test_sensor_message_is_obvious():
    assert list(message(sensor="x", type="y")) == ["time", "sensor", "type", "id", "data"]
