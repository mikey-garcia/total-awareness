from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from .models import Observation


class ObservationBus:
    def __init__(self, maxsize: int = 4096) -> None:
        self._queue: asyncio.Queue[Observation] = asyncio.Queue(maxsize=maxsize)

    async def publish(self, observation: Observation) -> None:
        await self._queue.put(observation)

    async def stream(self) -> AsyncIterator[Observation]:
        while True:
            yield await self._queue.get()
