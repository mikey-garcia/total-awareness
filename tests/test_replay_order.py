from pathlib import Path

from total_awareness.collectors.simulated import SimulatedCollector
from total_awareness.runner import run_collector
from total_awareness.storage.replay import replay_database
from total_awareness.storage.sqlite import SQLiteStore

import asyncio


def test_simulation_replay_preserves_entity_assignment(tmp_path: Path):
    scenario = Path(__file__).parents[1] / "scenarios" / "hallway.yaml"
    db = tmp_path / "scenario.db"
    store = SQLiteStore(db)
    try:
        original = asyncio.run(run_collector(SimulatedCollector(scenario), store))
    finally:
        store.close()
    replayed = replay_database(db)
    assert {
        key: value for key, value in original.world.subject_index.items()
    } == replayed.world.subject_index
