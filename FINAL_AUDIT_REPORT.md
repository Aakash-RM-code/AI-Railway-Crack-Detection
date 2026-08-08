# FINAL FULL-STACK ENGINEERING AUDIT — AI Railway Crack Detection System

**Project:** `D:\Python\crack_det_v_1`
**Date:** 08 Aug 2026
**Scope:** FastAPI backend · React/TanStack frontend · REST · WebSocket · YOLO pipeline · Camera/MJPEG · ESP32/GPS/GSM hardware · Storage · Config · Tests · Security/Deployment
**Constraint honoured:** Audit only — no files modified, no redesign/refactor.

---

## 1. Current Architecture

```
┌──────────────────────────  FRONTEND (src/)  ─────────────────────────────┐
│ React 19 · TanStack Start/Router · React Query · Tailwind v4 · shadcn/ui │
│   Dashboard: Layout(Grid) → 12 cards (camera, rover, alert, health, GPS, │
│   GSM, stats, charts, snapshot, history)                                  │
│   Data seam: monitoringApi (services/index.ts) = REST (useLiveQuery)     │
│   Realtime: RealtimeProvider + 3 WS clients (telemetry/detections/       │
│             camera-status) with exponential backoff, merges WS→RQ cache, │
│             REST polling resumes when WS is not "live"                   │
└───────────────────────────────────────────────────────────────────────────┘
                                       │ HTTP (camelCase JSON) + WS (http://…)
┌──────────────────────────  BACKEND (backend/)  ──────────────────────────┐
│ FastAPI app (main.py) + CORS(*, credentials)                             │
│  REST routes /api:  system, camera, detections, hardware, reports        │
│  WS /ws: telemetry, detections, camera-status, stream (hub broadcast)    │
│  Schemas: pydantic BaseCamelModel (camel/snake aliases)                  │
│  Services: CameraPipeline (singleton thread loop) + CameraManager        │
│    (background acquisition) → CrackDetector (YOLO best.pt)               │
│    → AlertManager (SAFE..CRITICAL) → StatisticsManager → DetectionLogger │
│    → HistoryManager; ReportGenerator (reportlab)                         │
│  Hardware: ESP32Controller (thread-safe HTTP, queue+coalescing, polling) │
│  Storage: DetectionRepository (CSV + JPG, singleton) · gsm_store         │
│  Config: config.py (single source of truth) + env overrides             │
└───────────────────────────────────────────────────────────────────────────┘
```
ESP32 rover / ESP32-CAM / GPS(NEO-6M) / GSM(SIM800L) are plain-HTTP devices the backend controls.

## 2. What Is Complete & Verified

**Verified clean (all pass):**
- `pytest tests/ -q` → **31 passed** (backend import graph, config paths, endpoint smoke, WS channel smoke).
- `npx tsc --noEmit` (frontend) → **clean**.
- `npm run lint` → **clean**.
- `npm run build` (Vite + TanStack + Nitro) → **succeeds**, `.output/` generated.

**Functional backend surface:**
- Full REST surface + pydantic camelCase contract with the frontend types (`types/monitoring.ts` mirrors schemas.py).
- YOLO detection pipeline (real model `models/best.pt` present), statistics, alert severity engine, track-health scoring.
- CSV history + JPG snapshot persistence; snapshot serve endpoint; severity trend/distribution analytics.
- PDF report generation (reportlab) — works standalone.
- WebSocket hub with 4 channels, keepalive ping/pong, disconnect cleanup, background broadcaster.
- Clean module decomposition, thread-safe caches (RLock), singleton pipeline/repo, non-blocking ESP32 command queue with per-key debounce (well designed).
- Frontend: good componentization, single data seam, real REST impl, RealtimeProvider with REST fallback, MJPEG player plumbing, mock impl retained behind flag.

## 3. Issues Found (ranked)

### CRITICAL

- **[C1] ESP32 hardware is never wired into the running app.** `CameraPipeline._esp` is set from `get_pipeline(esp32_controller=None)` and nothing passes a controller (`backend/services/camera.py:525-531`; `main.py` never constructs `ESP32Controller`). Verified live: `pipeline._esp → None`. All hardware endpoints silently succeed with fake data:
  - `GET /api/gps` always returns hardcoded `12.923456,80.123456` with `hasFix:false` (`hardware.py:28-29`).
  - `POST /api/gsm/send-sms` returns `{"ok": true, "message": "Mock SMS dispatcher"}` without sending anything (`hardware.py:60-61`).
  - Rover commands, GPS polling, GSM, auto-E-stop on CRITICAL all no-op. Any real-hardware run is impossible today.
  - Tests even assert `ok:true` for SMS (`test_phase1_endpoints.py:75-79`), cementing the mock as expected behaviour.

