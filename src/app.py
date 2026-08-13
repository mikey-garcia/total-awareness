from __future__ import annotations

import asyncio
import json
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, Response, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install total-awareness[server] to run the API") from exc

from core import World
from db import connect, load
from push import public_key, send_all, subscribe

STATIC_DIR = Path(__file__).with_name("static")


def _snapshot(db_path: Path | str) -> dict:
    conn = connect(db_path)
    try:
        entities = World.replay(load(conn)).snapshot()
    finally:
        conn.close()
    return {
        "entities": entities,
        "counts": {
            "total": len(entities),
            "rf": sum("rssi" in entity.get("data", {}) or "frequency_khz" in entity.get("data", {}) for entity in entities),
        },
    }


def create_app(db_path: Path | str = "awareness.db") -> FastAPI:
    db_path = Path(db_path)
    app = FastAPI(title="Total Awareness", version="0.6.0")

    @app.get("/", include_in_schema=False)
    def hud():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "db": str(db_path)}

    @app.get("/api/snapshot")
    def snapshot():
        return _snapshot(db_path)

    @app.get("/api/push/key")
    def push_key():
        return {"public_key": public_key()}

    @app.post("/api/push/subscribe", status_code=204)
    def push_subscribe(value: dict):
        try:
            subscribe(value)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return Response(status_code=204)

    @app.post("/api/push/test")
    def push_test():
        return {"sent": send_all({"title": "Total Awareness", "body": "Push is online.", "url": "/"})}

    @app.get("/entities")
    def entities():
        return _snapshot(db_path)["entities"]

    @app.get("/entities/{entity_id}")
    def entity(entity_id: str):
        entities = {entity["id"]: entity for entity in _snapshot(db_path)["entities"]}
        if entity_id not in entities:
            raise HTTPException(status_code=404, detail="entity not found")
        return entities[entity_id]

    @app.websocket("/ws")
    async def websocket_updates(websocket: WebSocket):
        await websocket.accept()
        last_signature: tuple[int, int] | None = None
        try:
            while True:
                try:
                    stat = db_path.stat()
                    signature = (stat.st_mtime_ns, stat.st_size)
                except FileNotFoundError:
                    signature = (0, 0)
                if signature != last_signature:
                    await websocket.send_text(json.dumps(_snapshot(db_path), default=str))
                    last_signature = signature
                await asyncio.sleep(0.35)
        except WebSocketDisconnect:
            return

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    @app.get("/{asset:path}", include_in_schema=False)
    def static_asset(asset: str):
        path = (STATIC_DIR / asset).resolve()
        if STATIC_DIR.resolve() not in path.parents or not path.is_file():
            raise HTTPException(status_code=404)
        return FileResponse(path)

    return app


app = create_app()
