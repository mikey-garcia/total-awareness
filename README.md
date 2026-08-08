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
