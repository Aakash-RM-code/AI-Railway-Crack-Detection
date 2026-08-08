# Project Handoff — AI Railway Crack Detection System

> **Purpose of this file:** self-contained context for an agent new to this codebase.
> Inspected from the live repo on 08-Aug-2026. If anything below disagrees with the
> code, trust the code and update this document.

---

## 1. Project overview

An AI-powered railway crack inspection system. A live camera streams rail footage;
a YOLOv8 detector classifies defects (cracks / broken chains) **in real time**; the
backend logs detections, saves snapshot images, tracks health/statistics, generates
PDF reports, and relays rover/emergency-stop commands to an ESP32 rover over Wi-Fi.

Hardware (ESP32 rover, ESP32-НаCAM, NEO-6M GPS, SIM800L GSM) is *optional*; the system
degrades gracefully to "offline / unavailable" state when hardware is absent. The
current focus is the **FastAPI backend + React frontend + detection pipeline**.

Gotchas for a newcomer: the system's priority is **detection reliability over FPS** —
several past optimizations were rejected because they reduced small-crack recall. See
§12.

---

## 2. Current architecture

```
D:\Python\crack_det_v_1\
├─ config.py                  # single source of truth for ALL paths/settings/env
├─ models/
│  ├─ best.pt                 # canonical PyTorch YOLO weights (source of truth)
│  └─ best_openvino_model/    # OpenVINO IR export (best.xml / best.bin / metadata.yaml)
├─ backend/
│  ├─ main.py                 # FastAPI entrypoint: startup/shutdown wiring, CORS
│  ├─ detector/detector.py    # CrackDetector: OpenVINO + PyTorch fallback + warmup
│  ├─ services/
│  │  ├─ camera.py            # CameraManager (source+acq thread) + CameraPipeline (loop)
│  │  ├─ alert_manager.py     # conf/severity from best box
│  │  ├─ statistics_manager.py# per-class counters
│  │  ├─ logger.py            # thin wrapper -> DetectionRepository
│  │  ├─ history_manager.py   # legacy CSV reader
│  │  └─ report_generator.py  # PDF reports (reportlab)
│  ├─ hardware/esp32.py       # ESP32 controller wrapper (poll, GPS, GSM, rover cmds)
│  ├─ hardware/gps.py, gsm.py # wrappers around ESP32 caches
│  ├─ storage/repository.py   # DetectionRepository singleton (CSV + snapshot JPG)
│  ├─ utils/imaging.py        # cv2_imencode + jpeg_base64
│  └─ api/
│     ├─ routes/__init__.py   # /api prefix, legacy /api/state
│     ├─ routes/{system,camera,detections,hardware,reports}.py
│     ├─ websocket.py         # /ws channels + telemetry_broadcaster_task
│     ├─ auth.py              # optional Bearer-token guard
│     └─ schemas.py           # pydantic camelCase models
├─ detections/, logs/, reports/, uploads/, assets/
├─ frontend/                  # React 19 + TanStack Router + Vite + Tailwind
│  └─ src/{routes,components,services,config,endpoints}
└─ tests/                     # unittest suite (pytest-compatible)
```

### Backend flow (REST & WS)
- `uvicorn backend.main:app --host 0.0.0.0 --port 8080`
- Routes are `/api/...`; WebSockets `/ws/{telemetry,detections,camera-status,stream}`.
- `get_pipeline()` in `backend/services/camera.py` is a **process-wide singleton**
  returning `CameraPipeline`. It lazily creates `CameraManager` inside its own thread
  loop (`_camera_loop`).
- Data leaves the pipeline through `CameraPipeline.get_state()`, `get_frame_base64()`,
  `get_alert()`, etc. WebSocket broadcasts are pulled from these accessors.

### Frontend (TypeScript, TanStack Router + Start)
- Endpoints map: `frontend/src/config/endpoints.ts`. API base `http://localhost:8080`.
- MJPEG player in `frontend/src/components/features/camera/`.
- Build: `npm run build` (Vite + Nitro). Lint: `npm run lint`. Types: `npx tsc --noEmit`.

