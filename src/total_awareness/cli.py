from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from total_awareness.collectors.simulated import SimulatedCollector
from total_awareness.runner import run_collector
from total_awareness.storage.replay import replay_database
from total_awareness.storage.sqlite import SQLiteStore

app = typer.Typer(help="Total Awareness research CLI")
console = Console()


def _entity_table(entities):
    table = Table("Entity", "Kind", "Confidence", "Position", "Evidence")
    for entity in sorted(entities, key=lambda e: e.id):
        pos = "-" if entity.position is None else f"({entity.position.x:.1f}, {entity.position.y:.1f}, {entity.position.z:.1f})"
        table.add_row(entity.id, entity.kind, f"{entity.confidence:.1%}", pos, str(len(entity.evidence)))
    return table


@app.command()
def simulate(
    scenario: Path,
    db: Path = typer.Option(Path("awareness.db"), help="SQLite event log"),
    realtime: bool = typer.Option(False, help="Sleep between simulated timesteps"),
) -> None:
    """Run a deterministic synthetic scenario through the real ingestion/fusion path."""
    store = SQLiteStore(db)
    try:
        engine = asyncio.run(run_collector(SimulatedCollector(scenario, realtime=realtime), store))
    finally:
        store.close()
    console.print(_entity_table(engine.world.entities.values()))


@app.command()
def replay(db: Path = typer.Option(Path("awareness.db"))) -> None:
    """Recompute world state only from immutable stored observations."""
    engine = replay_database(db)
    console.print(_entity_table(engine.world.entities.values()))


@app.command()
def entities(db: Path = typer.Option(Path("awareness.db"))) -> None:
    store = SQLiteStore(db)
    try:
        console.print(_entity_table(store.load_entities()))
    finally:
        store.close()


@app.command()
def explain(entity_id: str, db: Path = typer.Option(Path("awareness.db"))) -> None:
    engine = replay_database(db)
    entity, observations = engine.world.explain(entity_id)
    console.print(f"[bold]{entity.id}[/bold] {entity.kind} confidence={entity.confidence:.1%}")
    for obs in observations:
        console.print(
            f"- {obs.timestamp.isoformat()} {obs.modality.value}/{obs.type.value} "
            f"sensor={obs.sensor_id} confidence={obs.confidence:.2f} id={obs.id}"
        )

if __name__ == "__main__":
    app()
