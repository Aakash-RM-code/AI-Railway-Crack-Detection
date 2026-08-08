# Backend Overview — Railway Crack Detection System

This document explains how the backend is structured, how to run it, and how a
future React frontend can talk to it. It complements `docs/ARCHITECTURE.md`
(static layout) and `docs/API_PLAN.md` (planned API surface).

## What the backend does

1. **Capture** — `CameraManager` acquires frames from one of three sources:
   `usb`, `esp32cam`, or `demo` (a video file). A background acquisition thread
   always keeps the latest frame ready.
2. **Detect** — `CrackDetector` runs YOLO (`models/best.pt`) with
   `config.CONFIDENCE_THRESHOLD` on each frame.
3. **Assess** — `AlertManager` maps the best detection to a severity
   (SAFE/LOW/MEDIUM/HIGH/CRITICAL); `StatisticsManager` counts per-class
   detections.
4. **Record** — `DetectionLogger` saves cooldown-guarded snapshots +
   history rows; `HistoryManager` reads them back.
5. **Report** — `ReportGenerator` produces PDF inspection reports.
6. **Control** — `ESP32Controller` (rover movement, GPS, GSM/SMS) is wrapped by
   `GpsService` and `GsmService`.
7. **Serve** — `backend/main.py` exposes all of the above via FastAPI.

## Running the backend

```powershell
# from the project root
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8080
```

- Interactive docs: http://localhost:8080/docs
- Liveness probe: http://localhost:8080/api/health

Note: the capture pipeline is **not** auto-started at app startup. Start it via
`POST /api/camera/start` (or programmatically with `get_pipeline().start()`).
The ESP32 controller is instantiated by the consumer that needs it — the API
layer currently exposes pipeline state; rover/ESP32 endpoints are planned
(`docs/API_PLAN.md`).

## Threading model

- One `CameraPipeline` per process (singleton via `get_pipeline()`), guarded by
  an `RLock`. This replaces the legacy Flet `AppController` singleton.
- One camera acquisition thread inside `CameraManager`.
- One ESP32 polling thread inside `ESP32Controller` (started explicitly).

## How a React frontend would integrate

```
React SPA ──HTTP──▶ backend/main.py (FastAPI)
      │                 ├── /api/state, /api/camera/*, /api/history, /api/report
      └──WebSocket──▶ /ws/stream (live RuntimeState pushes)
```

The React app calls REST endpoints for on-demand data and commands, and keeps a
WebSocket open for live frame/alert updates. All response shapes are defined in
`backend/api/schemas.py`.

## File locations of interest

| Concern                | File                                    |
|------------------------|-----------------------------------------|
| FastAPI app            | `backend/main.py`                       |
| REST routes            | `backend/api/routes.py`                 |
| Pydantic models        | `backend/api/schemas.py`                |
| Live stream            | `backend/api/websocket.py`              |
| Capture + pipeline     | `backend/services/camera.py`            |
| YOLO wrapper           | `backend/detector/detector.py`          |
| Rover control          | `backend/hardware/esp32.py`             |
| Config (single source) | `config.py`                             |

## Testing

```powershell
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m pytest tests/ -q
```

The suite covers config paths (model file exists, `best.pt`), backend import
graph, API surface, and a live FastAPI health check.