---

## 3. Current ML model

- **Task:** YOLOv8 detection, 4 classes (Ultralytics `model.names`):
  `{0: "broken chain", 1: "large crack", 2: "medium crack", 3: "small crack"}`.
- **Canonical weights:** `models/best.pt` (21.5 MB). **Never delete or replace**; it is
  the fallback backend and the source for re-export.
- **Inference backend (default):** **OpenVINO** — `models/best_openvino_model/`
  (42.8 MB IR). Selected when `INFERENCE_BACKEND=openvino`.
- **Inference settings (must stay fixed):** `imgsz=640`, `conf=0.70`
  (`config.INFERENCE_IMGSZ`, `config.CONFIDENCE_THRESHOLD`). Both passed **explicitly**
  in `CrackDetector.detect()` from config — never rely on Ultralytics defaults.
- **Fallback behavior:** if OpenVINO load fails (missing runtime or export dir),
  `CrackDetector` falls back to `YOLO(config.MODEL_PATH)` (PyTorch `best.pt`) and sets
  `self.backend = "torch"`. Also forced with `INFERENCE_BACKEND=torch`.
- **Warmup:** `CrackDetector.warmup()` runs one 640x640 empty-frame inference to absorb
  the OpenVINO compile (`~4.7 s`) at construction time; called from
  `CameraManager.__init__` so the first live frame is never compile-stalled.
- **Measured performance:** OpenVINO ~80–90 ms/frame (~12–13 FPS);
  PyTorch ~140 ms/frame (~7 FPS).

---

## 4. Camera / streaming pipeline (core of current debugging)

1. `CameraManager(mode)` opens a source (usb | esp32cam | demo). For USB:
   `cv2.VideoCapture(config.CAMERA_INDEX)` — note **no explicit backend flag**
   (OpenCV auto-picks; see §7 warning). Resolution 640x480 BGR. A dedicated
   `_acquire_loop` thread reads frames into `_latest_frame`.
2. `CameraPipeline._camera_loop` (its own thread) runs:
   `read_frame() → result = CameraManager.process_frame(frame) →
   jpeg_base64(annotated)` → stores `_frame_base64` + fps + resolution + alert + stats
   in-memory (all under `self._lock`).
3. `process_frame` (CameraManager):
   - `detector.detect(frame)` → Ultralytics result (BGR in)
   - `alert_manager.process(results, model.names)` → severity/class/message
   - `results[0].plot()` → annotated BGR image
   - if any boxes: `logger.save_detection(...)` (snapshot JPEG + CSV row, 3 s cooldown via `DetectionRepository`)
   - returns `{"frame": annotated, "alert": alert, "stats": stats}`
4. **Streaming:** `GET /api/camera/stream` returns
   `StreamingResponse(_mjpeg_generator(), media_type="multipart/x-mixed-replace; boundary=frame")`.
   The generator polls `pipeline.get_frame_base64()`, base64-decodes, and yields
   `--frame\r\nContent-Type: image/jpeg\r\n\r\n <bytes>` every `time.sleep(0.04)` (~25 FPS).
   Browser `<img src="/api/camera/stream">` renders it.

**Critical invariant:** `_frame_base64` is updated **only** after a full pipeline
iteration succeeds **and** `jpeg_base64()` returns non-empty. If any step throws, the
exception is caught in `_camera_loop` (sets `_camera_error`) but **the MJPEG generator
keeps running and yields nothing** → HTTP 200 with a black/blank browser frame. This is
the "black frame" hairline.

---

## 5. Recent changes — OpenVINO integration

Verified in this workspace (against prior commit `dd4fb20` + uncommitted modular refactor):

