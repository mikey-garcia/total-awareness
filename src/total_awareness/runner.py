from __future__ import annotations

from total_awareness.collectors.base import Collector
from total_awareness.fusion.engine import FusionEngine
from total_awareness.storage.sqlite import SQLiteStore


async def run_collector(collector: Collector, store: SQLiteStore | None = None) -> FusionEngine:
    """Run a collector; persistence is optional instead of part of ingestion itself."""
    engine = FusionEngine()
    async for obs in collector.observations():
        if store is not None:
            store.append_observation(obs)
        entity = engine.ingest(obs)
        if store is not None:
            store.save_entity(entity)
    return engine
