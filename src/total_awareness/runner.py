from __future__ import annotations

from total_awareness.collectors.base import Collector
from total_awareness.fusion.engine import FusionEngine
from total_awareness.storage.sqlite import SQLiteStore


async def run_collector(collector: Collector, store: SQLiteStore) -> FusionEngine:
    engine = FusionEngine()
    async for obs in collector.observations():
        store.append_observation(obs)
        entity = engine.ingest(obs)
        store.save_entity(entity)
    return engine
