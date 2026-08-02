# PROJECT AUDIT — Railway Crack Detection System

**Document type:** Production‑readiness engineering audit (read‑only — no files modified)
**Date:** 02 August 2026
**Root directory:** `D:\Python\crack_det_v_1`
**Stack:** Python 3.11 · Flet 0.86.4 · Ultralytics YOLO · OpenCV 4.13 · ReportLab · requests/urllib3
**Baseline document:** `PROJECT_STATUS_REPORT.md` (older snapshot — several items below are now superseded)

> Audit reflects the **current codebase on disk** as inspected. Symbols: ✔ fully implemented / ⚠ partially implemented / ✗ not implemented or broken. Nothing is assumed.
> Live-state observation: the Flet web app is currently running (PID 15148 alive, serving HTTP on localhost:8080, `logs/detections.csv` growing). This audit did not launch or touch it.

---

## 1. PROJECT OVERVIEW

A real‑time railway crack detection and rover‑control system:

- **Detection:** YOLO (`best.pt`, 4 classes: small crack / medium crack / large crack / broken chain) with severity classification (SAFE → CRITICAL, confidence gate 0.70) and annotated frame output.
- **Camera sources:** USB webcam, ESP32‑CAM (MJPEG with snapshot fallback), and demo video — with live switching, reconnect, and demo‑file picking (M6 complete).
- **Rover control:** HTTP ESP32 client with a non‑blocking command queue, coalescing/debounce, single polling thread; D‑pad, speed slider + presets, emergency stop; auto E‑stop on CRITICAL alert.
- **Telemetry:** GPS (cached, parsed lat/lon) and GSM/SMS (enqueued to ESP32 module).
- **UI:** Flet web dashboard on `http://localhost:8080` — dark theme, single instance lock, bounded viewport layout, 10 Hz live refresh.
- **Deliverables:** PDF inspection reports, CSV detection history, annotated JPG snapshots.

**Milestone history (git):** `e0c6535` legacy v1.0 (YOLO + OpenCV + ESP32 LED) → `6021626` centralized config → uncommitted M1–M6 refactor (ui/, backend/, camera_manager) + the recent bounded‑layout repair.

**Estimated completion:** ~78% (up from ~75% in the baseline report: statistics bug fixed, report generator fixed and wired, config consolidated, dashboard layout stabilized).

| Architecture maturity | 7/10 |
|---|---|
| Strongest areas | Layered single‑owner design; real YOLO inference; production‑grade ESP32 queue layer; live dashboard |
| Weakest areas | No automated tests; hardware unproven; dead/legacy files; Flet thread model; SOS + SMS honesty bugs |

---

## 2. CURRENT FEATURES (✔ / ⚠ / ✗)

