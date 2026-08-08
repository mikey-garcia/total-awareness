from __future__ import annotations

import asyncio
import base64
import json
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from total_awareness.collectors.base import Collector
from total_awareness.core.models import Modality, Observation, ObservationType


def _dig(obj: dict[str, Any], *paths: str, default=None):
    for path in paths:
        cur: Any = obj
        ok = True
        for part in path.split('/'):
            if not isinstance(cur, dict) or part not in cur:
                ok = False
                break
            cur = cur[part]
        if ok:
            return cur
    return default


def device_to_observation(device: dict[str, Any], *, sensor_id: str = "kismet") -> Observation | None:
    mac = _dig(device, "kismet.device.base.macaddr", "macaddr", "mac")
    if not mac:
        return None
    mac = str(mac).lower()
    signal = _dig(
        device,
        "kismet.device.base.signal/kismet.common.signal.last_signal",
        "signal/kismet.common.signal.last_signal",
        "last_signal",
        "signal_dbm",
    )
    payload = {
        "kind_hint": "access_point" if str(_dig(device, "kismet.device.base.type", "type", default="")).lower() in {"wifi ap", "ap", "access_point"} else "rf_device",
        "name": _dig(device, "kismet.device.base.name", "name", "ssid"),
        "manufacturer": _dig(device, "kismet.device.base.manuf", "manufacturer", "vendor"),
        "channel": _dig(device, "kismet.device.base.channel", "channel"),
        "frequency_khz": _dig(device, "kismet.device.base.frequency", "frequency_khz", "frequency"),
        "signal_dbm": signal,
        "phy": _dig(device, "kismet.device.base.phyname", "phy"),
        "device_type": _dig(device, "kismet.device.base.type", "type"),
    }
    payload = {k: v for k, v in payload.items() if v is not None and v != ""}
    return Observation(
        timestamp=datetime.now(timezone.utc),
        sensor_id=sensor_id,
        modality=Modality.WIFI,
        type=ObservationType.RF_DETECTION,
        subject_key=f"wifi:{mac}",
        confidence=0.95,
        payload=payload,
    )


class KismetCollector(Collector):
    """Poll Kismet's device-view REST endpoint and emit normalized observations."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:2501",
        *,
        poll_interval: float = 2.0,
        username: str | None = None,
        password: str | None = None,
        sensor_id: str = "kismet:local",
        endpoint: str = "/devices/views/all/devices.json",
    ) -> None:
        self.url = base_url.rstrip("/") + endpoint
        self.poll_interval = poll_interval
        self.username = username
        self.password = password
        self.sensor_id = sensor_id
        self._last_fingerprint: dict[str, tuple[Any, ...]] = {}

    def _fetch(self) -> list[dict[str, Any]]:
        req = Request(self.url, headers={"Accept": "application/json"})
        if self.username is not None and self.password is not None:
            token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            req.add_header("Authorization", f"Basic {token}")
        with urlopen(req, timeout=5) as response:  # noqa: S310 - user-selected local Kismet endpoint
            data = json.load(response)
        if isinstance(data, dict):
            data = data.get("devices", data.get("results", []))
        if not isinstance(data, list):
            raise ValueError("Kismet endpoint did not return a device list")
        return [d for d in data if isinstance(d, dict)]

    async def observations(self) -> AsyncIterator[Observation]:
        while True:
            devices = await asyncio.to_thread(self._fetch)
            for device in devices:
                obs = device_to_observation(device, sensor_id=self.sensor_id)
                if obs is None or obs.subject_key is None:
                    continue
                fp = (
                    obs.payload.get("signal_dbm"), obs.payload.get("channel"),
                    obs.payload.get("name"), obs.payload.get("manufacturer"),
                )
                if self._last_fingerprint.get(obs.subject_key) == fp:
                    continue
                self._last_fingerprint[obs.subject_key] = fp
                yield obs
            await asyncio.sleep(self.poll_interval)


class KismetDemoCollector(Collector):
    """Replay Kismet-shaped snapshots without requiring Kismet or RF hardware."""

    def __init__(self, path: Path | str, *, realtime: bool = False, sensor_id: str = "kismet:demo") -> None:
        self.path = Path(path)
        self.realtime = realtime
        self.sensor_id = sensor_id

    async def observations(self) -> AsyncIterator[Observation]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        snapshots = data.get("snapshots", data) if isinstance(data, dict) else data
        if not isinstance(snapshots, list):
            raise ValueError("demo file must contain a list of snapshots")
        for snapshot in snapshots:
            devices = snapshot.get("devices", snapshot) if isinstance(snapshot, dict) else snapshot
            if not isinstance(devices, list):
                continue
            for device in devices:
                if isinstance(device, dict):
                    obs = device_to_observation(device, sensor_id=self.sensor_id)
                    if obs is not None:
                        yield obs
            if self.realtime:
                await asyncio.sleep(float(snapshot.get("delay_s", 1.0)) if isinstance(snapshot, dict) else 1.0)
