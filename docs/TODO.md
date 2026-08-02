# TODO — Railway Crack Detection System

Backlog of improvements. Nothing here blocks the current app; items are ordered
by value.

## Cleanup / hygiene
- [ ] Trim `requirements.txt`: `pandas`, `streamlit`, and `pyserial` are not
      referenced by any active module (only `reportlab`, `flet`,
      `ultralytics`, `opencv-python`, `numpy` are used). Confirm with the
      maintainers before removing, then pin versions.
- [ ] Remove `archive/legacy/layout_test.py` once the manual layout sandbox is
      no longer needed (it is the only archived file with a `sys.path` hack).
- [ ] Add `assets/` content or drop the folder if never used.

## Tests
- [ ] Unit tests: `StatisticsManager` counters, `AlertManager` severity
      mapping + SMS cooldown, `DetectionLogger` CSV/snapshot behaviour,
      `utils/gsm_store` load/save round-trip.
- [ ] Integration smoke test that walks the camera pipeline with a demo frame
      (no hardware): `CameraManager.process_frame` → `{frame, alert, stats}`.
- [ ] A tiny YOLO stub/fixture so tests never need `best.pt` to exist.

## Behaviour
- [ ] `Detector` currently persists a snapshot per detection inside the CSV
      loop; confirm the intended cooldown semantics between `DetectionLogger`
      (5 s) and `AlertManager` SMS cooldown.
- [ ] Health scoring thresholds (`<5 / <15 / else`) are hardcoded in
      `ui/controller._camera_loop`; consider moving to `config.py`.
- [ ] `report_generator` reads the latest snapshot by `getmtime`; document or
      enforce that snapshots are only written by `DetectionLogger`.

## Polish
- [ ] Add a favicon / app title consistent with the project (currently the
      page title is "ESP32 Rover Control System").
- [ ] Run `ruff`/`black` over `backend/`, `ui/`, `utils/` and adopt a single
      style.
