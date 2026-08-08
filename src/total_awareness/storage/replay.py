from __future__ import annotations

from pathlib import Path

from total_awareness.fusion.engine import FusionEngine
from .sqlite import SQLiteStore


def replay_database(path: Path | str) -> FusionEngine:
    store = SQLiteStore(path)
    engine = FusionEngine()
    for observation in store.load_observations():
        engine.ingest(observation)
    store.close()
    return engine
