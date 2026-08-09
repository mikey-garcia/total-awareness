# Simple core

Target package shape:

```text
total_awareness/
├── app.py
├── cli.py
├── core.py
├── db.py
├── protocol.py
├── hardware/
│   ├── kismet.py
│   ├── ble.py
│   ├── csi.py
│   └── camera.py
└── static/
    └── index.html
```

Rules:

1. Hardware files only translate external data into the five-key protocol.
2. `db.py` only stores and loads protocol dictionaries and derived entities.
3. `core.py` only turns observations into the current world model.
4. `app.py` only exposes the world model to the HUD/API.
5. `cli.py` only wires commands together.
6. Prefer functions and dictionaries. Add a class only when it owns meaningful state.
7. One concept gets one obvious home. No `utils.py` and no framework-shaped folders.

The existing `collectors/`, `core/`, `fusion/`, `server/`, and `storage/` packages are migration sources, not the desired final architecture. Move behavior only when its replacement has a test; then delete the old file.
