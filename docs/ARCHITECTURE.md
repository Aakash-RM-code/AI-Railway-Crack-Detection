# Architecture — Railway Crack Detection System

## Overview

A **FastAPI-ready backend** that controls a railway rover over an ESP32, feeds a
camera stream through a YOLO crack-detection model, and exposes live detection
state, statistics, health scoring, alerts (SMS via GSM module), and PDF
inspection reports over HTTP + WebSocket.

The legacy Flet front-end (dashboard, cards, `AppController`) has been archived
to `archive/legacy/ui/`; its business logic lives on in `backend/services/`. A
future React frontend consumes the API layer in `backend/api/`.

The codebase is organised into clean layers. Application modules never reach
past the layer they belong to: `backend/api` talks to `backend/services`,
`services` and `hardware` talk to `config.py`, and nothing talks to the file
system except through `config.py` paths.

```
┌─────────────────────────────── backend / api (FastAPI) ────────────────────────────────┐
│  main.py → routes.py (REST) + websocket.py (live stream) + schemas.py (pydantic)      │
└──────────────────────────────────────┬─────────────────────────────────────────────────┘
                                       │ get_* accessors / commands
┌──────────────────────────────────────▼─────────────────────────────────────────────────┐
│  backend / services  (detection pipeline business logic)                               │
│  CameraPipeline ──► CameraManager ──► CrackDetector ──► AlertManager                   │
│        │                                    │              └──► StatisticsManager      │
│        │                                    └──► DetectionLogger (CSV + snapshots)     │
│        │                                    └──► HistoryManager (reads CSV)            │
│        └── ReportGenerator ──► PDF reports from pipeline state                         │
│  backend / hardware                                                                     │
│  ESP32Controller ──► rover movement + GSM SMS + GPS (HTTP)                             │
│  GpsService / GsmService ──► thin, hardware-agnostic wrappers                          │
└──────────────────────────────┬──────────────────────────────────────────────────────────┘
                               │ config paths
┌──────────────────────────────▼──────────────────────────────────────────────────────────┐
│  config.py — every filesystem path + tunable setting                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Module responsibilities

### Entry point — `backend/main.py`
- Builds the FastAPI `app`, includes the REST + WebSocket routers, opens CORS
  for a future React client, and closes the shared pipeline on shutdown.
- Run with `uvicorn backend.main:app --host 0.0.0.0 --port 8080`.

### Configuration — `config.py`
- Single source of truth. All directory/file paths derive from
  `PROJECT_DIR = Path(__file__).resolve().parent`, so the project is relocatable.
- Paths: `MODELS_DIR`, `ASSETS_DIR`, `CONFIG_DIR`, `DETECTIONS_DIR`,
  `LOGS_DIR`, `REPORTS_DIR`, `UPLOADS_DIR`, `MODEL_PATH`, `HISTORY_CSV`,
  `GSM_SETTINGS_CSV`, `APP_LOCK_FILE`.
- Settings: `CONFIDENCE_THRESHOLD` (0.70), camera (mode/index/width/height),
  ESP32-CAM stream/snapshot URLs, ESP32 rover host/timeout/retries/speed bounds.
  Several values can be overridden with environment variables.

### API layer — `backend/api/`
- `routes.py` — REST endpoints (state, camera control, history, reports).
  Currently **structure only**; full coverage tracked in `docs/API_PLAN.md`.
- `schemas.py` — Pydantic models mirroring the runtime-state dicts.
- `websocket.py` — live `/ws/stream` channel contract (structure only).

### Detection — `backend/detector/`
- `detector.py` — `CrackDetector`. Thin YOLO wrapper around `models/best.pt`
  using `config.CONFIDENCE_THRESHOLD` (previously hardcoded 0.4 — fixed).

### Services — `backend/services/`
- `camera.py` — `CameraManager` (source mgmt + acquisition + `process_frame`)
  and `CameraPipeline` (the long-running background loop that replaced the
  legacy `AppController._camera_loop`). Holds shared state: frame base64, fps,
  resolution, alert, stats, severity counts, health. Triggers ESP32 e-stop on
  CRITICAL detections. Process-wide instance via `get_pipeline()`.
- `alert_manager.py` — `AlertManager`. Maps detections to a severity
  (SAFE/LOW/MEDIUM/HIGH/CRITICAL) using `CONFIDENCE_THRESHOLD`.
- `statistics_manager.py` — `StatisticsManager`. Per-class counters
  (total/small/medium/large/broken).
- `logger.py` — `DetectionLogger`. Cooldown-guarded snapshots to
  `config.DETECTIONS_DIR` and history rows to `config.HISTORY_CSV`.
- `history_manager.py` — `HistoryManager`. Read-only access to the detection
  history CSV and the latest snapshot image (base64).
- `report_generator.py` — `generate_report(state)` builds a professional PDF
  (reportlab) into `config.REPORTS_DIR` from a plain state dict — no UI
  dependency.

### Hardware — `backend/hardware/`
- `esp32.py` — `ESP32Controller`. Rover movement (forward/backward/stop/speed/
  e-stop), GPS caching, SMS/GSM. Thread-safe queue + single polling thread.
- `gps.py` — `GpsService`. Wraps the ESP32 GPS cache.
- `gsm.py` — `GsmService`. SMS alerts + operator phone number persistence.

### Storage — `backend/storage/`
- `gsm_store.py` — loads/saves GSM settings (phone number) to
  `config.GSM_SETTINGS_CSV`.

### Utils — `backend/utils/`
- `imaging.py` — frame → JPEG base64 helpers shared across services.

## Data flow (frame pipeline)

```
camera source → CameraManager.read_frame() → CameraPipeline._camera_loop
  → process_frame()
      → CrackDetector.detect(frame)            (YOLO, best.pt)
      → AlertManager.process(results, names)   (severity + threshold)
      → StatisticsManager.update(class)        (counters)
      → DetectionLogger.save_detection(...)    (snapshot + CSV row)
      → results[0].plot()                      (annotated frame)
  → frame base64 + alert + stats → pipeline state
  → API layer reads get_state()/endpoints
  → CRITICAL severity may trigger esp32 emergency_stop()
```

## Runtime & threading model

- One `CameraPipeline` per process (singleton via `get_pipeline()`), one camera
  acquisition thread, and one ESP32 polling thread.
- All shared pipeline state is guarded by an `RLock`; the API layer reads
  accessors on demand (and a future WebSocket pushes on change events).
- `config.py` remains the only source of filesystem paths.

## Legacy

- `archive/legacy/ui/` — the archived Flet front-end (controller, dashboard,
  theme, 13 component cards) and `app.py`/launchers. Not shipped.
- `archive/legacy/backend_old/` — pre-refactor flat backend modules, kept for
  reference. Do not import from active code.
