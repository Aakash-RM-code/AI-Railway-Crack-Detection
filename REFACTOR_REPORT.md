# REFACTOR REPORT — Railway Crack Detection System

**Project:** `D:\Python\crack_det_v_1`
**Scope:** code-only reorganisation / architecture cleanup
**Mode:** `code_only` — no UI, business-logic, or networking changes; no app launch;
no runtime verification (syntax/imports verified only).
**Interpreter:** `C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe`
**Before-snapshot:** `backup\PROJECT_INVENTORY_BEFORE.md` (full tree, file counts,
SHA256 of every `.py`, key asset sizes, data-dir counts, git state).
**Status:** ✅ All automated checks pass (45/45).

---

## 1. Project Summary

The Railway Crack Detection System is a Flet (web-browser mode) dashboard that:

- feeds a camera stream (USB / ESP32-CAM / demo video) through a YOLOv8
  crack-detection model (`models/best.pt`),
- annotates frames with bounding boxes + confidence,
- assigns a severity (SAFE/LOW/MEDIUM/HIGH/CRITICAL), sends SMS alerts via a GSM
  module on the ESP32, and can trigger an emergency stop,
- maintains per-class statistics, track-health scoring, detection history CSV,
  and auto-generated PDF inspection reports,
- controls the rover (forward/backward/stop/speed/e-stop) over the ESP32.

The refactor reorganised a flat, partially-duplicated codebase into a clean
layered structure (`app.py` / `config.py` / `backend/` / `ui/` / `utils/` /
`models/` / `assets/` / `config/` / `docs/` / `tests/` / `archive/`), removed
dead and superseded code, centralised every filesystem path into `config.py`,
and removed all `sys.path` hacks from shipped code — **without changing
functionality**.

---

## 2. Old Structure vs New Structure

### Before (flat)

```
crack_det_v_1/
├── app.py  config.py  requirements.txt  run_app.bat  run_app.ps1  README.md  .gitignore
├── detector.py  alert_manager.py  statistics_manager.py  logger.py
├── camera_manager.py  report_generator.py  gsm_store.py
├── main.py  ui.py  esp32.py  layout_test.py        # superseded / shims
├── sms_manager.py (0 bytes)  test_esp32.py  test_alert.py
├── ui/ controller.py dashboard.py theme.py mock.py
│   └── components/ 13 cards incl. rover_panel.py (never mounted)
├── models/ yolov8n.pt        # unused placeholder
├── best.pt                   # production model at root
├── detections/  reports/  logs/  datasets/  .flet/
```

### After (layered)

```
crack_det_v_1/
├── app.py                    # entry point (unchanged behaviour)
├── config.py                 # single source of truth for all paths/settings
├── requirements.txt          # untouched (out of scope)
├── run_app.bat / run_app.ps1 / README.md / .gitignore
├── backend/                  # server-side pipeline
│   ├── detector.py  alert_manager.py  statistics_manager.py  logger.py
│   ├── camera_manager.py  report_generator.py  esp32.py
├── ui/                       # Flet front-end
│   ├── controller.py  dashboard.py  theme.py
│   └── components/ 13 cards (rover_panel removed)
├── utils/gsm_store.py
├── models/best.pt            # production model (moved from root)
├── config/gsm_settings.csv
├── assets/  docs/  tests/    # new (docs populated)
├── detections/  logs/  reports/  uploads/   # runtime data
└── archive/legacy/           # superseded code, not imported
```

**Key difference:** 6 server modules moved from root into `backend/`, the helper
`gsm_store.py` moved into `utils/`, the production model moved under `models/`,
and all superseded/unused files were archived or deleted. All paths now derive
from `config.PROJECT_DIR`, making the project relocatable.

---

## 3. Files Moved / Renamed / Archived / Deleted

### Moved (kept in service)

| File | From | To |
|---|---|---|
| `detector.py` | root | `backend/detector.py` |
| `alert_manager.py` | root | `backend/alert_manager.py` |
| `statistics_manager.py` | root | `backend/statistics_manager.py` |
| `logger.py` | root | `backend/logger.py` |
| `camera_manager.py` | root | `backend/camera_manager.py` |
| `report_generator.py` | root | `backend/report_generator.py` |
| `gsm_store.py` | root | `utils/gsm_store.py` |
| `best.pt` | root | `models/best.pt` (production model, per task) |

