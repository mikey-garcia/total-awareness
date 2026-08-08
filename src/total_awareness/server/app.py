from __future__ import annotations

import asyncio
import json
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import FileResponse
    from fastapi import Response

except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install total-awareness[server] to run the API") from exc

from total_awareness.storage.replay import replay_database

STATIC_DIR = Path(__file__).with_name("static")


def _snapshot(db_path: Path | str) -> dict:
    engine = replay_database(db_path)
    entities = sorted(engine.world.entities.values(), key=lambda entity: entity.id)
    observer = next((entity for entity in entities if entity.kind == "observer"), None)
    return {
        "observer": None if observer is None else observer.model_dump(mode="json"),
        "entities": [entity.model_dump(mode="json") for entity in entities],
        "counts": {
            "total": len(entities),
            "cameras": sum(entity.kind == "camera" for entity in entities),
            "rf": sum(entity.kind in {"rf_device", "access_point"} for entity in entities),
            "unknown": sum(entity.kind == "unknown" for entity in entities),
        },
    }


def create_app(db_path: Path | str = "awareness.db") -> FastAPI:
    db_path = Path(db_path)
    app = FastAPI(title="Total Awareness", version="0.2.0")

    @app.get("/", include_in_schema=False)
    def hud():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "db": str(db_path)}

    @app.get("/api/snapshot")
    def snapshot():
        return _snapshot(db_path)

    @app.get("/entities")
    def entities():
        return _snapshot(db_path)["entities"]

    @app.get("/entities/{entity_id}")
    def entity(entity_id: str):
        engine = replay_database(db_path)
        if entity_id not in engine.world.entities:
            raise HTTPException(status_code=404, detail="entity not found")
        entity_, observations = engine.world.explain(entity_id)
        return {
            "entity": entity_.model_dump(mode="json"),
            "observations": [o.model_dump(mode="json") for o in observations],
        }

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

    # bc favicon not found is annoying lol
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    return app

app = create_app()
