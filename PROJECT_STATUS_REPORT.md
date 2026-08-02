# PROJECT STATUS REPORT
## Railway Crack Detection System

**Document type:** Technical engineering report
**Date generated:** 02 August 2026
**Root directory:** `D:\Python\crack_det_v_1`
**Stack:** Python 3.11 · Flet 0.86.4 · Ultralytics YOLO 8.4.90 · OpenCV 4.13.0 · Torch 2.12.1 · ReportLab 5.0.0 · HTTP (ESP32/ESP32-CAM)

> This report reflects the **actual codebase** as inspected. Symbols: ✔ fully implemented / ⚠ partially implemented / ❌ planned but not implemented. Nothing is assumed.

---

## 1. Executive Summary

| Item | Value |
|---|---|
| Overall status | Functional demo backbone; milestone M6 (multi-camera source) just completed |
| Estimated completion | **~75%** |
| Architecture maturity | 6/10 — solid layered design emerging, but several stale/legacy files remain |
| Strengths | Non-blocking ESP32 command queue + single polling thread; multi-source camera abstraction (USB / ESP32-CAM / demo video) with live switching; rich Flet dashboard; real YOLO inference; snapshot + CSV history persisted |
| Weaknesses | `StatisticsManager` class-name matching bug (never increments); `report_generator.py` broken import and not wired to UI; `config.py` duplicated/overlapping sections; dashboard cards mostly render at mount time only; no real hardware validated; several dead/legacy modules |

**Milestone history (git):**
- `e0c6535` — v1.0 stable YOLO + OpenCV + ESP32 LED (legacy single-file app)
- `6021626` — centralized config module
- Uncommitted work: M1–M6 refactors (`ui/`, `backend/`, `camera_manager.py`, etc.)

**Most recent verified state:** Flet web app boots on `http://localhost:8080` with `Application started successfully!`; 21/21 headless M6 verification checks passed; the one real startup bug found during validation (flet 0.86.4 `FilePicker(on_result=...)` not supported) was **fixed**.

---

## 2. Current Project Structure

```
D:\Python\crack_det_v_1
├── app.py                        # Flet entry point (WEB_BROWSER, port 8080)     [BACKEND/ENTRY]
├── camera_manager.py             # Multi-source camera + background acquisition    [BACKEND]
├── detector.py                   # YOLO wrapper (CrackDetector)                    [BACKEND]
├── alert_manager.py              # Severity classification from detections         [BACKEND]
├── statistics_manager.py         # Session counters (has class-name bug)          [BACKEND]
├── logger.py                     # CSV history + JPG snapshot saving               [BACKEND]
├── gsm_store.py                  # GSM phone-number persistence (CSV)              [BACKEND/UTIL]
├── report_generator.py           # PDF report (reportlab) — BROKEN IMPORT          [REPORTS]
├── sms_manager.py                # EMPTY FILE (dead)                               [DEAD CODE]
├── esp32.py                      # Shim re-exporting backend.esp32                 [LEGACY/SHIM]
├── main.py                       # Legacy OpenCV-window app — calls esp.update()   [LEGACY/BROKEN]
├── ui.py                         # Legacy cv2 overlay drawing                      [LEGACY]
├── test_alert.py                 # Trivial import check                             [LEGACY TEST]
├── test_esp32.py                 # Calls esp.update() — BROKEN vs new backend      [LEGACY TEST/BROKEN]
├── config.py                     # Configuration (TWO overlapping sections)        [CONFIG]
├── requirements.txt
├── best.pt                       # YOLO weights (4 classes)                        [MODEL]
├── README.md                     # Outdated (describes legacy feature set)
│
├── backend/
│   ├── __init__.py
│   └── esp32.py                  # ESP32Controller (HTTP, queue, polling)          [BACKEND/CORE]
│
├── ui/
│   ├── controller.py             # AppController — orchestrator (camera+ESP32+state)[BACKEND/CORE]
│   ├── dashboard.py              # Dashboard layout + refresh loop                  [UI/CORE]
│   ├── theme.py                  # Palette + severity colors                        [UI]
│   ├── mock.py                   # MOCK DATA (dead in live path)                   [DEAD CODE]
│   ├── components/
│   │   ├── base.py               # section_card / status_pill / kpi_card helpers    [UI]
│   │   ├── camera_card.py        # LIVE camera + Camera Source panel (M6)           [UI]
│   │   ├── alert_card.py         # Alert status card                                [UI]
│   │   ├── statistics_card.py    # KPI counters                                     [UI]
│   │   ├── health_card.py        # Track health ring                                [UI]
│   │   ├── history_table.py      # Detection history table                          [UI]
│   │   ├── snapshot_card.py      # Latest flagged snapshot                          [UI]
│   │   ├── analytics.py          # Distribution + severity progress bars            [UI]
│   │   ├── gps_card.py           # GPS status card (legacy style)                   [UI]
│   │   ├── gsm_card.py           # SMS form (legacy style)                          [UI]
│   │   ├── rover_control_card.py # D-pad + speed + E-stop (in use)                  [UI]
│   │   ├── rover_panel.py        # Older rover panel — NOT mounted                  [DEAD CODE]
│   │   ├── header.py             # Top bar + clock thread                           [UI]
│   │   └── footer.py             # Bottom bar                                       [UI]
│
├── config/
│   └── gsm_settings.csv          # Persisted GSM number                             [DATA]
├── logs/
│   └── detections.csv            # Detection history (90 rows)                      [DATA]
├── detections/                   # Saved snapshot JPGs (14 files)                   [DATA]
├── reports/                      # (empty — generator broken)                       [REPORTS]
├── .flet/                        # Flet runtime storage
├── app_output.log / app_error.log# Runtime logs (dev artifacts)
└── .git/
```

