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
