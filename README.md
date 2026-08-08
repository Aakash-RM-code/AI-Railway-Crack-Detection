# 🚆 AI Railway Crack Detection & Monitoring System

An end-to-end AI-powered railway inspection system that combines **computer vision, edge AI inference, embedded hardware, and real-time monitoring** to detect and classify railway track defects.

The system uses **YOLOv8 + OpenVINO** for crack detection, **FastAPI** for the backend, **React 19** for the monitoring dashboard, and **ESP32-based hardware** for rover, GPS, GSM, and camera integration.

---

## 🧠 System Overview

The system is designed around an autonomous railway inspection workflow:

```text
                    ┌──────────────────┐
                    │   Camera Source  │
                    │ USB / ESP32-CAM  │
                    │   / Demo Video   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Camera Manager   │
                    │  & Pipeline      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ YOLOv8 Detector  │
                    │    OpenVINO      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Alert Manager    │
                    │ Severity Engine  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ Snapshot │   │ Statistics│  │ Detection│
        │  + CSV   │   │  Engine   │  │  History │
        └────┬─────┘   └────┬─────┘  └────┬─────┘
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    ┌──────────────────┐
                    │ FastAPI Backend  │
                    │ REST + WebSocket │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌──────────────┐
          │ React 19     │      │ ESP32 Rover  │
          │ Dashboard    │      │ GPS / GSM    │
          └──────────────┘      └──────────────┘
```

---

# ✨ Features

### 🤖 AI Detection

* YOLOv8-based railway defect detection
* OpenVINO CPU acceleration
* PyTorch fallback
* Configurable confidence threshold
* 640×640 inference resolution
* Detection bounding boxes and confidence scores
* Four supported defect classes:

  * `small_crack`
  * `medium_crack`
  * `large_crack`
  * `broken_chain`

### 🎥 Live Camera

* USB webcam support
* ESP32-CAM support
* Demo video mode
* Real-time MJPEG streaming
* Automatic camera pipeline management
* Latest-frame architecture to avoid queue buildup
* Windows DirectShow support for USB cameras

### 🚨 Alert System

Detected defects are converted into severity levels:

| Defect       | Severity |
| ------------ | -------- |
| Small crack  | LOW      |
| Medium crack | MEDIUM   |
| Large crack  | HIGH     |
| Broken chain | CRITICAL |

The system also includes detection cooldown logic to prevent duplicate records.

### 📊 Monitoring Dashboard

The React dashboard provides:

* Live camera feed
* Active alerts
* Track health
* GPS information
* GSM status
* Rover controls
* Detection statistics
* Detection trends
* Latest snapshot
* Detection history
* Real-time telemetry

### 📡 Real-Time Communication

The backend exposes WebSocket channels for:

```text
/ws/telemetry
/ws/detections
/ws/camera-status
/ws/stream
```

The frontend uses a realtime layer with:

* Automatic reconnect
* Exponential backoff
* Per-channel connection state
* React Query cache merging
* REST polling fallback
* Detection event invalidation

### 🚗 Rover & Hardware

Backend hardware integration supports:

* ESP32 rover control
* ESP32-CAM
* GPS
* GSM
* SMS
* Rover speed control
* Hardware connection monitoring

The ESP32 devices communicate with the backend over HTTP.

---

# 🏗️ Technology Stack

## Backend

| Technology  | Purpose                               |
| ----------- | ------------------------------------- |
| Python 3.11 | Backend runtime                       |
| FastAPI     | REST API                              |
| OpenCV      | Camera acquisition & image processing |
| YOLOv8      | Object detection                      |
| OpenVINO    | CPU-optimized inference               |
| Pydantic    | API schemas                           |
| WebSockets  | Real-time communication               |
| ReportLab   | Report generation                     |

## Frontend

| Technology           | Purpose      |
| -------------------- | ------------ |
| React 19             | UI           |
| TypeScript           | Type safety  |
| TanStack Router      | Routing      |
| TanStack React Query | Server state |
| Tailwind CSS v4      | Styling      |
| Vite                 | Build system |

## Hardware

* ESP32
* ESP32-CAM
* NEO-6M GPS
* GSM module
* Rover motor controller
* USB webcam

---

# 🔬 AI Pipeline

The inference pipeline is:

```text
Frame Capture
     ↓
Preprocessing
     ↓
YOLOv8 + OpenVINO
     ↓
Bounding Boxes
     ↓
Confidence Filtering
     ↓
Class → Severity Mapping
     ↓
Alert Generation
     ↓
Snapshot + CSV Persistence
     ↓
REST / WebSocket
```

The canonical model remains:

```text
models/best.pt
```

while OpenVINO provides the optimized inference backend:

```text
models/best_openvino_model/
```

OpenVINO is the default backend, with PyTorch available as a fallback.

---

# ⚡ Performance

The system was benchmarked using the same model and inference resolution.

```text
Inference resolution : 640 × 640
Confidence threshold : 0.70
Backend              : OpenVINO
Device               : CPU
```

Representative local benchmark:

