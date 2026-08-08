from __future__ import annotations

import sqlite3
from pathlib import Path

from total_awareness.core.models import Entity, Observation


SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    ts TEXT NOT NULL,
    json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    json TEXT NOT NULL
);
"""


class SQLiteStore:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.conn = sqlite3.connect(self.path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def append_observation(self, obs: Observation) -> None:
        self.conn.execute(
            "INSERT INTO observations(id, ts, json) VALUES (?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET ts=excluded.ts, json=excluded.json",
            (str(obs.id), obs.timestamp.isoformat(), obs.model_dump_json()),
        )
        self.conn.commit()

    def save_entity(self, entity: Entity) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO entities(id, json) VALUES (?, ?)",
            (entity.id, entity.model_dump_json()),
        )
        self.conn.commit()

    def load_observations(self) -> list[Observation]:
        rows = self.conn.execute("SELECT json FROM observations ORDER BY seq").fetchall()
        return [Observation.model_validate_json(row[0]) for row in rows]

    def load_entities(self) -> list[Entity]:
        rows = self.conn.execute("SELECT json FROM entities ORDER BY id").fetchall()
        return [Entity.model_validate_json(row[0]) for row in rows]

    def close(self) -> None:
        self.conn.close()
