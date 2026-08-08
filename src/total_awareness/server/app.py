from __future__ import annotations

from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install total-awareness[server] to run the API") from exc

from total_awareness.storage.replay import replay_database


def create_app(db_path: Path | str = "awareness.db") -> FastAPI:
    app = FastAPI(title="Total Awareness", version="0.1.0")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/entities")
    def entities():
        engine = replay_database(db_path)
        return [e.model_dump(mode="json") for e in engine.world.entities.values()]

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

    return app


app = create_app()
