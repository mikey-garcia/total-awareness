from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from total_awareness.app import create_app
from total_awareness.core import World
from total_awareness.db import connect, load, save
from total_awareness.hardware.kismet import normalize

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
            if not isinstance(devices, list):
                continue
            for device in devices:
                if not isinstance(device, dict):
                    continue
                obs = normalize(device, sensor="kismet:demo")
                if obs is None:
                    continue
                world.observe(obs)
                if conn is not None:
                    save(conn, obs)
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
