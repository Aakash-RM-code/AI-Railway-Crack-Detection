# Project Tree — Railway Crack Detection System

> Generated from the post-refactor filesystem layout. Data directories
> (`detections/`, `reports/`, `logs/`) are shown as counts because they grow at
> runtime; everything else is a complete listing of tracked source files.

```
crack_det_v_1/
├── config.py                       # Single source of truth for paths & settings
├── requirements.txt                # Backend runtime dependencies
├── README.md
├── REFACTOR_REPORT.md              # Backend refactor report (10 sections)
├── prjct_audit.md                  # pre-refactor audit notes
├── PROJECT_STATUS_REPORT.md        # project status overview
├── .gitignore
├── .app.lock                       # runtime lock file (legacy, auto-created)
├── app_output.log                  # runtime console output (auto-created)
├── app_error.log                   # runtime error output (auto-created)
├── backend/                        # FastAPI-ready backend services
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry (uvicorn backend.main:app)
│   ├── api/                        # HTTP / WebSocket interface layer
│   │   ├── __init__.py
│   │   ├── routes.py               # REST endpoints (structure)
│   │   ├── schemas.py              # Pydantic request/response models
│   │   └── websocket.py            # live frame/alert stream (structure)
│   ├── detector/
│   │   ├── __init__.py
│   │   └── detector.py             # CrackDetector — YOLO wrapper (models/best.pt)
│   ├── hardware/                   # rover peripherals
│   │   ├── __init__.py
│   │   ├── esp32.py                # ESP32Controller — rover control + GSM (HTTP)
│   │   ├── gps.py                  # GpsService — GPS readings from ESP32 cache
│   │   └── gsm.py                  # GsmService — SMS alerts + phone number store
│   ├── services/                   # detection pipeline business logic
│   │   ├── __init__.py
│   │   ├── camera.py               # CameraManager + CameraPipeline (background loop)
│   │   ├── alert_manager.py        # AlertManager — severity assessment
│   │   ├── statistics_manager.py   # StatisticsManager — per-class counters
│   │   ├── history_manager.py      # HistoryManager — CSV history + latest snapshot
│   │   ├── logger.py               # DetectionLogger — snapshots + history CSV
│   │   └── report_generator.py     # PDF inspection reports (reportlab)
│   ├── storage/
│   │   ├── __init__.py
│   │   └── gsm_store.py            # GSM settings load/save (config/gsm_settings.csv)
│   └── utils/
│       ├── __init__.py
│       └── imaging.py              # frame → JPEG base64 helpers
├── models/
│   └── best.pt                     # production YOLO model
├── config/
│   └── gsm_settings.csv            # phone number / APN (gitignored)
├── assets/                         # reserved for static assets
├── docs/
│   ├── PROJECT_TREE.md
│   ├── ARCHITECTURE.md
│   ├── DEPENDENCIES.md
│   ├── API_PLAN.md                 # planned API surface + React integration
│   ├── BACKEND_OVERVIEW.md         # how the backend runs / serves a React client
│   ├── START_HERE.md
│   └── TODO.md
├── tests/
│   ├── __init__.py
│   └── test_backend.py             # import/config/API smoke tests
├── detections/                     # saved detection snapshots (gitignored)
├── logs/
│   └── detections.csv              # detection history CSV (gitignored)
├── reports/                        # generated PDF reports (gitignored)
├── uploads/                        # demo-video uploads (gitignored)
└── archive/
    ├── legacy/                     # superseded / archived code (not shipped)
    │   ├── app.py                  # legacy Flet entry point
    │   ├── run_app.bat             # legacy Windows launcher
    │   ├── run_app.ps1             # legacy PowerShell launcher
    │   ├── ui/                     # legacy Flet front-end (controller, dashboard, cards)
    │   ├── backend_old/            # pre-refactor backend modules (flat layout)
    │   ├── utils_old/              # pre-refactor utils (gsm_store.py)
    │   ├── main.py                 # superseded OpenCV pipeline (archived earlier)
    │   ├── ui.py                   # superseded UI (archived earlier)
    │   ├── esp32.py                # backward-compat shim (archived earlier)
    │   ├── mock.py                 # unused demo data (archived earlier)
    │   ├── rover_panel.py          # never-mounted component (archived earlier)
    │   ├── layout_test.py          # manual layout harness, port 8090 (archived earlier)
    │   └── models/
    │       └── yolov8n.pt          # unused placeholder model (archived earlier)
    └── legacy-backend-old/         # (reserved)
```

## Notes

- The **Flet UI is archived**, not deleted. The backend now serves a FastAPI
  interface (`backend/main.py`) that a future React frontend can consume.
- All `.py` files under `archive/legacy/` are non-shipping reference code.
- Every filesystem path used by the app derives from `config.py`; the project is
  relocatable as a whole.
