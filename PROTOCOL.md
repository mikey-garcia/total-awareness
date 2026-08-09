# Total Awareness protocol

Everything entering Total Awareness is one JSON object.

```json
{
  "time": "2026-08-09T14:00:00Z",
  "sensor": "pi1.wifi",
  "type": "wifi_device",
  "id": "wifi:aa:bb:cc:dd:ee:ff",
  "data": {
    "rssi": -57,
    "channel": 6,
    "name": "example"
  }
}
```

Only five top-level keys exist:

- `time`: UTC ISO-8601 timestamp.
- `sensor`: who measured it. Hardware names should be boring, e.g. `pi1.wifi`, `pi2.ble`, `phone.pose`.
- `type`: what was measured, e.g. `wifi_device`, `ble_device`, `camera`, `pose`, `csi_activity`.
- `id`: stable subject identity when known; `null` when unknown.
- `data`: sensor-specific facts. This is the only intentionally flexible field.

## Rule

Hardware knows hardware. Core knows this protocol. Neither side knows the other's internals.

```text
Kismet ─┐
BLE ────┤
CSI ────┼─> {time,sensor,type,id,data} ─> DB ─> world model ─> API/HUD
Camera ─┤
GPS ────┘
```

Adapters should be small functions that turn vendor/tool output into this dictionary. Do not add a framework, inheritance hierarchy, message bus, or new protocol unless the simple dictionary is proven insufficient.

The database stores observations losslessly. Fusion/world logic derives entities from observations. Derived entities never overwrite observation history.
