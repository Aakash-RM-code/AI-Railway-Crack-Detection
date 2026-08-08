# API Plan — Railway Crack Detection Backend

Target: a JSON REST + WebSocket API consumed by a future **React** frontend.
Current status: **structure only** — routers and schemas exist and import/run,
but endpoint coverage is intentionally minimal (see the checklist at the end).

## Base URL

```
http://<host>:8080
```

CORS is open (`*`) in `backend/main.py` so a React dev server on another origin
can call the API during development.

## Current endpoints (implemented)

| Method | Path                | Description                                   | Response model        |
|--------|---------------------|-----------------------------------------------|-----------------------|
| GET    | `/api/health`       | Liveness probe                                | `{status: "ok"}`      |
| GET    | `/api/state`        | Full runtime snapshot                         | `RuntimeState`        |
| GET    | `/api/camera/status`| Camera mode/running/fps/resolution/error      | `CameraStatus`        |
| GET    | `/api/camera/frame` | Latest frame as base64 JSON                   | `{frame_base64}`      |
| POST   | `/api/camera/start` | Start the capture pipeline                    | `{running}`           |
| POST   | `/api/camera/stop`  | Stop the capture pipeline                     | `{running}`           |
| POST   | `/api/camera/source`| Switch camera source                          | `CameraStatus`        |
| GET    | `/api/history`      | Recent detection history (CSV)                | `list[HistoryRow]`    |
| POST   | `/api/report`       | Generate a PDF report                         | `{path}`              |

## Planned endpoints (next)

| Method | Path                    | Purpose                                      |
|--------|-------------------------|----------------------------------------------|
| GET    | `/api/esp32/status`     | Rover online/ip/last_error/last_response     |
| POST   | `/api/esp32/forward`    | Move rover forward                           |
| POST   | `/api/esp32/backward`   | Move rover backward                          |
| POST   | `/api/esp32/stop`       | Stop rover                                   |
| POST   | `/api/esp32/speed`      | Set rover speed (`SpeedRequest`)             |
| POST   | `/api/esp32/estop`      | Emergency stop                               |
| GET    | `/api/gps`              | GPS string + fix flag + coordinates          |
| POST   | `/api/sms/send`         | Send SMS (`SmsRequest`)                      |
| POST   | `/api/sms/test`         | Send test SMS                                |
| GET    | `/api/settings/gsm`     | Read stored phone number                     |
| PUT    | `/api/settings/gsm`     | Persist phone number                         |
| GET    | `/api/detections/snapshot` | Latest snapshot base64                    |
| GET    | `/api/analytics/severity`  | Severity distribution counts             |
| WS     | `/ws/stream`            | Live push of `RuntimeState`                  |

## WebSocket contract — `/ws/stream`

- Client connects, optionally sends nothing.
- Server pushes JSON payloads of `RuntimeState` (frame base64 + alert + stats +
  health) — currently a heartbeat/demo loop; the production wiring will push
  on pipeline state-change events (see `docs/BACKEND_OVERVIEW.md`).

## React integration checklist

- [ ] Consume `/api/state` to render dashboard cards (alert, stats, health).
- [ ] Use `/api/history` for the history table; poll every few seconds.
- [ ] Use `/ws/stream` for live frame + alert updates (or poll `/api/state`).
- [ ] Camera controls via `/api/camera/start|stop|source`.
- [ ] Rover controls via `/api/esp32/*`.
- [ ] GPS card via `/api/gps`.
- [ ] GSM settings + test SMS via `/api/sms/*` and `/api/settings/gsm`.
- [ ] Report button calls `/api/report` then opens the returned PDF path.
- [ ] Auto-refresh: re-sync on reconnect when the WebSocket drops.

## Completion checklist

- [ ] All planned REST endpoints implemented and typed with pydantic schemas.
- [ ] `/ws/stream` wired to real pipeline change events.
- [ ] Error handling: consistent `HTTPException` payloads.
- [ ] Optional auth token for rover-control endpoints.
- [ ] Integration test covering the full flow end-to-end.
