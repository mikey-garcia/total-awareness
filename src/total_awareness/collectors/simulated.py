from __future__ import annotations

import asyncio
import math
import random
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from total_awareness.core.models import Modality, Observation, ObservationType, Vec3
from .base import Collector


def _distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b, strict=True)))


def _bearing_deg(observer: list[float], target: list[float]) -> float:
    return math.degrees(math.atan2(target[1] - observer[1], target[0] - observer[0])) % 360.0


class SimulatedCollector(Collector):
    def __init__(self, scenario_path: Path, realtime: bool = False) -> None:
        self.scenario_path = scenario_path
        self.realtime = realtime

    async def observations(self) -> AsyncIterator[Observation]:
        config = yaml.safe_load(self.scenario_path.read_text())
        rng = random.Random(config.get("seed", 0))
        steps = int(config.get("steps", 20))
        dt = float(config.get("dt_s", 0.25))
        start = list(map(float, config["observer"]["start"]))
        velocity = list(map(float, config["observer"].get("velocity", [0, 0, 0])))
        t0 = datetime.now(timezone.utc)

        for step in range(steps):
            observer = [start[i] + velocity[i] * dt * step for i in range(3)]
            timestamp = t0 + timedelta(seconds=dt * step)
            yield Observation(
                timestamp=timestamp,
                sensor_id="sim:pose",
                modality=Modality.POSE,
                type=ObservationType.POSE,
                subject_key="observer:self",
                position=Vec3(x=observer[0], y=observer[1], z=observer[2]),
                payload={"heading_deg": 0.0},
            )

            for entity in config.get("entities", []):
                target = list(map(float, entity["position"]))
                dist = max(_distance(observer, target), 0.5)
                rf_id = entity.get("rf_id")
                if rf_id:
                    # Crude log-distance model plus deterministic noise. Replace with calibrated model later.
                    rssi = -35.0 - 20.0 * math.log10(dist) + rng.gauss(0.0, 1.5)
                    yield Observation(
                        timestamp=timestamp,
                        sensor_id="sim:wifi",
                        modality=Modality.WIFI,
                        type=ObservationType.RF_DETECTION,
                        subject_key=rf_id,
                        confidence=0.85,
                        payload={
                            "rssi_dbm": rssi,
                            "ground_truth_entity": entity["id"],
                            "kind_hint": entity["kind"],
                        },
                    )

                if entity["kind"] == "camera" and dist < 20.0:
                    yield Observation(
                        timestamp=timestamp,
                        sensor_id="sim:vision",
                        modality=Modality.VISION,
                        type=ObservationType.VISUAL_DETECTION,
                        subject_key=f"vision:{entity['id']}",
                        bearing_deg=_bearing_deg(observer, target) + rng.gauss(0.0, 0.8),
                        confidence=0.95,
                        payload={
                            "class": "camera",
                            "ground_truth_entity": entity["id"],
                            "range_hint_m": dist + rng.gauss(0.0, 0.5),
                        },
                    )
            if self.realtime:
                await asyncio.sleep(dt)