**Classification:**
- **Backend modules:** `camera_manager.py`, `detector.py`, `alert_manager.py`, `statistics_manager.py`, `logger.py`, `gsm_store.py`, `backend/esp32.py`, `ui/controller.py`
- **UI modules:** `app.py`, `ui/dashboard.py`, `ui/components/*` (16 files), `ui/theme.py`
- **Configuration:** `config.py`
- **Utilities:** `gsm_store.py`
- **Reports:** `report_generator.py` (broken)
- **Models:** `best.pt`
- **Assets:** `.flet/` (runtime), none custom
- **Legacy files:** `main.py`, `ui.py`, `esp32.py` (shim), `test_alert.py`, `test_esp32.py`
- **Dead code:** `sms_manager.py` (empty), `ui/mock.py`, `ui/components/rover_panel.py` (unused), `_notify_ui_update()`/`set_ui_update_callback()` (no caller)

---

## 3. Architecture Overview

```
        ┌────────────────────────────────────────────────────────────┐
        │                        CAMERA SOURCES                      │
        │   USB (index)  ·  ESP32-CAM (MJPEG/snapshot)  ·  Demo MP4  │
        └───────────────────────────────┬────────────────────────────┘
                                        │  background thread (keeps latest frame)
                                        ▼
                              ┌─────────────────────┐
                              │    CameraManager    │  opens source, acquires frames,
                              │ (camera_manager.py) │  runs the detection pipeline
                              └──────────┬──────────┘
                                         ▼  detector.detect(frame)
                              ┌─────────────────────┐
                              │   CrackDetector     │  YOLO model → boxes/conf/class
                              │   (detector.py)     │
                              └──────────┬──────────┘
                                         ▼
                              ┌─────────────────────┐
                              │    AlertManager     │  picks best box → severity
                              │  (alert_manager.py) │  SAFE/LOW/MEDIUM/HIGH/CRITICAL
                              └──────────┬──────────┘
                                         ▼
                    ┌────────────────────┴─────────────────────┐
                    ▼                                           ▼
         ┌──────────────────┐                     ┌──────────────────────┐
         │ StatisticsManager│                     │    DetectionLogger    │
         │ (stats counters) │                     │ (CSV history + JPG)   │
         └──────────────────┘                     └──────────────────────┘
                    │                                           │
                    └───────────────┬───────────────────────────┘
                                    ▼
                        ┌───────────────────────┐
                        │     AppController     │  owns camera thread + ESP32 polling;
                        │  (ui/controller.py)   │  caches frame/alert/stats/fps/health
                        └───────────┬───────────┘
                                    ▼
                        ┌───────────────────────┐
                        │    Flet Dashboard     │  web UI (port 8080) — reads cached
                        │  (ui/dashboard.py)    │  state @10 Hz; Camera Source panel (M6)
                        └───────────┬───────────┘
                                    ▼
                        ┌───────────────────────┐
                        │   ESP32Controller     │  HTTP client, queue-based commands,
                        │  (backend/esp32.py)   │  single background polling thread
                        └───────────┬───────────┘
                                    ▼
                        ┌───────────────────────┐
                        │      ESP32 HARDWARE    │  rover motor / GPS / GSM / E-stop
                        └───────────────────────┘
```

