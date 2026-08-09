from protocol import REQUIRED


def test_protocol_has_only_five_top_level_fields():
    assert REQUIRED == {"time", "sensor", "type", "id", "data"}