| Feature | Status | Notes |
|---|---|---|
| USB camera source | ⚠ | Opens + thread acquisition ✔, but on this machine MSMF `can't grab frame` (environmental — see Performance) |
| ESP32‑CAM source | ✔ | MJPEG stream + snapshot fallback, Reconnect button (M6 harness 21/21) |
| Demo video source | ✔ | MP4, loops on EOF, FilePicker persists bytes to `uploads/` |
| Live source switching | ✔ | `set_camera_source()` stop→release→init→auto‑continue; Connect/Disconnect/Reconnect buttons |
| YOLO detection (4 classes) | ✔ | Annotated frames, confidence, class names with spaces |
| Alert severity engine | ✔ | Best box ≥0.70 → SAFE/LOW/MEDIUM/HIGH/CRITICAL + message |
| Statistics counters | ✔ | **Fixed** — `statistics_manager.py:17` normalizes `"_" → " "` so `"small_crack"` now matches `"small crack"` |
| Track health scoring | ✔ | Derives from live stats (score/status/note), refreshed every tick |
| Detection history (CSV) | ✔ | `logs/detections.csv` (474 rows) read via `controller.get_history()`; table live |
| Snapshot saving | ✔ | `detections/` — 402 JPGs; latest snapshot card live at 10 Hz |
| PDF report generation | ✔ | **Fixed** — no more `gui_components` import; reads CSV/detections directly; wired to Footer "Generate Report"; 9 PDFs already generated |
| ESP32 command queue | ✔ | `submit()` non‑blocking, coalescing + debounce (speed 0.2 s), single polling thread (M3 harness passed) |
| Rover controls | ✔ | F/B/Stop, speed slider + presets, E‑stop; online/offline indicator; speed slider syncs immediately (`.update()` calls) |
| Auto E‑stop on CRITICAL | ⚠ | Code path armed/triggered in `controller.py`; never fired in tests (no hardware) |
| GPS read (cached) | ⚠ | Parsing + cache logic ✔; no hardware fix → UI shows "📍 Waiting for GPS..." / N/A (correct placeholders) |
| GSM/SMS send & test | ⚠ | Enqueued non‑blocking ✔; **result always reported as success** (see Bugs) |
| GSM phone persistence | ⚠ | `gsm_store.py` saves/loads `config/gsm_settings.csv`; **not wired into GSMCard** (default never loaded) |
| Video recording | ✗ | `SAVE_VIDEO` flag exists in older config only — no implementation |
| Streamlit dashboard | ✗ | README mention only; Flet chosen instead (dead requirement) |
| Hardware validation (ESP32/CAM/GPS/GSM) | ✗ | Never exercised — everything runs offline path |
| Automated test suite | ✗ | Only trivial `test_alert.py`; `test_esp32.py` is broken legacy |

---

## 3. UI REVIEW

### Layout (current, after bounded‑layout repair)
`dashboard.py` root = `Container(expand)` → `Column` → [Header / **Middle 3‑column Row (expand)** / KPI strip / Footer].
No page‑level scrolling — the only internal scroll is inside the Detection History table. All cards bounded; columns are `Column(expand=True)`; the camera preview expands only inside its own card. Viewport‑filling, header/footer fixed, KPI strip fixed above footer.

- **LEFT (expand=4):** Camera (fills remaining) → GPS (height=185) → GSM (height=215)
- **CENTER (expand=3):** Rover Controls → Alert Status (LIVE)
- **RIGHT (expand=3):** Track Health → Detection History (internal scroll) → Latest Snapshot (height=200)
- **KPI strip:** 6 counters (total / small / medium / large / broken / critical) — live
- **Footer:** version, "Generate Report" button (works), session start, developer

### Live refresh
`_refresh_loop` (single daemon thread, 0.1 s) calls `update()` on **all 11 components** each tick: header, camera, snapshot, rover, statistics, health, alert, analytics, history, GPS, GSM. The baseline report's "cards stale after mount" issue is **resolved** — every card now refreshes live. Header clock + ESP/GPS/GSM dots updated via the same loop (no background clock thread → the old header thread‑safety bug is gone).

### Component status
| Component | Status | Notes |
|---|---|---|
| Header | ✔ | Live clock, ESP/GPS/GSM connection dots, title/badges |
| CameraCard | ✔ | Live feed, FPS/res badges, status pill, source panel (dropdown/Connect/Disconnect/Browse/Reconnect) |
| AlertCard | ✔/⚠ | Live severity pill/class/confidence bar/message; **SOS button is a no‑op** |
| StatisticsCard | ✔ | 6 KPIs, live |
| HealthCard | ✔ | Ring + status + note, live |
| HistoryTable | ✔ | Last‑10, colored crack types, scrolls internally, refreshes on CSV change |
| SnapshotCard | ✔ | Latest flagged JPG, live |
| AnalyticsPanel | ✗ | **Created but never mounted** in the current 3‑column layout (charts not visible) |
| GPSCard | ⚠ | Live update; correct "Waiting for GPS..." / N/A placeholders; legacy colors (ft.Colors vs Palette) |
| GSMCard | ⚠ | Live online/offline pill; form works; **always claims "✅ SMS sent"**; phone default not loaded; `max_lines=1` while `multiline=True` |
| RoverControlCard | ✔ | D‑pad (F/B live, L/R shown disabled), speed slider + presets, E‑stop, status/IP/hint ("Disconnected — local preview only" / "Synced with ESP32"); speed updates immediately |
| Footer | ✔ | Static info + working Report button |

