# 🚆 AI Railway Crack Detection System

## Overview

An AI-powered railway crack detection system using:

- YOLOv8 (Ultralytics)
- OpenCV
- ESP32 rover controller + ESP32-CAM
- GSM (SMS alerts)
- FastAPI backend (REST + WebSocket, React-ready)
- Python 3.11

The system detects cracks in real time, exposes live detection state through a
clean backend API, logs detections, saves snapshots, alerts via SMS, and
controls the rover hardware through an ESP32. The legacy Flet web dashboard has
been archived (`archive/legacy/ui/`); a future React frontend consumes the API
in `backend/api/`.

## Features

- ✅ Real-time crack detection (USB camera, ESP32-CAM, or demo video)
- ✅ Bounding boxes and confidence scores
- ✅ Crack classification by severity
- ✅ Detection logging to `logs/detections.csv`
- ✅ Automatic image saving to `detections/`
- ✅ GPS coordinate capture
- ✅ GSM SMS alerts
- ✅ Track-health scoring
- ✅ PDF inspection reports (`reports/`)
- ✅ Rover control + emergency stop
- ✅ FastAPI REST + WebSocket interface (`backend/main.py`)

## Getting Started

1. Install Python 3.11 (this project is verified on 3.11 only).
2. Install dependencies:

   ```powershell
   & "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
   ```

3. Run the backend (interactive docs on `http://localhost:8080/docs`):

   ```powershell
   & "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8080
   ```

See `docs/BACKEND_OVERVIEW.md` and `docs/API_PLAN.md` for how the backend runs
and how a React frontend can integrate.

## Project Structure

```
config.py         single source of truth for paths & settings
backend/          FastAPI-ready backend (api/, detector/, hardware/, services/,
                  storage/, utils/)
  main.py         FastAPI application entry point
  api/            REST routes + WebSocket + pydantic schemas
  services/       detection pipeline (camera, alert, stats, history, logger,
                  report generator)
  hardware/       ESP32 control + GPS/GSM wrappers
models/best.pt    production YOLO model
detections/       saved snapshots        logs/detections.csv   detection history
reports/          generated PDF reports  uploads/              demo video uploads
archive/legacy/   superseded / archived code (Flet UI, old flat backend)
docs/             PROJECT_TREE, ARCHITECTURE, DEPENDENCIES, API_PLAN,
                  BACKEND_OVERVIEW, START_HERE, TODO
```

For the full layout see `docs/PROJECT_TREE.md`.

## Documentation

| Document | Contents |
|---|---|
| `docs/PROJECT_TREE.md` | Full filesystem layout |
| `docs/ARCHITECTURE.md` | Layers, modules, data flow, threading model |
| `docs/DEPENDENCIES.md` | Import graph, libraries, path dependencies |
| `docs/API_PLAN.md` | Planned API surface + React integration checklist |
| `docs/BACKEND_OVERVIEW.md` | Running the backend, wiring a React client |
| `docs/START_HERE.md` | Setup, run, configuration |
| `docs/TODO.md` | Improvement backlog |
