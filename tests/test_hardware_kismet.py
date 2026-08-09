from hardware.kismet import normalize
from protocol import validate


def test_kismet_normalizes_to_protocol():
    value = normalize({"mac": "AA:BB:CC:DD:EE:FF", "type": "AP", "ssid": "demo", "signal_dbm": -51})
    assert value is not None
    validate(value)
    assert value["type"] == "wifi_device"
    assert value["id"] == "wifi:aa:bb:cc:dd:ee:ff"
    assert value["data"]["rssi"] == -51