### Archived (kept for reference, not imported by the app)

| File | New location | Reason |
|---|---|---|
| `main.py` | `archive/legacy/main.py` | superseded OpenCV pipeline |
| `ui.py` | `archive/legacy/ui.py` | superseded UI |
| `esp32.py` | `archive/legacy/esp32.py` | root shim; superseded by `backend/esp32.py` |
| `layout_test.py` | `archive/legacy/layout_test.py` | manual layout harness (port 8090) |
| `ui/mock.py` | `archive/legacy/mock.py` | unused demo data |
| `ui/components/rover_panel.py` | `archive/legacy/rover_panel.py` | never mounted in the dashboard |
| `models/yolov8n.pt` | `archive/legacy/models/yolov8n.pt` | unused placeholder model |

All archived `.py` files carry an `# ARCHIVED —` banner. `layout_test.py` alone
keeps a `sys.path.insert(0, project-root)` bootstrap so it can still be run by
hand as a manual UI harness (acceptable for an archived tool, not shipped code).

### Deleted

| File | Reason |
|---|---|
| `sms_manager.py` | 0 bytes — empty file |
| `test_esp32.py` | called the removed legacy serial API (`ESP32Controller(port="COM3")`, `esp.update()`) — would fail |
| `test_alert.py` | trivial throwaway |

### Created

`utils/__init__.py`, `tests/__init__.py`, `docs/` (5 documents), `assets/`,
`archive/`, `archive/legacy/`, `archive/legacy/models/`, `uploads/`,
`backup/PROJECT_INVENTORY_BEFORE.md`, `REFACTOR_REPORT.md`.

### Renamed

None. All names were preserved to keep controller interfaces and public names
unchanged.

---

## 4. Imports & Config Changes

### `config.py` — centralised path/config source
Added all path constants, derived from `PROJECT_DIR`:
`MODELS_DIR`, `ASSETS_DIR`, `CONFIG_DIR`, `DETECTIONS_DIR`, `LOGS_DIR`,
`REPORTS_DIR`, `UPLOADS_DIR`, `MODEL_PATH = models/best.pt`,
`HISTORY_CSV = logs/detections.csv`, `GSM_SETTINGS_CSV = config/gsm_settings.csv`,
`APP_LOCK_FILE = .app.lock`. Removed the previously duplicated config block.

### Import updates (package-qualified)
- `backend/camera_manager.py` → `from backend.detector/alert_manager/statistics_manager/logger`
- `ui/controller.py` → `from backend.esp32 import ESP32Controller`; lazy
  `from backend.camera_manager import CameraManager`
- `ui/dashboard.py` → lazy `from backend.report_generator import generate_report`
- `ui/components/history_table.py` → uses `config.HISTORY_CSV`
- `utils/gsm_store.py` → uses `config.GSM_SETTINGS_CSV`
- `app.py` → uses `config.APP_LOCK_FILE`

### Path centralisation
- `backend/logger.py` → `config.DETECTIONS_DIR`, `config.LOGS_DIR`, `config.HISTORY_CSV`
- `backend/report_generator.py` → `config.REPORTS_DIR`, `config.HISTORY_CSV`, `config.DETECTIONS_DIR`
- `ui/controller.py` → `config.DETECTIONS_DIR`, `config.HISTORY_CSV`
- `ui/dashboard.py` → `config.UPLOADS_DIR`

### Removed `sys.path` hacks (shipped code)
- `backend/esp32.py` — removed `sys.path.append(...)`
- `ui/components/rover_control_card.py` — removed `sys.path.append(...)`

**Verified:** 0 stale top-level imports of moved/removed modules remain in
active code; all active modules import cleanly.

---

## 5. Dead & Duplicate Code Removed

- **`sms_manager.py`** (0 bytes) — deleted.
- **`test_esp32.py` / `test_alert.py`** — deleted (broken/trivial).
- **`ui/controller.py`** — removed `import logging`, `_ui_update_callbacks`,
  `set_ui_update_callback()`, and `_notify_ui_update()` (which referenced the
  non-existent `get_ui_state()`).
