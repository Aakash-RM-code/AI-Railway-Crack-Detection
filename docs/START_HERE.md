# Start Here — Railway Crack Detection System

## What this is

A Flet (web) dashboard for a railway crack-detection rover:

- Live camera feed (USB camera, ESP32-CAM, or demo video) annotated with YOLO
  crack detections.
- Severity alerting, including SMS via a GSM module on the ESP32.
- Per-class detection statistics, track-health scoring, detection history, and
  auto-generated PDF inspection reports.

## Prerequisites

- Windows 10/11.
- **Python 3.11** — this project is verified on 3.11 only. The launchers
  (`run_app.bat`, `run_app.ps1`) use
  `C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe`.
- Dependencies installed: `pip install -r requirements.txt`
  (flet, ultralytics, opencv-python, numpy, reportlab; pandas/streamlit/pyserial
  are listed but not used by the app).

## Run the app

Easiest options:

- Double-click `run_app.bat`, or run `run_app.ps1` from PowerShell.

Or directly:

```powershell
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" app.py
```

The app starts Flet in **web-browser mode** on `http://localhost:8080` and
opens the browser automatically. It refuses to start a second copy while one is
already running (PID lock + port check).

## Configuration

All settings live in `config.py` (the single source of truth):

| Setting              | Default     | Meaning                                |
|----------------------|-------------|----------------------------------------|
| `CAMERA_MODE`        | `usb`       | `usb` \| `esp32cam` \| `demo`          |
| `CAMERA_INDEX`       | `0`         | USB camera index                       |
| `CONFIDENCE_THRESHOLD`| `0.70`     | YOLO confidence cutoff                 |
| `ESP32_IP`           | `192.168.1.120` | Rover controller host             |
| `ESP32CAM_IP`        | `192.168.4.1` | ESP32-CAM board host                 |
| `GSM_SETTINGS_CSV`   | `config/gsm_settings.csv` | SMS recipient/APN        |

Most can be overridden per-launch with environment variables, e.g.:

```powershell
$env:CAMERA_MODE = "demo"
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" app.py
```

## Where data lives

- Detection snapshots → `detections/` (one `.jpg` per logged detection)
- Detection history → `logs/detections.csv`
- PDF inspection reports → `reports/`
- Demo video uploads → `uploads/`
- GSM settings → `config/gsm_settings.csv` (gitignored — contains a phone number)

## Docs index

- `docs/PROJECT_TREE.md` — full filesystem layout.
- `docs/ARCHITECTURE.md` — layers, modules, data flow, threading.
- `docs/DEPENDENCIES.md` — import graph, libraries, path dependencies.
- `docs/TODO.md` — improvement backlog.

## Notes

- The production model is `models/best.pt`; it is the only model the app loads.
- Archived/legacy files (old OpenCV pipeline, old UI, layout harness) live under
  `archive/legacy/` and are not imported by the app.
- The `# ARCHIVED —` banners and `backup/PROJECT_INVENTORY_BEFORE.md` describe
  the pre-refactor state for historical reference.
