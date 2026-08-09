from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class Adapter(Protocol):
    def observations(self) -> Iterable[dict]: ...
