from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from adapters.kismet import KismetAdapter
from app import create_app
from core import World, run_adapter
from db import connect, load

app = typer.Typer(help="Total Awareness")
console = Console()


@app.command("demo-kismet")
def demo_kismet(
    fixture: Path = typer.Argument(Path("demos/kismet_devices.json")),
    db: Path = typer.Option(Path("awareness.db")),
    record: bool = typer.Option(False, "--record"),
) -> None:
    raw = json.loads(fixture.read_text(encoding="utf-8"))
    snapshots = raw.get("snapshots", raw) if isinstance(raw, dict) else raw
    world = World()
    conn = connect(db) if record else None
    try:
        for snapshot in snapshots:
            devices = snapshot.get("devices", snapshot) if isinstance(snapshot, dict) else snapshot
            if isinstance(devices, list):
                run_adapter(KismetAdapter(devices, sensor="kismet:demo"), world, conn)
    finally:
        if conn is not None:
            conn.close()
    console.print_json(data=world.snapshot())


@app.command()
def replay(db: Path = typer.Option(Path("awareness.db"))) -> None:
    conn = connect(db)
    try:
        world = World.replay(load(conn))
    finally:
        conn.close()
    console.print_json(data=world.snapshot())


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