- **Superseded pipeline** — `main.py` + `ui.py` (old OpenCV app) archived.
- **Root `esp32.py` shim** — archived (real controller is `backend/esp32.py`).
- **`ui/mock.py`** — unused demo data archived.
- **`ui/components/rover_panel.py`** — never mounted in the dashboard; archived.
- **`models/yolov8n.pt`** — unused placeholder model archived.
- **`__pycache__`** directories under root/`backend`/`ui`/`ui/components` cleaned.
- **`requirements.txt`** — NOT modified (out of scope). Note: `pandas`,
  `streamlit`, and `pyserial` are listed but referenced nowhere in active code
  (only `flet`, `ultralytics`, `opencv-python`, `numpy`, `reportlab` are used);
  they are candidate removals for a future maintenance pass.

**Duplicates:** `config.py` previously defined its settings in two blocks; these
were merged into one. No duplicate module names exist in the active tree
(verified).

---

## 6. Risks

1. **No runtime verification.** This was a code-only task. Only syntax and
   imports were verified. The app must be relaunched and exercised manually
   (Section 8) to confirm end-to-end behaviour.
2. **The pre-refactor process may still be running.** The app was live at
   PID 15148 when the refactor began. That old process still references the
   old file layout (and may hold port 8080 / `.app.lock`). It should be stopped
   before the new layout is launched; otherwise port/lock checks will report
   "already running".
3. **Archived harness keeps a `sys.path` bootstrap.** `archive/legacy/layout_test.py`
   inserts the project root into `sys.path` so it stays manually runnable. This
   is confined to the archive and does not affect shipped code.
4. **Lazy heavy imports.** `reportlab` is imported only when a report is
   generated. If `reportlab` is missing, the app still starts but report
   generation fails at runtime. Confirm it is installed before generating.
5. **`requirements.txt` untouched by design.** Unused dependencies remain listed;
   do not remove them without maintainer approval.
6. **Runtime data continues to grow.** `detections/` grew to 425 files during the
   refactor (the live process kept writing). The `.gitignore` additions cover
   these directories, so nothing sensitive/volatile is committed.

---

## 7. Recommendations

1. **Relaunch & exercise the app** (see checklist below); keep
   `backup/PROJECT_INVENTORY_BEFORE.md` until it has run cleanly for a few
   sessions.
2. **Move the hardcoded health thresholds** (`<5 / <15 / else`) out of
   `ui/controller._camera_loop` into `config.py`.
3. **Add unit tests** — `StatisticsManager`, `AlertManager` (severity + SMS
   cooldown), `DetectionLogger`, `utils/gsm_store` round-trip, and a
   no-hardware pipeline smoke test using a demo frame (see `docs/TODO.md`).
4. **Trim `requirements.txt`** (drop `pandas`, `streamlit`, `pyserial`) and pin
   versions, after maintainer confirmation.
5. **Retire `archive/legacy/`** (or at least `layout_test.py`) once the new
   structure is proven stable.
6. **Run a linter/formatter** (`ruff` / `black`) across `backend/`, `ui/`,
   `utils/` to unify style.

---

## 8. Manual Verification Checklist

Steps for the maintainer (the app was **not** launched by the refactor):

1. Stop the old instance (PID 15148, or via Task Manager / `run_app` window).
2. Confirm `models\best.pt` exists and `config.MODEL_PATH` points to it.
3. Confirm there is **no** `esp32.py`, `main.py`, `ui.py`, or `layout_test.py`
   at the project root.
4. Smoke-check imports:
   ```powershell
   & "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -c "import config, app, backend.camera_manager, ui.controller, ui.dashboard, utils.gsm_store; print('imports OK')"
   ```
5. Launch via `run_app.bat`; confirm the dashboard loads at
   `http://localhost:8080`.
6. Confirm the camera feed renders (USB by default, or set `$env:CAMERA_MODE="demo"`).
7. Trigger/observe a detection; confirm a `.jpg` lands in `detections\` and a row
   is appended to `logs\detections.csv`.
8. Generate an inspection report from the UI; confirm a PDF appears in `reports\`.
9. Confirm `.app.lock` is created on launch and removed on clean exit; confirm a
   second launch is blocked with "Application is already running".
10. Check `app_error.log` / `app_output.log` for missing-module or path errors.
11. Test rover controls, GPS, GSM/SMS, and camera-source switching (USB /
    ESP32-CAM / demo) from the UI.
