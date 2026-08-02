# Dependencies — Railway Crack Detection System

## Module import graph (active code)

`config` is the only module imported by both `backend/` and `utils/`; `ui/`
depends on `backend/`, `utils/`, and `config`. There are **no circular imports**
and **no duplicate module names** in the active tree (verified by script).

```
config.py
  ├── backend/esp32.py
  ├── backend/camera_manager.py
  ├── backend/logger.py
  ├── backend/report_generator.py
  ├── ui/controller.py
  ├── ui/dashboard.py
  └── utils/gsm_store.py

backend/esp32.py               ← config
backend/detector.py            ← config (CONFIDENCE_THRESHOLD, MODEL_PATH)
backend/alert_manager.py       ← backend/esp32.py (send SMS), config
backend/statistics_manager.py  ← (stdlib only)
backend/logger.py              ← config
backend/camera_manager.py      ← backend/detector, backend/alert_manager,
                                 backend/statistics_manager, backend/logger, config
backend/report_generator.py    ← config, controller (via parameter)
ui/controller.py               ← config, backend/esp32, backend/camera_manager (lazy)
ui/dashboard.py                ← config, ui/controller, ui/theme,
                                 ui/components/*, backend/report_generator (lazy)
ui/components/*                ← flet, ui/theme, ui/controller, config (per card)
utils/gsm_store.py             ← config
app.py                         ← config, ui/controller, ui/dashboard, flet
```

`backend/camera_manager` is imported lazily inside `ui/controller.py`
(`set_camera_source`, `_camera_loop`) to keep the module graph acyclic at
import time; `backend/report_generator` is imported lazily in `ui/dashboard.py`
so the heavy `reportlab` stack only loads when a report is actually generated.

## External libraries

| Package        | Used by                                                      | Notes                              |
|----------------|--------------------------------------------------------------|------------------------------------|
| `flet`         | `app.py`, `ui/*`                                             | Web-mode UI framework (0.86.4)     |
| `ultralytics`  | `backend/detector.py`                                        | YOLO inference (`best.pt`)         |
| `opencv-python`| `backend/camera_manager.py`, `backend/logger.py`, controller | Capture, encode, image save        |
| `numpy`        | `backend/camera_manager.py`                                  | ESP32-CAM snapshot decode          |
| `reportlab`    | `backend/report_generator.py`                                | PDF inspection reports             |
| `pyserial`     | — (unused)                                                   | Only the archived serial shim used it |
| `pandas`       | — (unused)                                                   | Listed in `requirements.txt` only  |
| `streamlit`    | — (unused)                                                   | Listed in `requirements.txt` only  |

`requirements.txt` is intentionally **untouched** (out of scope for the
refactor). `pandas`, `streamlit`, and `pyserial` remain listed there but are not
referenced anywhere in the active code; they are candidate removals.

## Filesystem path dependencies

Every path flows through `config.py`:

| Constant             | Default                                 | Consumed by                                  |
|----------------------|-----------------------------------------|----------------------------------------------|
| `MODEL_PATH`         | `models/best.pt`                        | `backend/detector.py`, `report_generator`    |
| `HISTORY_CSV`        | `logs/detections.csv`                   | `backend/logger.py`, `report_generator`, `ui/controller`, history table |
| `GSM_SETTINGS_CSV`   | `config/gsm_settings.csv`               | `utils/gsm_store.py`                         |
| `APP_LOCK_FILE`      | `.app.lock`                             | `app.py`                                     |
| `DETECTIONS_DIR`     | `detections/`                           | `backend/logger.py`, `report_generator`, `ui/controller` |
| `LOGS_DIR`           | `logs/`                                 | `backend/logger.py`                          |
| `REPORTS_DIR`        | `reports/`                              | `backend/report_generator.py`                |
| `UPLOADS_DIR`        | `uploads/`                              | `ui/dashboard.py`                            |
| `CONFIG_DIR`         | `config/`                               | `utils/gsm_store.py`                         |

## Verification commands

```powershell
# Python 3.11 (sole interpreter used by this project)
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -c "import config, app, backend.camera_manager, ui.controller, ui.dashboard, utils.gsm_store; print('imports OK')"
```
