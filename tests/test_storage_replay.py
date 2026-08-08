from pathlib import Path

from total_awareness.core.models import Modality, Observation, ObservationType
from total_awareness.fusion.engine import FusionEngine
from total_awareness.storage.replay import replay_database
from total_awareness.storage.sqlite import SQLiteStore


def test_replay_is_deterministic(tmp_path: Path):
    path = tmp_path / "events.db"
    store = SQLiteStore(path)
    observations = [
        Observation(
            sensor_id="wifi0",
            modality=Modality.WIFI,
            type=ObservationType.RF_DETECTION,
            subject_key="wifi:aa",
            confidence=0.8,
        ),
        Observation(
            sensor_id="wifi0",
            modality=Modality.WIFI,
            type=ObservationType.RF_DETECTION,
            subject_key="wifi:aa",
            confidence=0.8,
        ),
    ]
    original = FusionEngine()
    for obs in observations:
        store.append_observation(obs)
        original.ingest(obs)
    store.close()

    replayed = replay_database(path)
    a = original.world.entities["E0001"]
    b = replayed.world.entities["E0001"]
    assert a.confidence == b.confidence
    assert [e.observation_id for e in a.evidence] == [e.observation_id for e in b.evidence]