**Live verification:** `POST /api/camera/connect {"source":"esp32cam"} → 422`; `{esp32-cam} → 200`; `demo → 422`; `demo-video → 200`. Also `pipeline._esp → None`, gps returns coords with `hasFix:false`.

** [C2] Camera-source contract mismatch — UI cannot switch sources.** Frontend `toBackendSource()` (`restMonitoringApi.ts:91-95`) sends `esp32cam`/`demo` strings, but backend `CameraSource` enum accepts only `usb`/`esp32-cam`/`demo-video` (`schemas.py:56-60`). Clicking "ESP32-CAM" or "Demo Video" in the UI → **422 validation error**, so multi-source switching fails. The backend’s own `_map_source_to_backend` (`camera.py:15-20`) shows the intended direction — the frontend contradicts it.

** [C3] Live camera feed is never shown in the dashboard.** `CameraFeedCard.tsx:55-72` renders a static placeholder icon when "live"; `MjpegPlayer.tsx` is **completely unused** (only its own definition references it). `streamUrl` is exposed by the API but never consumed. The headline feature — live video — displays nothing.

** [C4] Snapshot images break across origins.** `LatestSnapshotCard` uses `<img src={data.image_url}>` where backend returns a relative `/api/detections/snapshot-image/...` (`repository.py:233`). No dev proxy is configured, frontend and backend run on different ports → `localhost:8080/api/...` 405/404. (Same class of bug affects `camera` websocket URL behind `streamUrl`.)

** [C5] No security on a hardware-control API (production loader).** Zero authentication/authorization on any endpoint (`/api/rover/command`, `/api/gsm/send-sms`, `/api/camera/*`, report generation). CORS is `*`+`allow_credentials=True` (`main.py:24-30`) — invalid for credentialed browsers and effectively open. Anyone who can reach the host can drive the rover, send SMS, and generate reports.

### HIGH

**[H1] Port/config chaos — the integration can’t start out of the box.**
- Backend docs/README run on **8080** (`docs/BACKEND_OVERVIEW.md:28`, README); frontend defaults to **8000** (`endpoints.ts:5-9`) and the Vite dev server binds **8080** (verified in `dev-server.log`, `frontend/README.md:23`). So backend-8080 and frontend-8080 collide when run together, and the default API/base URL (8000) points at nothing.
- `.env.example` sets `VITE_WS_BASE_URL=ws://localhost:8000/ws`, but the WS client already appends `/ws/${channel}` (`client.ts:78`). Copying `.env.example` → `.env` produces `ws://…/ws/ws/telemetry` → connection failure. Two different "descriptions" of the same URL.

** [H2] Rover speed/control logic is broken in the real path.**
- `RoverControlCard.tsx` slider `onValueChange` sends `{ command: "stop", speed }` (line 82) — every slider drag issues `stop`, so you can never set speed without stopping the rover.
- Backend `send_rover_command` handles only FORWARD/BACKWARD/STOP/EMERGENCY_STOP (`hardware.py:100-120`); **LEFT and RIGHT in the UI’s D-pad are silently ignored** (enum has them, `schemas.py:62-69`).
- Speed scale mismatch: frontend slider is 0-100, backend/RoverState speed is 0-255 (default 150); the dashboard will show `150` yet the UI clamps to 100.

** [H3] GPS/SMS telemetry shows fake data instead of error.** `telemetry_broadcaster_task` and `/api/gps` both synthesize `12.923456,80.123456` + signal `85.0` / "Cellular IoT Gateway" when there is no fix (`websocket.py:170-177`). The operator can’t distinguish telemetry from hallucination; a live-but-fixed monitor would look "healthy".

** [H4] Untracked runtime state leaks / no lifecycle wiring.** No startup task connects the hardware/pipeline; nothing starts or stops the capture pipeline or ESP32 on app lifecycle; broadcaster accesses `pipeline._esp` private attribute — brittle coupling to a field that is currently None by construction.

### MEDIUM

- **M1** — Websocket `/ws/stream` re-pushes the full `frame_base64` on every client ping (`websocket.py:126-135`); large (hundreds of KB) per-message with a legacy endpoint the frontend no longer uses. Bandwidth hazard.
- **M2** — `HttpPost` in `restMonitoringApi.ts` retries 0 times while `httpGet` retries 2; POSTs to a flaky backend surface errors with no resilience.
- **M3** — `DetectionRepository` is a singleton but `__new__`/`__init__` allows callers to pass different csv/dir/cooldown; the second+ callers get the same instance with the first caller’s settings, silently `cooldown` etc. ignored (`storage/repository.py:61-80`).
- **M4** — `GET /api/state` (legacy route, `routes/__init__.py`) returns the raw runtime dict incl. full base64 frame on every poll — heavy, unused by the new UI.
- **M5** — Snapshot `get_latest_snapshot()` is scan-`glob` + CSV re-read on every poll/WS broadcast — acceptable with small CSVs but O(n) each time; snapshot cards poll every 10-15 s.
- **M6** — WS camera-status payload (`websocket.py:182-192`) uses `mode: "demo"`/`usb`/`esp32cam`, but frontend `mapCameraStatus` maps exactly those strings — **OK**, but it promises a closest-coupled-looking mapping that will silently degrade if the backend mode strings change in `config.CAMERA_MODE`.

