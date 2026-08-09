from pathlib import Path


def test_runtime_database_is_not_committed():
    assert not Path("awareness.db").exists()