**Module responsibilities:**

| Module | Responsibility |
|---|---|
| `CameraManager` | Opens/closes the active source (`usb`, `esp32cam`, `demo`), runs a background acquisition thread that keeps only the latest frame, exposes `read_frame()`/`process_frame()`, and re-initializes on `set_mode()`. |
| `CrackDetector` | Thin wrapper over Ultralytics `YOLO(model)`. `detect(frame)` runs inference at `conf=0.4`. |
| `AlertManager` | From model results picks the highest-confidence box, gates on `CONFIDENCE_THRESHOLD=0.70`, maps class substring (`small/medium/large/broken`) → severity + message. |
| `StatisticsManager` | Session counters (`total/small/medium/large/broken`). ⚠ bug: compares against underscored class names. |
| `DetectionLogger` | 5-second-cooldown saving of JPG snapshots to `detections/` and CSV rows to `logs/detections.csv`. |
| `AppController` | Single orchestrator. Spawns camera loop thread + one ESP32 polling thread; caches everything the UI reads (frame base64, fps, resolution, alert, stats, severity counts, health, camera error/source). Provides source-switching API (M6). |
| `ESP32Controller` | HTTP client with retry session; commands enqueued via `submit()` (non-blocking, coalesced/debounced) and executed on one polling thread; caches status/GPS/online. |
| `Dashboard` | Composes cards; 10 Hz refresh via `threading.Timer` chain; wires rover + camera-source callbacks; owns FilePicker for demo video. |
| `Header` | Clock + status badges; updates clock from a background thread. |

---

## 4. Completed Features

| Feature | Description | Files | Status | Verification |
|---|---|---|---|---|
| ✔ Live camera (USB) | `cv2.VideoCapture(index)`, configurable width/height | `camera_manager.py`, `config.py` | ✔ | M6 harness: USB opens + produces frames |
| ✔ ESP32-CAM source | MJPEG stream URL with snapshot-URL fallback (`urlopen`+`imdecode`) | `camera_manager.py`, `config.py` | ✔ | M6 harness: stream + snapshot mock server both pass |
| ✔ Demo video source | MP4 via `cv2.VideoCapture`, loops on EOF | `camera_manager.py`, `config.py` | ✔ | M6 harness: video opens + frames produced |
| ✔ Camera source switching | `set_camera_source()` — stop→release→init→auto-continue, no app restart; Reconnect button | `ui/controller.py`, `ui/components/camera_card.py` | ✔ | M6 harness: usb↔demo switching + reconnect pass |
| ✔ Latest-frame-only acquisition | Background acquisition thread, old frames dropped | `camera_manager.py` | ✔ | M6 harness: consecutive reads return fresh refs |
| ✔ YOLO inference | Real detection, bounding boxes, confidence, class | `detector.py`, `camera_manager.py` | ✔ | M4 probe: model detects on `detections/20260722_204252.jpg`; M6 end-to-end frame→base64 |
| ✔ Detection history (CSV) | 90 historical rows; `get_history()` reads + dashboard table | `logger.py`, `ui/controller.py`, `ui/components/history_table.py` | ✔ | Data file present; controller read path exercised |
| ✔ Snapshot saving | Annotated JPGs saved to `detections/` | `logger.py` | ✔ | 14 JPG files on disk |
| ✔ Statistics counters | Session totals per class | `statistics_manager.py` | ⚠ | Logic present but **never increments** (see §12) |
| ✔ Track health scoring | Score/status/note derived from totals | `ui/controller.py` | ⚠ | Derives from broken stats → always "EXCELLENT" |
| ✔ Alert severity engine | SAFE→CRITICAL classification + message | `alert_manager.py` | ✔ | Logic verified by inspection |
| ✔ Flet dashboard | Web dashboard on :8080, dark theme, 15+ cards | `ui/dashboard.py`, `ui/components/*` | ✔ | App boots; `Application started successfully!` |
| ✔ Camera Source panel (M6) | Dropdown + Connect/Disconnect/Browse/Reconnect | `ui/components/camera_card.py` | ✔ | Build smoke test passes |
| ✔ Demo video browse (M6) | FilePicker (async, flet 0.86.4) → persists bytes to `uploads/` | `ui/dashboard.py` | ⚠ | Code path fixed & boot-verified; interactive pick untested |
| ✔ ESP32 command queue | Non-blocking `submit()`; coalescing + debounce (speed=0.2s) | `backend/esp32.py`, `ui/controller.py` | ✔ | M3 harness: 40 calls→1 request; offline/reconnect verified |
| ✔ ESP32 single polling thread | 0.1 s drain; status/GPS polled at `POLLING_INTERVAL=2 s` | `backend/esp32.py` | ✔ | M3 harness: single polling thread verified |
| ✔ ESP32 status/GPS cache | `get_cached_gps()`, online flag, last-error cache | `backend/esp32.py` | ✔ | M3 harness |
| ✔ Rover controls | Forward/Backward/Stop/Speed slider + presets/E-stop | `ui/components/rover_control_card.py` | ⚠ | UI wired; no hardware to validate |
| ✔ Emergency stop (auto) | Auto E-stop on CRITICAL alert (once per arming) | `ui/controller.py` | ⚠ | Code path present; not triggered in tests |
| ✔ SMS send/test (non-blocking) | Enqueued to ESP32; returns True immediately | `ui/controller.py` | ⚠ | Enqueues correctly; requires hardware to confirm |
| ✔ GPS read (cached) | `get_gps()` from cache; card parses lat/lon | `ui/components/gps_card.py` | ⚠ | Parsing logic present; no fix in tests |
| ⚠ GSM phone persistence | `gsm_store` save/load CSV | `gsm_store.py` | ⚠ | Helpers exist; UI does not load stored number |
| ❌ PDF reports | ReportLab generator | `report_generator.py` | ❌ | **Broken import** + not wired into UI |
| ❌ Video recording | `SAVE_VIDEO` config | — | ❌ | Flag only, no implementation |
| ❌ Streamlit dashboard | README mention + `REFRESH_RATE` config | — | ❌ | Not implemented (Flet chosen instead) |

