# Project Tree — Railway Crack Detection System

> Generated from the post-refactor filesystem layout. Data directories
> (`detections/`, `reports/`, `logs/`) are shown as counts because they grow at
> runtime; everything else is a complete listing of tracked source files.

```
crack_det_v_1/
├── app.py                          # Entry point — Flet web app + single-instance lock
├── config.py                       # Single source of truth for paths & settings
├── requirements.txt                # Python dependencies (DO NOT MODIFY)
├── run_app.bat                     # Windows launcher (verified Python 3.11)
├── run_app.ps1                     # PowerShell launcher (verified Python 3.11)
├── README.md
├── .gitignore
├── .app.lock                       # runtime lock file (auto-created/deleted)
├── app_output.log                  # runtime console output (auto-created)
├── app_error.log                   # runtime error output (auto-created)
├── backend/                        # server-side / pipeline modules
│   ├── __init__.py
│   ├── alert_manager.py            # AlertManager — severity assessment + SMS alerts
│   ├── camera_manager.py           # CameraManager — source mgmt + detection pipeline
│   ├── detector.py                 # CrackDetector — YOLO wrapper (models/best.pt)
│   ├── esp32.py                    # ESP32Controller — rover control + GSM (HTTP/AT)
│   ├── logger.py                   # DetectionLogger — history CSV + snapshot images
│   ├── report_generator.py         # PDF inspection reports (reportlab)
│   └── statistics_manager.py       # StatisticsManager — per-class detection counters
├── ui/                             # Flet front-end
│   ├── __init__.py
│   ├── controller.py               # AppController — shared process-wide singleton
│   ├── dashboard.py                # Dashboard — main view (bounded 3-column layout)
│   ├── theme.py                    # color / theme constants
│   └── components/
│       ├── __init__.py
│       ├── alert_card.py
│       ├── analytics.py
│       ├── base.py
│       ├── camera_card.py
│       ├── footer.py
│       ├── gps_card.py
│       ├── gsm_card.py
│       ├── header.py
│       ├── health_card.py
│       ├── history_table.py
│       ├── rover_control_card.py
│       ├── snapshot_card.py
│       └── statistics_card.py
├── models/
│   └── best.pt                     # production YOLO model (moved from root)
├── utils/
│   ├── __init__.py
│   └── gsm_store.py                # GSM settings load/save (config/gsm_settings.csv)
├── config/
│   └── gsm_settings.csv            # phone number / APN (gitignored)
├── assets/                         # reserved for static assets
├── docs/
│   ├── PROJECT_TREE.md
│   ├── ARCHITECTURE.md
│   ├── DEPENDENCIES.md
│   ├── START_HERE.md
│   └── TODO.md
├── tests/
│   └── __init__.py                 # test package (empty)
├── detections/                     # saved detection snapshots (gitignored) — 425 files
├── logs/
│   └── detections.csv              # detection history CSV (gitignored)
├── reports/                        # generated PDF reports (gitignored) — 9 files
├── uploads/                        # demo-video uploads (gitignored)
└── archive/
    └── legacy/
        ├── main.py                 # superseded OpenCV pipeline (archived)
        ├── ui.py                   # superseded UI (archived)
        ├── esp32.py                # original serial shim (archived)
        ├── mock.py                 # unused demo data (archived)
        ├── rover_panel.py          # never-mounted component (archived)
        ├── layout_test.py          # manual layout harness, port 8090 (archived)
        └── models/
            └── yolov8n.pt          # unused placeholder model (archived)
```

## Notes

- All `.py` files under `archive/legacy/` are prefixed with an `# ARCHIVED —`
  banner. `layout_test.py` keeps a small `sys.path` bootstrap so it can still be
  run by hand as a manual harness; shipped code contains no `sys.path` hacks.
- Every filesystem path used by the app derives from `config.py`; the project is
  relocatable as a whole.
