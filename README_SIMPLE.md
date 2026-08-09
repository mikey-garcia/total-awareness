# Total Awareness, at a glance

```text
hardware -> protocol dict -> database -> core/world -> API -> phone HUD
```

The protocol dict is defined in `PROTOCOL.md`. Hardware adapters live in `src/total_awareness/hardware/`. Everything else is being collapsed toward `core.py`, `db.py`, `app.py`, and `cli.py`.

If you are adding a sensor, you should normally need exactly one new file under `hardware/` and a test.
