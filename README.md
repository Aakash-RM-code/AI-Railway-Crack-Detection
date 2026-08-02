# 🚆 AI Railway Crack Detection System

## Overview

An AI-powered railway crack detection system using:

- YOLOv8 (Ultralytics)
- OpenCV
- ESP32 rover controller + ESP32-CAM
- GSM (SMS alerts)
- Flet (web dashboard)
- Python 3.11

The system detects cracks in real time, displays a professional inspection UI,
logs detections, saves snapshots, alerts via SMS, and controls the rover
hardware through an ESP32.

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
- ✅ Professional Flet dashboard

## Getting Started

1. Install Python 3.11 (this project is verified on 3.11 only).
2. Install dependencies:

   ```powershell
   & "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
   ```

3. Run the app (web mode on `http://localhost:8080`):

   ```powershell
   & "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" app.py
   ```

   or double-click `run_app.bat`.

See `docs/START_HERE.md` for configuration and `docs/TODO.md` for the backlog.

## Project Structure

```
app.py            entry point (Flet web app, single-instance lock)
config.py         single source of truth for paths & settings
backend/          server-side pipeline (detector, alert, stats, logger,
                  camera manager, ESP32 control, report generator)
ui/               Flet front-end (controller singleton + dashboard + components)
utils/            helpers (GSM settings store)
models/best.pt    production YOLO model
detections/       saved snapshots        logs/detections.csv   detection history
reports/          generated PDF reports  uploads/              demo video uploads
archive/legacy/   superseded / unused code (not imported)
docs/             PROJECT_TREE, ARCHITECTURE, DEPENDENCIES, START_HERE, TODO
```

For the full layout see `docs/PROJECT_TREE.md`.

## Documentation

| Document | Contents |
|---|---|
| `docs/PROJECT_TREE.md` | Full filesystem layout |
| `docs/ARCHITECTURE.md` | Layers, modules, data flow, threading model |
| `docs/DEPENDENCIES.md` | Import graph, libraries, path dependencies |
| `docs/START_HERE.md` | Setup, run, configuration |
| `docs/TODO.md` | Improvement backlog |
