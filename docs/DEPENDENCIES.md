# Dependencies — Railway Crack Detection System

## Module import graph (active code)

`config` is the only module imported by every package; `backend/services`
depends on `backend/detector`, `backend/hardware`, `backend/storage`, and
`backend/utils`. There are **no circular imports** and **no duplicate module
names** in the active tree (verified by tests).

```
config.py
  ├── backend/hardware/esp32.py
  ├── backend/services/camera.py
  ├── backend/services/alert_manager.py
  ├── backend/services/logger.py
  ├── backend/services/report_generator.py
  ├── backend/storage/gsm_store.py
  └── tests/test_backend.py

backend/detector/detector.py          ← config
backend/services/camera.py            ← backend/detector, backend/services/{alert_manager,
                                        statistics_manager, logger}, backend/utils/imaging, config
backend/services/alert_manager.py     ← config
backend/services/statistics_manager.py← (stdlib only)
backend/services/logger.py            ← config
backend/services/history_manager.py   ← config
backend/services/report_generator.py  ← config
backend/hardware/esp32.py             ← config
backend/hardware/gps.py               ← (wraps esp32 via parameter)
backend/hardware/gsm.py               ← backend/storage/gsm_store
backend/storage/gsm_store.py          ← config
backend/utils/imaging.py              ← cv2 (lazy import)
backend/api/routes.py                 ← backend.services.{camera,history_manager,report_generator}, schemas
backend/api/websocket.py              ← backend.services.camera
backend/api/schemas.py                ← pydantic
backend/main.py                       ← backend.api.routes, backend.api.websocket
```

`backend/services/camera.py` imports the detector eagerly; the heavy `reportlab`
stack only loads when a report is generated.

## External libraries

| Package        | Used by                                          | Notes                                    |
|----------------|--------------------------------------------------|------------------------------------------|
| `ultralytics`  | `backend/detector/detector.py`                   | YOLO inference (`best.pt`)               |
| `opencv-python`| `backend/services/camera.py`, `logger.py`, `utils`| Capture, encode, image save            |
| `numpy`        | `backend/services/camera.py`                     | ESP32-CAM snapshot decode                |
| `reportlab`    | `backend/services/report_generator.py`           | PDF inspection reports                   |
| `requests`     | `backend/hardware/esp32.py`                      | Rover HTTP client + retries              |
| `fastapi`      | `backend/api/*`, `backend/main.py`               | REST + WebSocket interface               |
| `uvicorn`      | `backend/main.py` (runtime)                      | ASGI server                              |
| `pydantic`     | `backend/api/schemas.py`                         | Request/response validation              |

Removed in the refactor: `flet`, `streamlit`, `pandas`, `pyserial` (no longer
referenced by active code; `flet` only served the archived UI).

## Filesystem path dependencies

Every path flows through `config.py`:

| Constant             | Default                                 | Consumed by                                  |
|----------------------|-----------------------------------------|----------------------------------------------|
| `MODEL_PATH`         | `models/best.pt`                        | `backend/detector`, `report_generator`       |
| `HISTORY_CSV`        | `logs/detections.csv`                   | `backend/services/logger`, `history_manager`, `report_generator` |
| `GSM_SETTINGS_CSV`   | `config/gsm_settings.csv`               | `backend/storage/gsm_store`                  |
| `APP_LOCK_FILE`      | `.app.lock`                             | legacy `app.py` (archived)                   |
| `DETECTIONS_DIR`     | `detections/`                           | `backend/services/logger`, `history_manager`, `report_generator` |
| `LOGS_DIR`           | `logs/`                                 | `backend/services/logger`                    |
| `REPORTS_DIR`        | `reports/`                              | `backend/services/report_generator`          |
| `UPLOADS_DIR`        | `uploads/`                              | legacy `ui/dashboard` (archived)             |
| `CONFIG_DIR`         | `config/`                               | `backend/storage/gsm_store`                  |

## Verification commands

```powershell
# Python 3.11 (project's reference interpreter)
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -c "import config, backend, backend.main; print('imports OK')"
& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m pytest tests/ -q
```
