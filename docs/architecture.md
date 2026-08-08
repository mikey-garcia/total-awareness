# Architecture

## Invariants

1. Observations are immutable facts produced by a named sensor.
2. Entities are hypotheses and may be merged, split, reclassified, or deleted by later fusion logic.
3. Every entity claim must retain provenance to the observations that support it.
4. Raw event logs must be replayable through newer fusion algorithms.
5. Collectors never know about UI or entity identity decisions.
6. Sensor-specific quirks stop at the adapter boundary.

## Planned adapters

- Kismet: 802.11 device/frame metadata and RSSI
- BlueZ: BLE advertisements and manufacturer/service fingerprints
- Nexmon CSI: channel state measurements
- Phone bridge: GPS/IMU/camera detections
- SDR: SigMF-compatible capture/event references
- FPGA: timestamped high-rate feature stream, only after profiling proves value

## Fusion roadmap

V0 deliberately uses stable subject keys and conservative confidence accumulation. Next steps:

1. observer pose history
2. RF track localization from measurements along observer trajectory
3. visual bearing tracks
4. candidate RF ↔ visual associations, never silent identity merges
5. probabilistic association / factor-graph backend
6. observability field derived from sensor pose/FOV/capabilities
7. CSI presence regions and cross-modal reacquisition

The schema and replay log are intended to survive all of those algorithm swaps.
