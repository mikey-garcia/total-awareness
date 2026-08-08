from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from total_awareness.core.models import Observation


class Collector(ABC):
    @abstractmethod
    async def observations(self) -> AsyncIterator[Observation]:
        raise NotImplementedError
