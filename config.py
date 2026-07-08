"""
=====================================================
Railway Crack Detection System - Configuration File
Version : 2.0
=====================================================
Modify project settings here instead of changing
multiple files.
"""

# =====================================================
# MODEL SETTINGS
# =====================================================

MODEL_PATH = "best.pt"

# =====================================================
# CAMERA SETTINGS
# =====================================================

CAMERA_INDEX = 1

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# =====================================================
# AI DETECTION SETTINGS
# =====================================================

CONFIDENCE_THRESHOLD = 0.70

# =====================================================
# LOGGER SETTINGS
# =====================================================

SAVE_IMAGES = True

SAVE_VIDEO = False

LOG_COOLDOWN = 5      # seconds

# =====================================================
# ESP32 SETTINGS
# =====================================================

ESP32_PORT = "COM3"

BAUDRATE = 115200

# =====================================================
# STREAMLIT SETTINGS
# =====================================================

APP_TITLE = "🚆 Railway Crack Detection Dashboard"

REFRESH_RATE = 30

# =====================================================
# UI SETTINGS
# =====================================================

WINDOW_NAME = "Railway Crack Detection System"

SHOW_FPS = True

SHOW_COUNTER = True

SHOW_CONFIDENCE = True

# =====================================================
# ALERT SETTINGS
# =====================================================

LOW_CONFIDENCE = 0.70

HIGH_CONFIDENCE = 0.90

SAVE_ONLY_HIGH_CONFIDENCE = True