---

## 5. UI Components

| Component | File | What it does | Data source | Status |
|---|---|---|---|---|
| Header | `header.py` | Title, ESP32/GPS/GSM dots, status pill, live clock | Clock = thread; dots are static | ⚠ Working (clock thread is not thread-safe) |
| CameraCard | `camera_card.py` | Live feed image, FPS/res badges, status pill, Start/Stop Inspection, **Camera Source panel** (dropdown, Connect/Disconnect/Browse/Reconnect) | `controller.get_frame_base64()`, `get_fps()`, `get_resolution()`, `get_camera_info()` | ✔ Working (updates at 10 Hz) |
| AlertCard | `alert_card.py` | Severity pill, class, confidence bar, message, SOS button | `controller.get_alert()` at **build time** | ⚠ SOS button is a no-op (`lambda e: None`); not refreshed live |
| StatisticsCard | `statistics_card.py` | 6 KPI counters (total/small/medium/large/broken/critical) | `controller.get_stats()`, `get_severity_counts()` at **build time** | ⚠ Static after mount; stats bug suppresses updates |
| HealthCard | `health_card.py` | Progress ring + status + note | `controller.get_health()` at build time | ⚠ Static; driven by broken stats |
| HistoryTable | `history_table.py` | Last-10 detection rows with colored crack types | `controller.get_history()` at build time | ⚠ Static after mount (does refresh via… no) |
| SnapshotCard | `snapshot_card.py` | Latest flagged snapshot image | `controller.get_latest_snapshot()` | ✔ Refreshed at 10 Hz |
| AnalyticsPanel | `analytics.py` | Crack distribution + severity share progress bars | `get_stats()`, `get_severity_counts()` at build time | ⚠ Static after mount |
| GPSCard | `gps_card.py` | GPS fix status + lat/lon | `controller.get_gps()` at build time | ⚠ Legacy-styled, static, unrefreshed |
| GSMCard | `gsm_card.py` | Phone + message form, Send/Test buttons | Callbacks only; no controller state | ⚠ Loads empty default; doesn't use `gsm_store` |
| RoverControlCard | `rover_control_card.py` | D-pad (F/B, L/R disabled), speed slider + presets, E-stop, status/IP | `controller.get_esp_status()` — **refreshed at 10 Hz** | ✔ Working (live online/offline) |
| Footer | `footer.py` | Version, session start, developer | `controller.started_at()` | ✔ Static |
| RoverPanel | `rover_panel.py` | Older rover card (never mounted) | controller | ❌ Dead code |

**Note:** Dashboard `_refresh()` only updates `camera_card`, `snapshot_card`, and `rover_control`. Everything else renders once at mount. Card `build()` methods read controller state eagerly.

---

## 6. Backend Components

