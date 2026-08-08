from pathlib import Path

from total_awareness.server.app import _snapshot
from total_awareness.storage.sqlite import SQLiteStore


def test_snapshot_counts_and_observer(tmp_path: Path):
    # Empty DB is still a valid live-HUD state.
    db = tmp_path / "empty.db"
    store = SQLiteStore(db)
    store.close()
    snapshot = _snapshot(db)
    assert snapshot["entities"] == []
    assert snapshot["observer"] is None
    assert snapshot["counts"] == {"total": 0, "cameras": 0, "rf": 0, "unknown": 0}