### LOW
- **L1** — No CI config (no `.github/workflows`), tests/lint/typecheck/build only run manually.
- **L2** — `architecture` `requirements.txt` unpinned (open versions) — build reproducibility risk.
- **L3** — Dead/unused artifacts: `MjpegPlayer.tsx`, mock API shipped (flag off) and bundled, legacy `RuntimeState`/`SpeedRequest` schemas, `WS_CHANNELS.videoFeed`, `command` "left/right" UI but no backend → few bits.
- **L4** — Report raises `ReportResponse.path` (server filesystem path) to the frontend; minor info leak.
- **L5** — No backend test for: report PDF content, camera pipeline detection, pivot stats math, ESP offline behavior, `detections` filtering/`search`/`688`.

## 4. Production Blockers (ranked)

1. **[C1]** Robot/GSM/GPS never connected → the product simply does not function with real hardware.
2. **[C2]** Camera-source switching from UI impossible (422) — cannot select hardware ESP32-CAM source.
3. **[C3]** Live video never rendered in the dashboard — core feature missing.
4. **[H2]** Rover controls mis-handled (stop-onspeed-slider, left/right ignored, scale mismatch) → dangerous/unreliable remote control.
5. **[C5]** Zero auth on physical control endpoints → production liability.
6. **[H1]** Port/config mismatch → app cannot be started correctly by following the documented steps.
7. **C4/M** relative snapshot URLs broken across origins → history/media unusable in typical deployment.

## 5. Recommended Fixes (priority order)

1. **Wire ESP32Controller into the app** — construct `ESP32Controller(BASE_URL)`, `start_polling(POLLING_INTERVAL)`, pass it into `get_pipeline(esp32_controller=esp)` at startup, close on shutdown; remove "Mock" success paths so the absence of hardware is visible, not recycled as success.
2. **Align camera-source contract.** Frontend `toBackendSource()` should emit `"esp32-cam"`/`"demo-video"` (or the backend should accept its own pho); then update the `CameraSource` mapping test to include both directions.
3. **Render the live feed** — use `Mul`/`forEach` only when `live`; consume `CameraState.streamUrl` (absolute backend URL) or complete the precedent with an `<img src>` on the MJPEG endpoint; delete/hide the static placeholder when live.
4. **Fix rover controls** — split “set speed” from “command” (slider should call set-speed only), implement `LEFT`/`RIGHT` on backend or remove from D-pad, align speed scale (100 vs 255), fix E-Stop release semantics.
5. **Make telemetry honest** — when no ESP/GPS fix/SMS, send real `offline`/`hasFix:false` states and empty coords instead of hardcoded values; have the frontend show "no fix" state (a higher fidelity) rather than coordinates.
6. **Fix ports + WS URL** — single source of truth for backend port (recommend 8000 loi), update `.env.example` to `ws://localhost:8000` (no trailing `/ws`), point frontend default at the same host, document both dev servers.
7. **Add authN/authZ** (API token/HMAC + allowlist + admin-only for rover/SMS/E-stop), tighten CORS (`allow_credentials=False` with explicit origins or a reverse proxy).
8. **Paths** — serve snapshot/report/download via absolute backend URLs or a Vite `server.proxy` for `/api`.
9. **Cleanups** — remove unused schemas/components/`videoFeed`, pin `requirements.txt`, add CI (pytest + tsc + eslint + vite build), add a `pre-commit` hook, add tests for: source mapping, rover commands, report generation, WS push→RQ merge, snapshot filtering/pagination.

## 6. Overall Readiness Score

**5.5 / 10**

- **Code quality/build hygiene:** strong — everything compiles and the test suite passes.
- **Architecture:** solid modular separation; data seam + WS/REST fallback is well designed.
- **Integration reality:** unplugged ** (core — hardware & live render never wired, ports/contracts broken).
- **Security/deployment:** not ready for any exposure (no auth, star CORS, config drift).

The system is a **well-engineered internal scaffold/demo**, not yet a deployable hardware loop. With the 1-4 fixes (wiring ESP32, camera-source contract, live feed render, rover control) plus ports/security it would reach ~8/10.

---
*Generated during a read-only audit. No project files were changed.*