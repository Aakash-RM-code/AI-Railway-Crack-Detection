# ARCHIVED — backward-compat shim for the pre-package era. The real client is
# backend/esp32.py. Kept for reference only.
"""Backward-compatible shim — re-exports from backend.esp32"""
from backend.esp32 import *  # noqa: F401, F403
from backend.esp32 import ESP32Controller  # noqa: F401