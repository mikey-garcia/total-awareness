from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from protocol import observation


def _get(device: dict[str, Any], *names: str):
    for name in names:
        value: Any = device
        for part in name.split("/"):
            if not isinstance(value, dict) or part not in value:
                value = None
                break
            value = value[part]
        if value not in (None, ""):
            return value
    return None


def _normalize(device: dict[str, Any], sensor: str) -> dict[str, Any] | None:
    mac = _get(device, "kismet.device.base.macaddr", "macaddr", "mac")
    if not mac:
        return None

    kind = str(_get(device, "kismet.device.base.type", "type") or "").lower()
    data = {
        "kind": "access_point" if kind in {"wifi ap", "ap", "access_point"} else "rf_device",
        "name": _get(device, "kismet.device.base.name", "name", "ssid"),
        "vendor": _get(device, "kismet.device.base.manuf", "manufacturer", "vendor"),
        "channel": _get(device, "kismet.device.base.channel", "channel"),
        "frequency_khz": _get(device, "kismet.device.base.frequency", "frequency_khz", "frequency"),
        "rssi": _get(device, "kismet.device.base.signal/kismet.common.signal.last_signal", "signal/kismet.common.signal.last_signal", "last_signal", "signal_dbm"),
    }
    return observation(
        sensor=sensor,
        type="wifi_device",
        id=f"wifi:{str(mac).lower()}",
        data={key: value for key, value in data.items() if value not in (None, "")},
    )


class KismetAdapter:
    def __init__(self, devices: Iterable[dict[str, Any]], sensor: str = "pi1.wifi"):
        self.devices = devices
        self.sensor = sensor

    def observations(self):
        for device in self.devices:
            obs = _normalize(device, self.sensor)
            if obs is not None:
                yield obs
