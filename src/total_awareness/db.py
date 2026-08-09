from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from total_awareness.protocol import validate


SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    json TEXT NOT NULL
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(Path(path))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def save(conn: sqlite3.Connection, observation: dict) -> None:
    conn.execute("INSERT INTO observations(json) VALUES (?)", (json.dumps(validate(observation)),))
    conn.commit()


def load(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT json FROM observations ORDER BY seq").fetchall()
    return [validate(json.loads(row[0])) for row in rows]
