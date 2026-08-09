from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from protocol import validate

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT NOT NULL,
    sensor TEXT NOT NULL,
    type TEXT NOT NULL,
    id TEXT,
    data TEXT NOT NULL
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn


def save(conn: sqlite3.Connection, obs: dict[str, Any]) -> None:
    obs = validate(obs)
    conn.execute(
        "INSERT INTO observations(time, sensor, type, id, data) VALUES (?, ?, ?, ?, ?)",
        (obs["time"], obs["sensor"], obs["type"], obs["id"], json.dumps(obs["data"])),
    )
    conn.commit()


def load(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("SELECT time, sensor, type, id, data FROM observations ORDER BY seq").fetchall()
    return [
        {"time": row[0], "sensor": row[1], "type": row[2], "id": row[3], "data": json.loads(row[4])}
        for row in rows
    ]
