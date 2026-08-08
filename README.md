# Total Awareness

A portable multimodal world-modeling research platform for fusing passive sensor observations into explainable hypotheses about nearby physical and RF entities.

The core rule is simple: **observations are facts; entities are hypotheses**. Raw observations are immutable and replayable. Every entity state keeps provenance back to the evidence that produced it.

## Current scaffold

- normalized observation schema for RF, vision, pose, CSI, and generic sensors
- asynchronous observation bus
- simulated collector with deterministic scenarios
- lightweight fusion engine for track creation/update and RF/vision association hooks
- explainable persistent world model
- SQLite observation/event log
- deterministic replay
- CLI (`ta simulate`, `ta replay`, `ta entities`, `ta explain`)
- optional FastAPI world-model endpoint
- tests covering model serialization, persistence, and deterministic fusion

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,server]'
pytest

ta simulate scenarios/hallway.yaml --db awareness.db
ta entities --db awareness.db
ta explain E0001 --db awareness.db
```

## Architecture

```text
collectors -> ObservationBus -> Recorder -> FusionEngine -> WorldModel
                    |                              |
                    +---------- raw log -----------+
                                                   |
                                             API / HUD
```

Collectors are adapters. Kismet, BlueZ, Nexmon CSI, phone telemetry, SDRs, cameras, and future FPGA frontends should all emit the same `Observation` envelope.

## Safety / scope

The platform is designed for passive situational awareness, controlled experiments, and authorized security research. Internet-facing enrichment should only be used on infrastructure you own or are authorized to assess.


## Mobile HUD

Install the server extra and start the HUD:

```powershell
pip install -e ".[server,dev]"
ta serve --db awareness.db
```

On the same Windows machine, open `http://127.0.0.1:8000`. To use your phone, keep it on the same LAN and open `http://<YOUR-PC-LAN-IP>:8000`. Windows Firewall may ask you to allow Python on private networks.

For a live synthetic demo, leave `ta serve` running and start the simulator in a second PowerShell window:

```powershell
ta simulate scenarios/hallway.yaml --db awareness.db --realtime
```

The HUD reads the same persisted observation stream as the CLI. It receives world-model snapshots over `/ws`, shows entities relative to the observer, and lets you inspect each entity's underlying evidence. No frontend build toolchain is required.
