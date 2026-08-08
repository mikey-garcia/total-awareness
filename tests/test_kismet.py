from total_awareness.collectors.kismet import device_to_observation
from total_awareness.fusion.engine import FusionEngine


def test_kismet_device_normalization_and_persistence():
    first = device_to_observation({
        "mac": "AA:BB:CC:DD:EE:FF", "type": "AP", "ssid": "lab",
        "vendor": "Example", "channel": "6", "signal_dbm": -70,
    })
    second = device_to_observation({
        "mac": "AA:BB:CC:DD:EE:FF", "type": "AP", "ssid": "lab",
        "vendor": "Example", "channel": "6", "signal_dbm": -51,
    })
    assert first is not None and second is not None
    engine = FusionEngine()
    a = engine.ingest(first)
    b = engine.ingest(second)
    assert a.id == b.id
    assert b.kind == "access_point"
    assert b.attributes["signal_dbm"] == -51
    assert b.attributes["name"] == "lab"