### UI issues found
1. **AnalyticsPanel unmounted** — instantiated in `Dashboard.__init__` and `update()`d every tick, but `build_distribution()`/`build_severity()` are never called → the two charts exist in code but are invisible. Regression introduced during the layout repair.
2. **SOS button dead** — `alert_card.py:67` `on_click=lambda e: None`.
3. **GSM "Send SMS"/"Send Test" always show success** — `controller.esp_send_sms()` returns `True` unconditionally (command is queued, delivery unknown).
4. Emergency‑stop dialog claims "GPS recorded, SMS sent" without verification.
5. Style drift: GPS/GSM cards use raw `ft.Colors.*`; the rest use `Palette.*`. `ft.icons.Icons` vs `ft.Icons` mixed (both valid in 0.86.4, inconsistent).
6. Header "SYSTEM READY" pill is static (`set_status` never called).

---

## 4. CODE QUALITY

### Architecture (good)
- Clean layered flow: `app.py` → `Dashboard` → `AppController` (single orchestrator, owns camera loop + ESP32) → `CameraManager` / `ESP32Controller`.
- Process‑wide singleton (`get_controller`) so N browser tabs share one camera loop + one polling thread — correct for Flet web mode.
- RLock‑protected state caches; commands never run on the UI thread.
- Flet helpers (`section_card`, `status_pill`, `kpi_card`, `Palette`) keep the UI consistent and concise.

### Problems
- **Dead code:** `sms_manager.py` (empty), `ui/mock.py` (unused), `ui/components/rover_panel.py` (never mounted), `controller._notify_ui_update()` / `get_ui_state()` (references a method that does not exist — latent `AttributeError` if ever invoked), `controller.set_ui_update_callback()` (no callers), `esp32.py` root shim, `main.py`, `ui.py`, `test_esp32.py`, `test_alert.py`.
- **Duplication:** detection logged once per box *and* once for the best box (`camera_manager.process_frame:189-217`, masked by logger cooldown); GPS/GSM cards re‑implement legacy styling; two rover panels exist.
- **`sys.path.append` hacks** in `rover_control_card.py:11` and `backend/esp32.py:18` — should rely on the project being on the path.
- **Indentation quality:** `camera_manager.process_frame` and `logger.py` have misaligned continuation lines (syntactically valid, hard to read).
- **Unused deps in `requirements.txt`:** `streamlit`, `pandas`, `pyserial` are not used by the live path.
- **Unused assets:** `models/yolov8n.pt` (generic 6.5 MB download) — `MODEL_PATH` is `best.pt`.
- **No tests, no CI, no linter config**, inconsistent type hints/docstrings.
- **README outdated** (describes OpenCV legacy + Streamlit + ESP32 LED as current/future).

---

## 5. PERFORMANCE

| Metric | Observed / Estimate |
|---|---|
| YOLO inference | ~0.2 s/frame steady (~5 fps effective); first call ~10 s warm‑up; acquisition decoupled, processing is the bottleneck |
| UI refresh | 10 Hz `page.update()` even when nothing changed — Flet web re‑render churn; unnecessary on idle |
| Snapshot reads | `get_latest_snapshot()` globs + re‑reads newest JPG and base64‑encodes **every 100 ms** from disk — avoidable IO |
| ESP32 offline | 3 s timeout × (`/status` + `/gps`) every 2 s = up to ~1.5× poll time spent blocked waiting; retries add more. Coalescing/debounce keeps command spam low |
| Memory | Low — only latest frame + base64 retained; no frame buffering |
| Threads | ~4 persistent: `_camera_loop`, `CameraAcquisition`, `ESP32PollingThread`, `Dashboard._refresh_loop` |
| Machine‑specific | **USB camera fails on this machine** — `CvCapture_MSMF::grabFrame can't grab frame` spams `app_error.log`; use `CAMERA_MODE=demo` (with a track MP4) or ESP32‑CAM for demos here |

---

