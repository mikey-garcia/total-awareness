from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from total_awareness.app import create_app
from total_awareness.core import World, ingest, replay as replay_world
from total_awareness.db import connect, load, save
from total_awareness.hardware.kismet import normalize

app = typer.Typer(help="Total Awareness research CLI")
console = Console()


@app.command("demo-kismet")
def demo_kismet(
    fixture: Path = typer.Argument(Path("demos/kismet_devices.json")),
    db: Path = typer.Option(Path("awareness.db")),
    record: bool = typer.Option(False, "--record", help="Persist observations to SQLite"),
) -> None:
    import json

    data = json.loads(fixture.read_text(encoding="utf-8"))
    snapshots = data.get("snapshots", data) if isinstance(data, dict) else data
    world = World()
    conn = connect(db) if record else None
    try:
        for snapshot in snapshots:
            devices = snapshot.get("devices", snapshot) if isinstance(snapshot, dict) else snapshot
            if not isinstance(devices, list):
                continue
            for device in devices:
                if not isinstance(device, dict):
                    continue
                observation = normalize(device, sensor="kismet:demo")
                if observation is None:
                    continue
                if conn is not None:
                    save(conn, observation)
                ingest(world, observation)
    finally:
        if conn is not None:
            conn.close()
    console.print_json(data=list(world.entities.values()))


@app.command()
def replay(db: Path = typer.Option(Path("awareness.db"))) -> None:
    conn = connect(db)
    try:
        world = replay_world(load(conn))
    finally:
        conn.close()
    console.print_json(data=list(world.entities.values()))


@app.command()
def serve(
    db: Path = typer.Option(Path("awareness.db")),
    host: str = typer.Option("0.0.0.0"),
    port: int = typer.Option(8000),
) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise typer.BadParameter('Install server dependencies: pip install -e ".[server]"') from exc
    uvicorn.run(create_app(db), host=host, port=port)


if __name__ == "__main__":
    app()
