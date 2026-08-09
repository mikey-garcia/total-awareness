"""Tiny SQLite persistence for the five-key Total Awareness protocol."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from total_awareness.protocol import validate

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    json TEXT NOT NULL
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    """Open the database and ensure the minimal schema exists."""
    conn = sqlite3.connect(Path(path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def store_observation(conn: sqlite3.Connection, observation: dict[str, Any]) -> None:
    """Persist one validated protocol dictionary."""
    validate(observation)
    conn.execute(
        "INSERT INTO observations(json) VALUES (?)",
        (json.dumps(observation, separators=(",", ":"), sort_keys=True),),
    )
    conn.commit()


def load_observations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    """Load observations in insertion order."""
    rows = conn.execute("SELECT json FROM observations ORDER BY seq").fetchall()
    return [validate(json.loads(row[0])) for row in rows]
