from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from total_awareness.collectors.kismet import KismetCollector, KismetDemoCollector
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


def _store(db: Path, record: bool) -> SQLiteStore | None:
    return SQLiteStore(db) if record else None


def _close(store: SQLiteStore | None) -> None:
    if store is not None:
        store.close()


@app.command()
def simulate(
    scenario: Path,
    db: Path = typer.Option(Path("awareness.db"), help="SQLite event log used with --record"),
    record: bool = typer.Option(False, "--record", help="Record observations and derived entities to SQLite"),
    realtime: bool = typer.Option(False, help="Sleep between simulated timesteps"),
) -> None:
    """Run a deterministic synthetic scenario through the real ingestion/fusion path."""
    store = _store(db, record)
    try:
        engine = asyncio.run(run_collector(SimulatedCollector(scenario, realtime=realtime), store))
    finally:
        _close(store)
    console.print(_entity_table(engine.world.entities.values()))


@app.command("demo-kismet")
def demo_kismet(
    fixture: Path = typer.Argument(Path("demos/kismet_devices.json")),
    db: Path = typer.Option(Path("awareness.db"), help="SQLite event log used with --record"),
    record: bool = typer.Option(False, "--record", help="Record observations and derived entities to SQLite"),
    realtime: bool = typer.Option(True, help="Pause between demo snapshots"),
) -> None:
    """Replay representative Kismet device snapshots through the real fusion/HUD path."""
    store = _store(db, record)
    try:
        engine = asyncio.run(run_collector(KismetDemoCollector(fixture, realtime=realtime), store))
    finally:
        _close(store)
    console.print(_entity_table(engine.world.entities.values()))


@app.command()
def kismet(
    url: str = typer.Option("http://127.0.0.1:2501", help="Kismet server base URL"),
    db: Path = typer.Option(Path("awareness.db"), help="SQLite event log used with --record"),
    record: bool = typer.Option(False, "--record", help="Record observations and derived entities to SQLite"),
    poll: float = typer.Option(2.0, help="Poll interval in seconds"),
    username: str | None = typer.Option(None, help="Kismet username, if required"),
    password: str | None = typer.Option(None, help="Kismet password, if required", hide_input=True),
) -> None:
    """Continuously ingest nearby Wi-Fi devices from a Kismet server."""
    store = _store(db, record)
    destination = str(db) if record else "memory only"
    console.print(f"[bold green]Kismet[/bold green] {url} -> {destination} (Ctrl+C to stop)")
    try:
        asyncio.run(run_collector(KismetCollector(url, poll_interval=poll, username=username, password=password), store))
    except KeyboardInterrupt:
        console.print("Stopped Kismet ingestion")
    finally:
        _close(store)


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


@app.command()
def serve(
    db: Path = typer.Option(Path("awareness.db"), help="SQLite event log"),
    host: str = typer.Option("0.0.0.0", help="Listen address"),
    port: int = typer.Option(8000, help="HTTP port"),
) -> None:
    """Serve the mobile-first Total Awareness HUD and API."""
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter('Install server dependencies: pip install -e ".[server]"') from exc

    from total_awareness.server.app import create_app

    console.print(f"[bold green]HUD[/bold green] http://127.0.0.1:{port}")
    if host == "0.0.0.0":
        console.print("Open the same port using this PC's LAN IP from your phone.")
    uvicorn.run(create_app(db), host=host, port=port)


if __name__ == "__main__":
    app()