| File | Change |
|---|---|
| `backend/detector/detector.py` | Rewritten `CrackDetector`: backend select from `config.INFERENCE_BACKEND`; OpenVINO (default) or PyTorch; auto-fallback to `best.pt`; explicit `imgsz=640`, `conf=0.70`; added `warmup()`; preserves `.model.names` |
| `config.py` | Added `INFERENCE_BACKEND` (env default `openvino`), `INFERENCE_IMGSZ=640`, `OPENVINO_MODEL_PATH` |
| `backend/services/camera.py` | One line in `CameraManager.__init__`: `self.detector.warmup()` |
| `requirements.txt` | Added `openvino` |
| `models/best_openvino_model/` | Added OpenVINO IR exported from `best.pt` @ imgsz=640 |

No changes to frontend, API routers, WebSockets, ESP32/GPS/GSM, or overall architecture.

---

## 6. Current verified state

- `pytest tests/ -q` → **39 passed, 2 subtests passed** (+1 Starlette/httpx warning).
- `npx tsc --noEmit` → exit 0.
- `npm run lint` → exit 0.
- `npm run build` (frontend) → exit 0 (~807 ms).
- Detector import OK · OpenVINO backend loads (`backend = openvino`, LATENCY mode, CPU)
  · PyTorch fallback via `INFERENCE_BACKEND=torch` OK · simulated missing OpenVINO dir
  auto-falls back to `best.pt` with warning · warmup completes.
- **Inference (imgsz 640, conf 0.70):** OpenVINO ~80–90 ms/frame (~12–13 FPS);
  PyTorch ~140 ms/frame (~7 FPS). Parity verified on 52-image valid/test set (~0.98 box
  IoU, class drift nil).
- **Smoke test (CAMERA_MODE=demo):** pipeline connects, captures frames, `process_frame`
  detects a small crack, alert → LOW, annotated+JPEG produced, `logged=True`.
- **Backend diagnostic this session:** USB cam `opened=True, read=True, shape (480,640,3)`;
  pipeline `running=True, fps=3.6, error=None`; `_frame_base64` populated → valid JPEG.

---

## 7. Current known issues

**Expected behavior (not bugs):**
- No frames (webcam unplugged, ESP32-CAM offline): after a 3 s no-frame timeout
  `_camera_error` is set, MJPEG returns 200 with no frames (black frame). Expected
  behavior for a disconnected camera.

**Actual / observed:**
- `/api/camera/stream` returns 200 but Chrome shows a **black frame** while the webcam
  is physically **disconnected / unplugged** (the current live-test state). The
  diagnostic proves the pipeline produces valid JPEG frames when the USB cam is
  connected, so the black screen today is consistent with "no camera frames reaching
  the MJPEG", not a detection defect.
- `CameraPipeline._camera_loop` swallows exceptions to `_camera_error` only; nothing
  logs the exact failing stage for the stream path.
- OpenCV prints `WARN: ... VIDEOIO(MSMF): backend ... can't be used to capture by index`
  on Windows. Harmless noise — but passing `CAP_DSHOW` explicitly for USB (not yet
  done) is the recommended deterministic fix.
- `_frame_base64` is only refreshed on pipeline success; if a consumer decodes an empty
  string it yields nothing (no reset/heartbeat JPEG).

---

## 8. Configuration / environment

- **Python:** 3.11.0 at
  `C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe`.
- **Runtime deps:** ultralytics, openvino, opencv-python, numpy, reportlab, requests,
  fastapi, uvicorn, pydantic. Test deps incl. httpx/pytest.
- **Model paths:** `models/best.pt` (canonical), `models/best_openvino_model/` (OV IR).
  Do not delete `best.pt`.
- **Environment variables** (see `config.py`, all read at import time):
  `CAMERA_MODE` (usb|esp32cam|demo), `CAMERA_INDEX` (0), `CAMERA_WIDTH/HEIGHT`
  (640x480), `DEFAULT_VIDEO_PATH` (demo), `INFERENCE_BACKEND` (openvino|torch),
  `ESP32_ENABLED`, `ESP32_IP`, `ESP32_PORT`, `ESP32_BASE_URL`, `POLLING_INTERVAL`,
  `APP_ENV` (default "development"; "production" requires `API_AUTH_TOKEN`),
  `CORS_ALLOWED_ORIGINS`, `API_AUTH_TOKEN`.
