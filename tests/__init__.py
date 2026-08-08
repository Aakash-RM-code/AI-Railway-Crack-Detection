"""Test-suite bootstrap.

Sets non-network environment defaults so backend imports pick up a
hardware-free configuration deterministically.
"""

import os

os.environ["ESP32_ENABLED"] = "false"
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "*")