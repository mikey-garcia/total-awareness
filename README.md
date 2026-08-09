# Total Awareness

Small Python experiment for taking sensor observations, keeping the latest state for each observed entity, optionally recording observations to SQLite, and showing the result in a browser HUD.

Right now the real input is Kismet Wi-Fi device data. The rest is intentionally small.

## Layout

```text
src/
├── app.py          # FastAPI + HUD
├── cli.py          # commands
├── core.py         # in-memory World
├── db.py           # SQLite record/replay
├── protocol.py     # observation dictionaries
├── wire.py         # tiny binary packet framing
├── hardware/
│   └── kismet.py   # Kismet -> observation adapter
└── static/

demos/              # sample inputs/scenarios
tests/
```

## Observation format

Observations are plain dictionaries with exactly five top-level fields:

```json
{
  "time": "2026-08-09T12:00:00+00:00",
  "sensor": "pi1.wifi",
  "type": "wifi_device",
  "id": "wifi:aa:bb:cc:dd:ee:ff",
  "data": {"rssi": -51, "channel": 6}
}
```

`hardware/kismet.py` converts Kismet device dictionaries into that shape. `World.observe()` keeps the latest data for each stable ID. `db.py` can record the same observations and replay them later.

`wire.py` is only a small binary frame for future Pi/ESP/FPGA transport: magic + version + message type + payload length + payload. Sensor-specific payload structs will be added when there is an actual sensor that needs them.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,server]'
pytest

ta demo-kismet demos/kismet_devices.json --record
ta serve --db awareness.db --host 0.0.0.0
```

The HUD is then available on port 8000. On the same LAN, another device can open the host machine's LAN IP on that port.
