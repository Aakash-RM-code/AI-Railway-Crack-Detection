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


# AI Railway Crack Detection System

An AI-powered railway inspection system that detects rail cracks and broken chains using a camera, YOLO-based computer vision, OpenVINO acceleration, and a React/FastAPI dashboard.

## Requirements

* Windows 10/11
* Python 3.11
* Node.js 18+
* Git
* Webcam/USB camera for live testing
* 8 GB+ RAM recommended

> ESP32, GPS, GSM and rover hardware are optional for software-only testing.

---

## 1. Clone the Repository

```powershell
git clone https://github.com/Aakash-RM-code/AI-Railway-Crack-Detection.git
cd AI-Railway-Crack-Detection
```

---

## 2. Backend Setup

Create a Python 3.11 virtual environment:

```powershell
cd backend
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Return to the project root:

```powershell
cd ..
```

---

## 3. Configure the Backend

The application supports different camera and inference modes.

For a normal USB webcam:

```powershell
$env:CAMERA_MODE="usb"
$env:INFERENCE_BACKEND="openvino"
```

For demo/testing mode without a physical camera:

```powershell
$env:CAMERA_MODE="demo"
$env:INFERENCE_BACKEND="openvino"
```

OpenVINO is the default inference backend.

The system keeps PyTorch as a fallback:

```powershell
$env:INFERENCE_BACKEND="torch"
```

Make sure the model files exist:

```text
models/
├── best.pt
└── best_openvino_model/
```

---

## 4. Start the Backend

From the project root:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080
```

The backend will be available at:

```text
http://127.0.0.1:8080
```

Health check:

```text
http://127.0.0.1:8080/api/health
```

Keep this terminal running.

---

## 5. Frontend Setup

Open a **second PowerShell terminal**.

From the project root:

```powershell
cd frontend
npm install
```

Then start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

Open that address in your browser.

---

## 6. Run With a USB Webcam

Connect your webcam before starting the backend.

Set:

```powershell
$env:CAMERA_MODE="usb"
$env:INFERENCE_BACKEND="openvino"
```

Then start:

```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080
```

Open the frontend.

The camera card should display the live MJPEG stream.

The detection pipeline is:

```text
USB Camera
     ↓
OpenCV Capture
     ↓
YOLO + OpenVINO
     ↓
Crack Detection
     ↓
Alert Manager
     ↓
Snapshot + CSV
     ↓
REST API / WebSocket
     ↓
React Dashboard
```

---

## 7. Demo Mode

If no camera or hardware is available:

```powershell
$env:CAMERA_MODE="demo"
$env:INFERENCE_BACKEND="openvino"
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080
```

This allows the software pipeline to be tested without connecting the physical rover.

---

## 8. ESP32 / GPS / GSM

The hardware components are optional.

The backend communicates with the ESP32 over HTTP.

If the ESP32 is unavailable, the application should remain operational, but hardware-related features will report as disconnected/unavailable.

For physical hardware testing, configure the ESP32 address and required environment variables according to the project's configuration.

---

## 9. Verify the Installation

Backend tests:

```powershell
python -m pytest tests/ -q
```

TypeScript:

```powershell
cd frontend
npx tsc --noEmit
```

Lint:

```powershell
npm run lint
```

Production build:

```powershell
npm run build
```

---

## 10. Production Build

Build the frontend:

```powershell
cd frontend
npm run build
```

The generated production files can then be deployed using the project's configured deployment system.

---

## Troubleshooting

### Backend does not start

Check Python:

```powershell
python --version
```

It should be Python 3.11.

Check dependencies:

```powershell
pip install -r backend/requirements.txt
```

### Webcam is not detected

Test the camera directly:

```powershell
python -c "import cv2; c=cv2.VideoCapture(0, cv2.CAP_DSHOW); print('opened=',c.isOpened()); ok,f=c.read(); print('frame=',ok, 'shape=', None if f is None else f.shape); c.release()"
```

Expected output should contain:

```text
opened= True
frame= True
```

### OpenVINO fails to load

Check that:

```text
models/best_openvino_model/
```

exists.

You can temporarily switch to PyTorch:

```powershell
$env:INFERENCE_BACKEND="torch"
```

### Frontend cannot connect to backend

Make sure the backend is running on:

```text
http://127.0.0.1:8080
```

and that the frontend's API/WS configuration points to port `8080`.

### Live camera shows a black screen

Check:

1. Webcam is connected.
2. `CAMERA_MODE` is set to `usb`.
3. Backend is running.
4. OpenCV can capture frames.
5. OpenVINO model exists.
6. Browser can access:

```text
http://127.0.0.1:8080/api/camera/stream
```

---

## Project Status

The software stack has been verified with:

* FastAPI backend
* React frontend
* YOLO crack detection
* OpenVINO CPU inference
* USB webcam capture
* MJPEG live streaming
* REST APIs
* WebSocket realtime updates
* Detection persistence
* Snapshot generation
* Alert/severity processing
* ESP32 integration layer
* GPS/GSM integration layer

Current OpenVINO configuration:

```text
Image size: 640
Confidence threshold: 0.70
Inference backend: OpenVINO
```

The system detects:

* Broken chain
* Large crack
* Medium crack
* Small crack

> Physical ESP32/rover/GPS/GSM functionality requires the corresponding hardware to be connected and configured.

