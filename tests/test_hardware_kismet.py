from adapters.kismet import KismetAdapter
from protocol import validate


def test_kismet_adapter_produces_protocol_observations():
    adapter = KismetAdapter([{"mac": "AA:BB:CC:DD:EE:FF", "type": "AP", "ssid": "demo", "signal_dbm": -51}])
    value = next(iter(adapter.observations()))
    validate(value)
    assert value["id"] == "wifi:aa:bb:cc:dd:ee:ff"
    assert value["data"]["kind"] == "access_point"
    assert value["data"]["rssi"] == -51
