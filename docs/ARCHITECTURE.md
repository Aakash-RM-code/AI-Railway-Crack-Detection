# Architecture — Railway Crack Detection System

## Overview

A Flet (web-browser mode) dashboard that controls a railway rover over an ESP32,
feeds a camera stream through a YOLO crack-detection model, and exposes live
detection state, statistics, health scoring, alerts (SMS via GSM module), and
PDF inspection reports.

The codebase is organised into four layers. Application modules never reach
past the layer they belong to: `ui/` talks to `backend/` (and `utils/`),
`backend/` and `utils/` talk to `config.py`, and nothing talks to the file
system except through `config.py` paths.

```
┌───────────────────────────── ui / (Flet front-end) ─────────────────────────────┐
│  app.py  →  Dashboard  →  13 component cards  →  AppController (singleton)     │
└──────────────────────────────────┬──────────────────────────────────────────────┘
                                   │ get_* accessors / esp_* commands
┌──────────────────────────────────▼──────────────────────────────────────────────┐
│  backend / (server-side pipeline)                                               │
│  CameraManager ──► CrackDetector ──► AlertManager ──► StatisticsManager        │
│        │                                          └──► DetectionLogger (CSV)    │
│        └── reads from config.MODEL_PATH / demo video / ESP32-CAM stream         │
│  ESP32Controller ──► rover movement + GSM SMS (HTTP)                            │
│  ReportGenerator ──► PDF reports from controller state + CSV                    │
└──────────────────────────────┬──────────────────────────────────────────────────┘
                               │ config paths
┌──────────────────────────────▼──────────────────────────────────────────────────┐
│  config.py — every filesystem path + tunable setting                            │
└──────────────────────────────────────────────────────────────────────────────────┘
```

## Module responsibilities

### Entry point — `app.py`
- Configures `logging`, verifies Python 3.11, acquires a single-instance lock
  (`config.APP_LOCK_FILE`), and starts Flet in **web-browser mode** on port 8080.
- On shutdown releases the lock and closes the shared controller.

### Configuration — `config.py`
- Single source of truth. All directory/file paths derive from
  `PROJECT_DIR = Path(__file__).resolve().parent`, so the project is relocatable.
- Paths: `MODELS_DIR`, `ASSETS_DIR`, `CONFIG_DIR`, `DETECTIONS_DIR`,
  `LOGS_DIR`, `REPORTS_DIR`, `UPLOADS_DIR`, `MODEL_PATH`, `HISTORY_CSV`,
  `GSM_SETTINGS_CSV`, `APP_LOCK_FILE`.
- Settings: `CONFIDENCE_THRESHOLD`, camera (mode/index/width/height), ESP32-CAM
  stream/snapshot URLs, ESP32 rover host/timeout/retries/speed bounds. Several
  values can be overridden with environment variables.

### Front-end — `ui/`
- `controller.py` — `AppController`, a **process-wide singleton**
  (`get_controller()`), because Flet web mode creates one session per browser
  tab; exactly one camera loop and one ESP32 polling thread must be shared.
  Exposes read accessors (`get_frame_base64`, `get_alert`, `get_stats`,
  `get_health`, `get_history`, `get_latest_snapshot`, ...) and commands
  (`start`, `stop`, `connect`, `set_camera_source`, `esp_*`).
- `dashboard.py` — `Dashboard` mounts the bounded 3-column layout; owns the
  periodic UI refresh loop and persists demo-video uploads under
  `config.UPLOADS_DIR`.
- `theme.py` — colour/theme constants used by the components.
- `components/` — 13 presentational cards (header, camera, gps, gsm, health,
  alert, statistics, snapshot, history table, rover control, analytics, footer,
  base helpers). They are passive: they receive values from the dashboard and
  forward user actions to the controller.

### Back-end — `backend/`
- `camera_manager.py` — `CameraManager`. Owns the active source
  (`usb` | `esp32cam` | `demo`), runs an acquisition thread, and `process_frame`
  drives the full detection pipeline and returns `{frame, alert, stats, logged}`.
- `detector.py` — `CrackDetector`. Thin YOLO wrapper around
  `models/best.pt` with the configured `CONFIDENCE_THRESHOLD`.
- `alert_manager.py` — `AlertManager`. Maps detections to a severity
  (SAFE/LOW/MEDIUM/HIGH/CRITICAL), enforces an SMS cooldown and sends alerts via
  the ESP32/GSM module.
- `statistics_manager.py` — `StatisticsManager`. Tracks per-class counters
  (total/small/medium/large/broken).
- `logger.py` — `DetectionLogger`. Cooldown-guarded saving of snapshots to
  `config.DETECTIONS_DIR` and append-only history rows to `config.HISTORY_CSV`.
- `esp32.py` — `ESP32Controller`. Rover movement (forward/backward/stop/speed/
  e-stop), GPS caching, and SMS/GSM via AT commands. All network settings come
  from `config`.
- `report_generator.py` — `generate_report(controller)` builds a professional
  PDF (reportlab) into `config.REPORTS_DIR` from controller state plus the
  detection CSV and latest snapshot.

### Helpers — `utils/`
- `gsm_store.py` — loads/saves GSM settings (phone number, APN) to
  `config.GSM_SETTINGS_CSV`.

## Data flow (frame pipeline)

```
camera source → CameraManager.read_frame() → controller._camera_loop
  → process_frame()
      → CrackDetector.detect(frame)            (YOLO, best.pt)
      → AlertManager.process(results, names)   (severity + SMS)
      → StatisticsManager.update(class)        (counters)
      → DetectionLogger.save_detection(...)    (snapshot + CSV row)
      → results[0].plot()                      (annotated frame)
  → frame base64 + alert + stats pushed to AppController state
  → dashboard refresh reads get_*() and renders cards
  → CRITICAL severity may trigger esp_emergency_stop()
```

## Runtime & threading model

- Flet **web mode** (not desktop); one controller, one camera acquisition
  thread, and one ESP32 polling thread per process — enforced by the singleton
  in `ui/controller.py`.
- All shared state on `AppController` is guarded by an `RLock`; the dashboard
  polls accessors on a timer rather than receiving callbacks.
- `app.py` prevents duplicate launches with a PID lock file + port check.

## Manual harness (not shipped)

`archive/legacy/layout_test.py` is an archived layout sandbox that serves a
standalone Flet page on port 8090. It imports `ui.controller`/`ui.dashboard`
and keeps a `sys.path.insert(0, ...)` bootstrap so it can still be launched by
hand for UI experimentation. It is not part of the shipped application.