## 6. KNOWN BUGS

### Critical
- None — the app boots, serves, detects, logs, and generates PDFs without crashes. (Verified live: HTTP 200s, growing CSV, 9 reports.)

### High
| # | Bug | Location | Fix |
|---|---|---|---|
| H1 | **SOS button is a no‑op** — press does nothing | `ui/components/alert_card.py:67` | Wire to `esp_emergency_stop()` + GPS capture + SMS |
| H2 | **SMS send/test always reports success** even when ESP32 is offline or delivery fails (command is queued; result discarded) | `ui/controller.py:209-215`, `ui/components/gsm_card.py:188-204` | Surface async delivery status; block/disable when offline |
| H3 | **Analytics charts invisible** — panel instantiated + refreshed but never added to layout | `ui/dashboard.py:43,82`, `ui/components/analytics.py` | Mount `charts_panel` (e.g., bottom of CENTER column or above KPI strip) |

### Medium
| # | Bug | Location | Notes |
|---|---|---|---|
| M1 | Flet controls updated from a non‑main thread (`_refresh_loop` calls `page.update()` at 10 Hz) | `ui/dashboard.py:65-86` | Works today; against Flet guidance; intermittent web‑UI risk |
| M2 | `_notify_ui_update()` calls nonexistent `get_ui_state()` | `ui/controller.py:374-381` | Dead today; crash if ever invoked — remove |
| M3 | Detection double‑logged (every box, then best box again) | `camera_manager.py:189-217` | Cooldown masks it; log best box once |
| M4 | CSV vs snapshots mismatch: 474 rows vs 402 JPGs | `logs/detections.csv`, `detections/` | 72 rows reference images no longer on disk — reconcile or rebuild history |
| M5 | USB camera fails to grab on this machine (MSMF) | `camera_manager.py`, env | Environmental; default `CAMERA_MODE=usb` gives a blank feed here |
| M6 | Emergency‑stop dialog claims "SMS sent" / "GPS recorded" unconditionally | `ui/dashboard.py:179-195` | Only claim what the ESP32 confirmed |

### Low
| # | Bug | Location | Notes |
|---|---|---|---|
| L1 | `_last_gps` stale forever if a fix is lost — `NO_FIX` never clears the cached coordinate | `backend/esp32.py:245-264` | Clear cache when NO_FIX received |
| L2 | `_refresh` reads header status via `get_esp_status()` each tick (~10 Hz) | `ui/components/header.py:82` | Trivial cost; fine |
| L3 | `gsm_card` `max_lines=1` on a `multiline=True` field; GSM/GSM cards use legacy colors | `gsm_card.py:69`, `gps_card.py` | Cosmetic |
| L4 | Nested `with self._lock:` inside `_camera_loop` (outer+inner) | `ui/controller.py:328-336` | Harmless (RLock), redundant |
| L5 | `set_status()` on Header unused; "SYSTEM READY" pill static | `ui/components/header.py:94` | Cosmetic |
| L6 | Legacy/broken files still present: `main.py`, `ui.py`, `test_esp32.py`, `esp32.py` shim, `sms_manager.py` | repo root | Broken vs new backend (`esp.update()`, `port=` removed) |

---

## 7. TECHNICAL DEBT

- **Dead/legacy surface area:** ~9 files (empty, unused, or broken) — confuses onboarding and audits.
- **Config consolidation (M5):** ✔ done — `config.py` is now a single source of truth (no more duplicate `CAMERA_INDEX`/`ESP32_IP` overrides).
- **Flet thread model:** refresh loop updates controls off‑thread; should move to Flet main‑thread scheduling and change‑driven updates.
- **Refresh is timer‑blind:** `page.update()` every 100 ms regardless of whether anything changed; snapshot re‑read from disk at 10 Hz.
- **No automated tests / no CI** for the core logic that *is* testable (stats, alert, ESP32 queue, CSV parsing).
- **`sys.path` hacks** and inconsistent card styling generations (legacy GPS/GSM vs `Palette`-based cards).
- **Repo hygiene:** `app_output.log`/`app_error.log`, `.app.lock`, `detections/` (402 files), `reports/` committed or unignored; `models/yolov8n.pt` stray; `.gitignore` incomplete.
- **README** out of date (legacy feature set).
- **Hardware blind spots:** GPS, GSM, motors, E‑stop — all designed, none validated.