### CameraManager (`camera_manager.py`) — ✔ core
- Constructs detector/alert/stats/logger, validates mode, opens source.
- `_acquire_loop` background thread: reads → stores `_latest_frame` under lock → 5 ms sleep. Only latest kept.
- `_read_once`: `cap.read()` for usb/demo (demo loops via `CAP_PROP_POS_FRAMES=0`); snapshot HTTP fetch for ESP32-CAM fallback.
- `process_frame` = unchanged AI pipeline (detect → alert → stats → log → plot).
- **Duplication:** `process_frame` logs every box in a loop **and** logs the best box again (second call usually suppressed by logger cooldown).

### CrackDetector (`detector.py`) — ✔
- Loads `best.pt` at construction (~10 s first inference warm-up observed), `detect()` at `conf=0.4`.

### AlertManager (`alert_manager.py`) — ✔
- Highest-confidence box only; threshold gate `0.70`; substring severity mapping.

### StatisticsManager (`statistics_manager.py`) — ⚠ BUG
- Compares `class_name` against `"small_crack"/"medium_crack"/"large_crack"/"broken_chain"` (underscores). Actual YOLO names are `"small crack"/"medium crack"/"large crack"/"broken chain"` (spaces). **Counters never increment** → stats, health, and analytics all stay at zero.

### DetectionLogger (`logger.py`) — ✔
- Creates dirs/CSV on init; `save_detection` respects 5 s cooldown, writes JPG + CSV row.

### ESP32Controller (`backend/esp32.py`) — ✔ core
- Retry `requests.Session` (retries on 5xx/timeouts), `submit()` queue (FIFO + coalesced keys + per-key debounce), single `_polling_loop` (drain @0.1 s; `/status`+`/gps` @`POLLING_INTERVAL=2 s`), cached online/last-error/GPS, `close()` stops polling + closes session.
- **Note:** root `esp32.py` is a shim re-exporting this class for legacy code.

