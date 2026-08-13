from protocol import REQUIRED


def test_protocol_has_only_four_top_level_fields():
    assert REQUIRED == {"time", "sensor", "id", "data"}
