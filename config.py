"""
=====================================================
Railway Crack Detection System - Configuration
Single Source of Truth
=====================================================
Only values actually used by the running Flet application
are kept. Keys that were previously duplicated across two
config blocks are defined exactly once here.

Environment variables override defaults where noted.
"""

import os
from pathlib import Path

# =====================================================
# PROJECT LAYOUT — every filesystem path derives from
# PROJECT_DIR so the project is relocatable and no
# absolute/hardcoded paths exist in application code.
# =====================================================

PROJECT_DIR = Path(__file__).resolve().parent

MODELS_DIR = PROJECT_DIR / "models"
ASSETS_DIR = PROJECT_DIR / "assets"
CONFIG_DIR = PROJECT_DIR / "config"
DETECTIONS_DIR = PROJECT_DIR / "detections"
LOGS_DIR = PROJECT_DIR / "logs"
REPORTS_DIR = PROJECT_DIR / "reports"
UPLOADS_DIR = PROJECT_DIR / "uploads"

MODEL_PATH = str(MODELS_DIR / "best.pt")
HISTORY_CSV = str(LOGS_DIR / "detections.csv")
GSM_SETTINGS_CSV = str(CONFIG_DIR / "gsm_settings.csv")
APP_LOCK_FILE = str(PROJECT_DIR / ".app.lock")

# =====================================================
# AI MODEL
# =====================================================

CONFIDENCE_THRESHOLD = 0.70
INFERENCE_IMGSZ = 640

# Inference backend: "openvino" (default) | "torch".
# OpenVINO is ~1.5-1.6x faster with equivalent detection results; CrackDetector
# falls back to the PyTorch best.pt model automatically if the OpenVINO export
# cannot be loaded. Set INFERENCE_BACKEND=torch to force the PyTorch path.
INFERENCE_BACKEND = os.getenv("INFERENCE_BACKEND", "openvino").strip().lower()

# OpenVINO model precision selection (only used when INFERENCE_BACKEND=openvino):
#   "fp32" (default) -> models/best_openvino_model/  (verified production model)
#   "int8"           -> models/best_int8_openvino_model/  (experimental NNCF PTQ)
# INT8 is opt-in. If the requested precision export is missing or fails to load,
# CrackDetector falls back to the other OpenVINO export, then to PyTorch.
OPENVINO_PRECISION = os.getenv("OPENVINO_PRECISION", "fp32").strip().lower()

# OpenVINO IR export of best.pt; best.pt remains the canonical source model.
OPENVINO_MODEL_PATH = str(MODELS_DIR / "best_openvino_model")

# Experimental INT8 OpenVINO IR (NNCF post-training quantization of best.pt).
# Kept separate so the production FP32 export is never replaced implicitly.
OPENVINO_INT8_MODEL_PATH = str(MODELS_DIR / "best_int8_openvino_model")

# =====================================================
# CAMERA
# =====================================================

# Active source: "usb" | "esp32cam" | "demo"
CAMERA_MODE = os.getenv("CAMERA_MODE", "usb")

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))

# Demo video path (set at runtime when a file is picked in the UI)
DEFAULT_VIDEO_PATH = os.getenv("DEFAULT_VIDEO_PATH", "")

# =====================================================
# ESP32-CAM (capture board)
# =====================================================

ESP32CAM_IP = os.getenv("ESP32CAM_IP", "192.168.4.1")
ESP32CAM_PORT = int(os.getenv("ESP32CAM_PORT", "81"))

ESP32CAM_STREAM_URL = os.getenv(
    "ESP32CAM_STREAM_URL",
    f"http://{ESP32CAM_IP}:{ESP32CAM_PORT}/stream",
)
ESP32CAM_SNAPSHOT_URL = os.getenv(
    "ESP32CAM_SNAPSHOT_URL",
    f"http://{ESP32CAM_IP}:{ESP32CAM_PORT}/capture",
)

# =====================================================
# ESP32 (rover control)
# =====================================================

# When "true", the app constructs an ESP32Controller, polls it, and attaches
# it to the camera pipeline on startup. When "false" (or no hardware present),
# hardware endpoints report explicit offline/unavailable state instead of fake data.
ESP32_ENABLED = os.getenv("ESP32_ENABLED", "true").lower() in ("1", "true", "yes")

ESP32_IP = os.getenv("ESP32_IP", "192.168.1.120")
ESP32_PORT = os.getenv("ESP32_PORT", "80")
ESP32_BASE_URL = f"http://{ESP32_IP}:{ESP32_PORT}"

ESP32_TIMEOUT = int(os.getenv("ESP32_TIMEOUT", "3"))
ESP32_RETRIES = int(os.getenv("ESP32_RETRIES", "2"))
ESP32_RETRY_DELAY = float(os.getenv("ESP32_RETRY_DELAY", "0.5"))
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "2"))  # seconds

DEFAULT_SPEED = int(os.getenv("DEFAULT_SPEED", "150"))
ESP32_DEFAULT_SPEED = 150
MIN_SPEED = 0
MAX_SPEED = 255
SPEED_SLOW = 80
SPEED_MEDIUM = 150
SPEED_FAST = 220

# =====================================================
# API SECURITY
# =====================================================

# Runtime environment: "development" (default) | "production".
# In production the app refuses to start without an API_AUTH_TOKEN set.
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()

# Comma-separated list of origins allowed to call this API. When set, CORS
# is restricted to these origins; when "*" (default) CORS stays wide open for
# local development only — never expose a hardware-control API with "*" publicly.
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "*")

# Optional shared secret. When set, REST/WebSocket clients must send it via
# `Authorization: Bearer <token>` (or `?token=` for WebSockets). Empty = open.
#
# Production requires a non-empty value (see backend/main.py startup guard).
# The value must come from the environment — never hardcode a secret here.
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "").strip()