| Backend  |  Inference |
| -------- | ---------: |
| PyTorch  |     ~7 FPS |
| OpenVINO | ~10–13 FPS |

OpenVINO provided approximately **1.5–1.7× faster inference** during local testing while maintaining comparable detection behavior on the available validation frames.

The inference resolution was intentionally kept at **640** because reducing the resolution caused unacceptable loss of small-crack detection during benchmarking.

---

# 💾 Data Persistence

Detected defects are persisted using the `DetectionRepository`.

Each detection can generate:

```text
CSV record
   +
JPEG snapshot
```

The system also exposes:

* Latest detection
* Latest snapshot
* Detection history
* Statistics
* Trend information
* Distribution information

---

# 🔌 API Architecture

The backend is organized into modular API routers:

```text
/api/system
/api/camera
/api/detections
/api/statistics
/api/hardware
/api/gps
/api/gsm
/api/rover
/api/reports
```

Frontend components communicate through a single `MonitoringApi` abstraction.

This keeps the UI independent of the underlying transport.

```text
React Components
       ↓
MonitoringApi
       ↓
React Query
       ↓
REST API
       ↕
WebSocket Realtime Layer
```

REST remains the fallback when realtime WebSocket connectivity is unavailable.

---

# 📁 Project Structure

```text
AI-Railway-Crack-Detection/
│
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   └── websocket.py
│   │
│   ├── detector/
│   │   └── detector.py
│   │
│   ├── hardware/
│   │   └── esp32.py
│   │
│   ├── services/
│   │   ├── camera.py
│   │   ├── alert_manager.py
│   │   ├── statistics.py
│   │   └── ...
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── api/
│   │   │   └── realtime/
│   │   └── types/
│   │
│   └── package.json
│
├── models/
│   ├── best.pt
│   └── best_openvino_model/
│
├── tests/
│
├── config.py
├── requirements.txt
└── README.md
```

---

# 🚀 Running the Project

## Backend

From the project root:

```powershell
cd D:\Python\crack_det_v_1

$env:INFERENCE_BACKEND="openvino"
$env:CAMERA_MODE="usb"

& "C:\Users\Aakash\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8080
```

Backend:

```text
http://127.0.0.1:8080
```

## Frontend

Open another terminal:

```powershell
cd D:\Python\crack_det_v_1\frontend
npm run dev
```

Then open the Vite URL displayed in the terminal.

---

# 🧪 Verification

The current software stack has been verified with:

```text
39 backend tests passing
TypeScript check passing
ESLint passing
Production frontend build passing
OpenVINO runtime smoke test passing
USB camera acquisition passing
MJPEG streaming passing
REST endpoint smoke tests passing
WebSocket channel tests passing
Detection persistence verified
```

The complete software chain has been exercised:

```text
Camera
  ↓
OpenVINO
  ↓
Detection
  ↓
Alert
  ↓
Snapshot
  ↓
CSV
  ↓
REST / WebSocket
  ↓
React Dashboard
```

---

# ⚠️ Current Limitations

The software stack is substantially implemented, but full physical-system validation is still required.

### Hardware

The following require field validation:

* ESP32 rover
* Rover motor control
* ESP32-CAM
* GPS
* GSM/SMS
* Physical rover network connectivity

### Frontend

Additional testing can be added for:

* Component unit tests
* Browser-level WebSocket tests
* MJPEG browser E2E tests
* Full dashboard integration tests

### Production Hardening

Before production deployment:

* Configure a strong `API_AUTH_TOKEN`
* Restrict `CORS_ALLOWED_ORIGINS`
* Protect sensitive endpoints
* Move secrets to environment variables
* Add CI/CD
* Review logging and generated files
* Validate hardware failure behavior

---

# 🛣️ Roadmap

## Phase 1 — Core System ✅

* Backend architecture
* Camera pipeline
* YOLO detection
* Alert management
* Persistence
* REST API

## Phase 2 — Realtime System ✅

* WebSockets
* React Query integration
* Realtime cache updates
* MJPEG streaming
* REST fallback

## Phase 3 — AI Optimization ✅

* OpenVINO integration
* PyTorch fallback
* Performance benchmarking
* Inference warmup

## Phase 4 — Hardware Integration 🔄

* ESP32 rover validation
* GPS validation
* GSM/SMS validation
* ESP32-CAM validation
* Physical field testing

## Phase 5 — Production Hardening 🔄

* Authentication
* CORS tightening
* Frontend test suite
* CI/CD
* Documentation cleanup
* Browser E2E testing
* Performance optimization

---

# 🎯 Project Goal

The long-term goal is to develop a **real-time intelligent railway inspection platform** capable of detecting track defects, recording their location and severity, transmitting alerts, and providing operators with a centralized monitoring interface.

The project combines:

**Computer Vision + Edge AI + Embedded Systems + Robotics + Full-Stack Development + Real-Time Communication**

---

# ⚠️ Disclaimer

This project is an engineering and research prototype.

It must **not** be used as the sole safety mechanism for railway infrastructure without professional validation, redundancy, certification, and compliance with applicable railway safety standards.