---

## 8. SECURITY

| Area | Finding | Severity |
|---|---|---|
| Web server binding | Binds localhost (127.0.0.1/::1) — not exposed externally | ✔ Good |
| Hardcoded secrets/keys | None found | ✔ Good |
| ESP32 HTTP API | **No authentication** — plain‑text HTTP to `192.168.1.120` / `192.168.4.1`; any device that can reach the rover can issue forward/stop/speed/SMS/E‑stop commands | ⚠ Acceptable for demo/LAN; add token auth for field use |
| PII storage | GSM phone number persisted in plaintext `config/gsm_settings.csv` | ⚠ Low risk locally; avoid committing |
| Input handling | GSM phone/message URL‑encoded before send; no injection into the local UI beyond status text | ✔ OK |
| Traffic | No TLS anywhere (LAN hardware endpoints) | ⚠ Fine for local; not for remote |

---

## 9. PROJECT HEALTH SCORE

| Dimension | /10 | Rationale |
|---|---|---|
| Architecture | 7.5 | Clean layering + singleton controller; dead code and sys.path hacks drag it down |
| UI | 8.0 | Bounded, live, professional; SOS no‑op + invisible analytics dock points |
| AI / Detection | 7.0 | Real YOLO, 4 classes, sound severity logic; 5 fps |
| ESP32 Integration | 7.0 | Excellent queue/debounce/polling design; completely unproven on hardware |
| Performance | 5.5 | 5 fps YOLO; wasteful 10 Hz page.update + disk reads; offline poll timeouts |
| Reliability | 6.5 | Runs stable (33+ min observed); thread‑safety + MSMF env issue |
| Testing | 2.0 | No real tests; legacy test broken |
| Documentation | 4.5 | Excellent `PROJECT_STATUS_REPORT.md`; outdated README |
| Security | 6.0 | Localhost + no secrets; unauthenticated ESP32 API, plaintext phone |
| Demo‑readiness on this machine | 5.0 | Needs `CAMERA_MODE=demo` + track MP4 (USB camera fails here) |
| **Overall** | **6.5/10** | Production‑adjacent demo backbone; fix SOS, SMS honesty, analytics mount, and validate hardware |

---

## 10. REMAINING ROADMAP (prioritized)

### Critical
| Item | Effort | Impact |
|---|---|---|
| Validate on real hardware (ESP32 rover, ESP32‑CAM, GPS, GSM, E‑stop) | 1 day + hardware | Highest — every hardware path is unproven |
| Fix H1–H3 (SOS wiring, SMS honesty, mount analytics charts) | 2–3 h | High visibility bugs |

### High
| Item | Effort | Impact |
|---|---|---|
| Move Flet updates to main thread / change‑driven refresh; throttle snapshot reads | 2–3 h | Web‑UI stability + idle load |
| Set up demo mode for this machine (`CAMERA_MODE=demo` + track MP4) | 10 min | Makes live feed actually work here |
| Reconcile CSV vs snapshot history (M4) | 30 min | Data consistency |

### Medium
| Item | Effort | Impact |
|---|---|---|
| Real test suite (pytest): stats, alert, ESP32 queue/coalesce/debounce, controller history | 3–4 h | Regression safety |
| Wire `gsm_store` phone default into GSMCard | 30 min | UX |
| Clean double‑logging in `process_frame` + tidy indentation | 30 min | Code quality |
| ESP32 GPS: clear cached fix on NO_FIX | 15 min | Correct telemetry |

### Low
| Item | Effort | Impact |
|---|---|---|
| Purge dead/legacy files; trim `requirements.txt` | 30 min | Repo hygiene |
| Update README to current architecture | 30 min | Docs |
| Repo hygiene: `.gitignore` logs/lock/detections/reports; archive 402 snapshots | 30 min | Repo hygiene |
| ESP32 auth token on HTTP endpoints | 1–2 h | Field security |