### Report Generator (`report_generator.py`) — ❌ BROKEN
- `from gui_components import history_panel` → `ModuleNotFoundError` (module doesn't exist in this repo). PDF logic itself (reportlab) is written but unreachable.

### History (in `ui/controller.py:get_history`) — ✔
- Parses `logs/detections.csv` via `csv.DictReader`, returns last N rows.

### AppController (`ui/controller.py`) — ✔ core
- Owns `_esp`, camera thread, cached UI state. M6 additions: `set_camera_source`, `reconnect_camera`, `set_demo_video_path`, `get_camera_source/info`, `_join_camera_thread`.
- `_camera_loop`: creates `CameraManager(mode)`, `start()`; polls `read_frame()`; 3 s no-frame stall → error break; processes frame; base64-encodes; updates all state under lock; auto E-stop on CRITICAL.

**Interactions:** CameraManager is self-contained (owns pipeline objects). Controller calls `camera.read_frame()` → `camera.process_frame(frame)` → encodes. Controller enqueues ESP32 commands via `submit()`. UI reads controller's cached getters. No direct UI→hardware calls (M2/M3 enforced).

---

## 7. Camera Pipeline

**Shared path (all sources):**
```
source ──(acquisition thread)──▶ latest frame ──▶ Controller._camera_loop ──▶ process_frame:
        detector.detect → AlertManager → StatisticsManager.update
        → DetectionLogger.save_detection (JPG+CSV) → results[0].plot() (annotated)
        → cv2_imencode → base64 → _frame_base64 → CameraCard.image
```

- **USB:** `cv2.VideoCapture(CAMERA_INDEX)` with `CAMERA_WIDTH/HEIGHT`. On this machine the MSMF backend currently fails to grab frames (`can't grab frame` warnings) — environment-dependent, not a code defect.
- **ESP32-CAM:** tries `ESP32CAM_STREAM_URL` (MJPEG); if unopenable, falls back to `ESP32CAM_SNAPSHOT_URL` polling (`urlopen` → `imdecode`) at acquisition cadence.
- **Demo Video:** `cv2.VideoCapture(DEFAULT_VIDEO_PATH)`; loops on EOF. Processed through the **identical** pipeline (no separate demo path — M6 requirement satisfied).
- **Detection/Logging/Stats/Snapshots/Dashboard:** same for all three; controller caches per-frame base64; logger persists snapshots; dashboard refreshes feed @10 Hz.

---

## 8. ESP32 Integration

| Aspect | Implementation | Status |
|---|---|---|
| Transport | HTTP `requests.Session` w/ `Retry` (status_forcelist [408,429,500,502,503,504], backoff 0.5 s) | ✔ |
| Commands | `forward` `/forward`, `backward` `/backward`, `stop` `/stop`, `set_speed` `/speed?val=` (clamped 0–255), `send_sms` `/sms`, `send_test_sms` `/sms_test`, `emergency_stop` `/crack_stop` | ✔ |
| Non-blocking | `submit(cmd,*args,key=,debounce=)` enqueues; never runs on UI thread | ✔ (M3) |
| Coalescing/debounce | Speed slider 0.2 s; E-stop keyed `estop` | ✔ (M3: 40→1 request) |
| Status polling | `/status` every `POLLING_INTERVAL=2 s` on polling thread | ✔ |
| GPS | `/gps` polled on same cadence; cached string + parsed `(lat,lon)` | ⚠ logic ✔, hardware ❌ |
| GSM | SMS enqueued via controller; `gsm_store` persists number (not wired to UI) | ⚠ |
| Emergency stop | Manual button + auto on CRITICAL alert | ⚠ |
| Speed/direction | Slider + presets + d-pad, cached `_last_status` | ⚠ |
| Background polling | Single thread `ESP32PollingThread` (0.1 s loop) | ✔ (M3) |
| Reconnect | Polling auto-recovers online flag on next successful request; UI reflects cached state | ✔ (M3) |
| Threading | RLock-protected caches/queues; one command queue + one coalesced dict | ✔ (M3) |
| Close | `stop_polling()` join(3 s) + session close | ✔ |

Hardware is **not present** in the test environment → offline path (connection timeouts to `192.168.1.120`) is what has actually been exercised.

---

## 9. Performance Analysis

| Metric | Observed / Estimate |
|---|---|
| YOLO inference | First call ~10 s (warm-up), steady ~0.2 s/frame → **~5 fps** effective (frames from acquisition are decoupled; processing is the bottleneck) |
| Acquisition cadence | `read()` in a tight loop with 5 ms sleep (USB/demo); snapshot fetch bounded by HTTP round-trip |
| Threads | Main/Flet, `_camera_loop`, `CameraAcquisition`, `ESP32PollingThread`, `Header._tick`, transient refresh `threading.Timer` per 0.1 s → ~5 persistent + periodic timers |
| Polling frequency | ESP32: command drain 10 Hz, status/GPS 0.5 Hz; UI refresh 10 Hz |
| Memory | Latest frame + base64 JPG retained (≤ ~1 MB); `get_latest_snapshot()` re-reads newest JPG from disk each call; no frame buffering → low memory |
| Blocking operations | First YOLO load blocks camera thread start; ESP32 HTTP has 3 s timeout (offline path adds latency each poll); snapshot `urlopen` timeout 3 s |
| Thread safety | Controller/ESP32 state under `RLock` ✔; **Header clock + dashboard refresh mutate Flet controls from non-main threads** ⚠ (known Flet concern) |
| Bottlenecks | YOLO inference (5 fps); camera-busy MSMF on this machine; 3 s ESP32 connect timeouts while offline; `get_latest_snapshot()` disk read @10 Hz |

---

## 10. Code Quality Review

| Category | Item |
|---|---|
| Dead code | `sms_manager.py` (empty); `ui/mock.py` (unused mock data); `ui/components/rover_panel.py` (never mounted); `set_ui_update_callback()`/`_notify_ui_update()` (no caller; references nonexistent `get_ui_state()`) |
| Duplicate code | Two rover panels (`rover_panel.py` vs `rover_control_card.py`); two GPS/GSM style generations; duplicate detection logging in `process_frame`; two config sections redefine same keys (`CAMERA_INDEX`, `ESP32_IP`, `ESP32_PORT`, …) |
| Unused imports | `typing.Optional/Callable` and `datetime` in several cards; `ft.Icons` aliases; `streamlit`, `pandas`, `pyserial` in requirements.txt are unused by the live path |
| Architecture problems | Heavy `sys.path` hacks in `rover_control_card.py`/`backend/esp32.py`; Dashboard mixes layout + file-picker + snackbars; config split-brain (later section silently wins) |
| Technical debt | M5 (config consolidation) not done; dashboard cards static after mount; thread-unsafe Flet updates; `_refresh` uses `threading.Timer` chain instead of a single loop |
| Broken files | `report_generator.py` (import error); `main.py` + `test_esp32.py` (call removed `esp.update()`/`port=` arg); root `esp32.py` shim exists only for legacy |
| Legacy modules | `main.py`, `ui.py`, `test_alert.py`, `test_esp32.py`, `esp32.py` shim |
| README | Outdated (references Streamlit, ESP32 LED, "future features") |

---

## 11. Remaining Work

### Critical
| Item | Difficulty | Impact | Time |
|---|---|---|---|
| Fix `StatisticsManager` class-name matching (spaces vs underscores) | Trivial | High — stats/health/analytics currently always zero | 15 min |
| Fix `report_generator.py` import (`from gui_components import history_panel`) or rewire to `controller.get_history()`; wire a "Generate Report" button | Medium | Medium — PDF deliverable | 1–2 h |
| Resolve flet thread-safety: header clock + 10 Hz `page.update()` from non-main threads (move to `page.run_thread`/single loop) | Medium | High — intermittent web UI instability | 2–3 h |

### High
| Item | Difficulty | Impact | Time |
|---|---|---|---|
| M5: consolidate `config.py` duplicate sections (single source of truth) | Medium | High — removes silent override confusion | 1–2 h |
| Live-refresh alert/stats/health/history/analytics cards (not just camera/snapshot/rover) | Medium | High — dashboard currently shows stale numbers | 2–3 h |
| Validate against real ESP32 + ESP32-CAM + GPS + GSM hardware | High | Critical — hardware paths unproven | 1 day (with hardware) |
| Fix duplicated logging in `camera_manager.process_frame` | Trivial | Low-Medium | 15 min |

### Medium
| Item | Difficulty | Impact | Time |
|---|---|---|---|
| Wire `gsm_store` phone number into GSMCard (load saved default) | Low | Medium | 30 min |
| SOS button → emergency stop + SMS | Low | Medium | 30 min |
| Remove dead files (`sms_manager.py`, `mock.py`, `rover_panel.py`, `ui.py`, `test_*`) | Trivial | Low | 20 min |
| Add real test suite (pytest) for controller/camera/stats/alert | Medium | Medium | 3–4 h |
| Reduce offline ESP32 timeout churn (cache last error, longer backoff) | Low | Low | 30 min |

### Low
| Item | Difficulty | Impact | Time |
|---|---|---|---|
| Update README to current architecture | Trivial | Low | 30 min |
| Deduplicate GPS/GSM card implementations | Low | Low | 1 h |
| Config-driven video save (`SAVE_VIDEO`) | Medium | Low | 2 h |

---

## 12. Known Bugs

| # | Bug | Root cause | Files | Severity | Suggested fix |
|---|---|---|---|---|---|
| 1 | **Stats never increment** | `StatisticsManager.update()` compares `"small_crack"` (underscore) but YOLO names have spaces (`"small crack"`) | `statistics_manager.py`, `camera_manager.py` | High | Compare normalized names (`class_name.replace(" ","_")`) or update the strings to match model names |
| 2 | **PDF report broken** | `from gui_components import history_panel` → `ModuleNotFoundError`; also not wired to any button | `report_generator.py` | High | Read CSV directly or via `controller.get_history()`; add Report button in UI |
| 3 | **Flet web UI thread-safety** | `Header._tick` and Dashboard `_refresh` mutate/update controls from background threads | `ui/components/header.py`, `ui/dashboard.py` | Medium | Route updates through Flet's main thread (single refresh loop / `page.run_thread`) |
| 4 | **FilePicker startup crash (fixed)** | flet 0.86.4 `FilePicker(on_result=...)` not supported; `pick_files` is async + returns files | `ui/dashboard.py` | Fixed | Now `ft.FilePicker()` + `await pick_files(... with_data=True)` |
| 5 | **Legacy `main.py` broken** | Calls `esp.update(severity)` (removed in M2/M3) and `ESP32Controller()` mismatch | `main.py`, `test_esp32.py` | Low | Delete or migrate to AppController; root shim can't restore `update()` |
| 6 | **Duplicate detection logging** | `process_frame` saves each box then saves best box again | `camera_manager.py` | Low | Save best box only once |
| 7 | **USB camera fails on this machine** | MSMF backend `can't grab frame` (driver/in-use); CAMERA_INDEX duplicated (1 then 0 → 0 wins) | `config.py`, env | Low | Use demo/ESP32-CAM for demos; or set `CAMERA_INDEX` once |
| 8 | **Dashboard cards stale** | `_refresh()` only updates camera/snapshot/rover; others build once | `ui/dashboard.py`, cards | Medium | Refresh all cards each tick (or recompute from controller getters) |
| 9 | **GSM default not loaded** | `gsm_card` built with empty `default_phone`; `gsm_store.load_phone_number()` never called | `ui/components/gsm_card.py`, `gsm_store.py` | Low | Load stored number at mount |
| 10 | **Dead code calls `get_ui_state()`** | `_notify_ui_update()` references method that doesn't exist (never invoked today) | `ui/controller.py` | Low | Remove or implement |

---

## 13. Testing Status

| Area | Verified | Outstanding |
|---|---|---|
| Camera — USB | Opens + produces frames (headless harness) | Stable grab on this machine (MSMF warns); real field camera |
| Camera — ESP32-CAM | MJPEG stream + snapshot fallback via mock HTTP server ✔ | Real ESP32-CAM hardware; frame rate; reconnect in hardware |
| Camera — Demo video | MP4 opens, frames produced, loops on EOF ✔ | Real MP4 variety/codecs (mp4v only tested) |
| Camera switching | usb↔demo↔esp32cam via `set_camera_source`, auto-continue, reconnect ✔ | UI dropdown end-to-end click |
| YOLO | Model loads, detects on sample frame; end-to-end frame→base64 ✔ | Conf/class accuracy on real track footage |
| Dashboard | App boots, `Application started successfully!`, port 8080, components build ✔ | Visual confirmation of all cards + FilePicker in browser |
| ESP32 | Queue, coalescing/debounce, single polling thread, offline/reconnect — M3 harness ✔ | Real hardware commands (forward/stop/speed/estop) |
| GPS | Parsing logic + cache path | Real GPS fix over HTTP |
| GSM | SMS enqueued non-blocking | Real SMS send via hardware |
| Reports | ❌ not tested — generator import fails | After fix, verify PDF output + image embed |
| History | CSV read path works; 90 rows on disk | Live refresh of table |
| Snapshots | Files written + latest-read path ✔ | Display at speed in web UI |

**Automated harnesses:** `C:\Users\Aakash\AppData\Local\Temp\opencode\m3_verify.py` (ESP32 — passed), `m6_verify.py` (camera sources + switching — 21/21 passed), `m6_smoke.py` (UI build — passed).

---

## 14. Hackathon Readiness

| Dimension | Score /10 | Notes |
|---|---|---|
| Architecture | 6 | Good layering + single-owner controller, but dead/legacy files and config split |
| Performance | 5 | ~5 fps YOLO; camera-busy on this machine; offline ESP32 timeouts |
| Reliability | 5 | Thread-unsafe Flet updates; stats bug; report broken |
| UI | 8 | Rich, polished dashboard; some cards stale after mount |
| AI | 7 | Real YOLO inference with 4 crack classes; severity logic sound |
| Hardware Integration | 4 | Well-designed HTTP/queue layer but unproven on real ESP32 |
| Demo Readiness | 6 | Works headless + boots; needs demo video configured + a couple of fixes |
| **Overall** | **6** | Strong demo backbone; fix stats + report + thread-safety to shine |

---

## 15. Final Roadmap (priority order to hackathon)

1. **Fix `StatisticsManager` name matching** (Critical, 15 min) → stats/health/analytics become live.
2. **Fix `report_generator.py` + add "Generate Report" button** (Critical, 1–2 h).
3. **Move Flet updates off background threads** (High, 2–3 h) → prevents web UI freezes.
4. **M5 — consolidate `config.py`** (High, 1–2 h) → remove duplicate-key ambiguity (`CAMERA_INDEX`, `ESP32_IP`, `ESP32_PORT`).
5. **Refresh all dashboard cards each tick** (High, 2–3 h) → numbers stay current.
6. **Load GSM number from `gsm_store` + wire SOS** (Medium, 1 h).
7. **Purge dead/legacy files** (`sms_manager.py`, `mock.py`, `rover_panel.py`, `main.py`, `ui.py`, `test_*`, `esp32.py` shim) (Low, 20 min).
8. **Prepare demo assets** — set `CAMERA_MODE=demo` + `DEFAULT_VIDEO_PATH` to a real track MP4 (10 min).
9. **Hardware rehearsal** — ESP32 rover + ESP32-CAM + GPS + GSM end-to-end (1 day, with hardware).
10. **Polish** — update README, verify PDF, smoke-test in browser (1–2 h).

**Estimated remaining effort to hackathon-ready:** ~2–3 focused dev-days (software) + 1 day with hardware.

---
*Generated from the live codebase. No features claimed beyond what the source implements.*