- **Commands:**
  - Backend: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080`
  - Tests: `python -m pytest tests/ -q`
  - Frontend: `cd frontend; npx tsc --noEmit; npm run lint; npm run build`
  - Re-export OpenVINO:
    `python -c "from ultralytics import YOLO; YOLO('models/best.pt').export(format='openvino', imgsz=640)"`

---

## 9. Important design decisions

1. **Single source of truth (`config.py`)** — all paths/settings derive from
   `PROJECT_DIR`; env overrides; no hardcoded paths in app code.
2. **Keep `imgsz=640` fixed.** Lowering to 416/320/512 collapsed small-crack recall in
   a controlled benchmark (§12). Never reduce it.
3. **OpenVINO over PyTorch by default** — 1.5–1.7× faster, verified equivalent (same
   classes, ~0.98 box IoU, conf drift ≤0.007) on 52 annotated frames; PyTorch kept as
   fallback (env or auto).
4. **Warmup at construction** — `CrackDetector.warmup()` (compiles OV) before live
   frames so the first frame is not stalled.
5. **Explicit `imgsz=`/`conf=`** in `detect()` — never trust Ultralytics defaults.
6. **Singleton pattern** (`get_pipeline`, `DetectionRepository.__new__`/`_instance`) to
   avoid duplicate camera/model state.
7. **Honest hardware reporting** — no fabricated coords/signal; offline = DISCONNECTED /
   503. Never fake success.
8. **No frontend/architecture churn** — detector refactor must keep
   `CrackDetector.detect(frame)` signature + `.model.names`.

---

## 10. What remains to be done (next logical stages)

1. **Black-frame root cause (the active task).** Reproduce `/api/camera/stream` with the
   USB camera **physically connected**. Confirm the backend actually yields JPEG bytes
   (check `_frame_base64` length while streaming). If yes → browser/MPJPEG boundary
   issue; if no → trace the failing stage (§4 step 2/3).
2. Add **temporary diagnostics** (or keep permanent) to log the failing stage; verify
   `boundary=frame` matches the client's expectation.
3. Consider **explicit `cv2.VideoCapture(index, cv2.CAP_DSHOW)`** for USB to silence the
   MSMF warning and make capture deterministic.
4. **Re-run the 52-frame parity validation** after any change to keep OpenVINO ≃ PyTorch.

---

## 11. How another agent should continue

1. Read **`config.py`** then **`backend/services/camera.py`** (the whole pipeline),
   **`backend/detector/detector.py`**, **`backend/api/routes/camera.py`** (MJPEG),
   **`backend/utils/imaging.py`**.
2. For debugging prefer **read-only diagnostics in temp scripts**
   (`C:\Users\Aakash\AppData\Local\Temp\opencode`) over editing source; run
   `python -m pytest tests/ -q` after each change.
3. When fixing the black-frame camera: add logging, then make the smallest safe change
   (e.g. explicit `CAP_DSHOW` or a populated `_frame` fallback JPEG). Do **not** touch
   OpenVINO config, `imgsz`, `conf`, `best.pt`, or frontend unless asked.
4. Register new files/behavior with `config.py`; keep `get_pipeline()` singleton.

---

## 12. Known pitfalls / history (do not repeat)

- **Do NOT lower `imgsz` below 640.** A controlled benchmark showed 512/416/320 lose
  small cracks entirely — past lesson of this project.
- **Don't silently drop the PyTorch path.** Several prior "speedup" attempts (FPN+
  imgsz) failed on recall; OpenVINO is the approved speedup. Keep the fallback.
- **Don't reinvent the pipeline flow.** `process_frame` → annotated → `frame_base64`
  coupling is used by API, WS, snapshots, and reports; change the lock/update in one
  place and all consumers break.
- **The MJPEG "black frame" was already traced to "no frames flowing from camera"** —
  do not rewrite the streaming layer. Add a fallback heartbeat JPEG + logging, keep
  `imgsz=640`, touch only the backend camera path.

---

**Estimated newcomer effort:** ~1–2 hours read-through + a diagnostic script for the
camera black-frame.