---

## 11. NEXT RECOMMENDED ACTIONS (10 tasks, in order)

1. **Mount AnalyticsPanel** in the layout (e.g., under Rover Controls in CENTER, or a fourth row) — the two charts exist but are invisible today. (~30 min)
2. **Wire the SOS button** to `esp_emergency_stop()` + GPS capture + SMS, with honest confirmation UI. (~30 min)
3. **Make SMS reporting honest** — surface queued/delivered/failed state from the ESP32 response; disable Send when offline. (~1 h)
4. **Configure demo mode on this machine** — `CAMERA_MODE=demo` + `DEFAULT_VIDEO_PATH` to a real track MP4 so the feed shows live frames (USB MSMF fails here). (~10 min)
5. **Throttle the refresh loop** — only `page.update()` when frame/alert/stats actually changed; cache the latest snapshot base64 instead of re‑reading disk at 10 Hz. (~1–2 h)
6. **Fix the double‑logging + indentation** in `camera_manager.process_frame` (log best box once) and reconcile the 474‑vs‑402 history mismatch. (~30 min)
7. **Purge dead/legacy code** — `sms_manager.py`, `ui/mock.py`, `rover_panel.py`, `main.py`, `ui.py`, `test_esp32.py`, `test_alert.py`, root `esp32.py` shim, `_notify_ui_update`/`get_ui_state`; trim unused requirements. (~30 min)
8. **Add a pytest suite** for the testable core: statistics normalization, alert severity mapping, ESP32 submit/coalesce/debounce, controller CSV parsing. (~3–4 h)
9. **Repo hygiene** — extend `.gitignore` (`.app.lock`, `app_*.log`, `detections/`, `reports/`, `uploads/`), remove `models/yolov8n.pt`, archive the 402 snapshots, update README. (~1 h)
10. **Hardware rehearsal** — end‑to‑end run with real ESP32 rover, ESP32‑CAM, GPS fix and GSM delivery; verify E‑stop, speed, and report content. (1 day with hardware)

---

## EXECUTIVE SUMMARY

The Railway Crack Detection System is a **functional, production‑adjacent demo backbone (~78% complete, overall health 6.5/10)**. It runs reliably on Python 3.11 / Flet 0.86.4 as a single‑instance web app on localhost:8080; it currently boots and serves with a stable background pipeline, real YOLO inference over three switchable camera sources, live severity alerts, statistics, snapshots, CSV history, and working PDF report generation (9 reports already produced). The three largest issues from the baseline report are **fixed**: statistics counters now normalize class names and increment correctly; `report_generator.py` no longer imports a missing module and is wired to the UI; `config.py` is consolidated into a single source of truth. The dashboard layout was also repaired into a bounded, viewport‑filling 3‑column grid with every card refreshing live at 10 Hz — no page scrolling, live clock, GPS/GSM placeholders, and instant rover‑speed updates.

Remaining gaps keep it short of production: **(1)** hardware has never been exercised — all ESP32/GPS/GSM/E‑stop paths run only the offline branch; **(2)** three visible defects — a dead SOS button, SMS that always reports "sent", and Analytics charts instantiated but never mounted; **(3)** no automated tests; **(4)** Flet updates happen from a background thread with a 10 Hz `page.update()` and 10 Hz disk snapshot reads (idle churn); **(5)** on this specific machine the USB camera cannot grab frames (MSMF), so a demo video or ESP32‑CAM must be configured; **(6)** repo hygiene (dead files, unignored logs, 402 accumulated snapshots, outdated README).

Recommended path to readiness: fix the three visible defects (task 1–3), configure demo mode on this machine (task 4), throttle the refresh loop (task 5), then build the test suite and clean the repo (task 6–9) before a one‑day hardware rehearsal (task 10). Estimated software effort to completion: **2–3 focused dev‑days** plus **1 day with hardware**.

---
*Read‑only audit generated from the live codebase. No application code was modified and no application was launched by this audit.*
