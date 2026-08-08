"""
Tiny storage helper for the GSM operator phone number.
Keeps it in its own CSV (config/gsm_settings.csv) rather than mixing it
into logs/detections.csv, which should stay pure detection records.
"""

import csv
import os
from datetime import datetime

import config

SETTINGS_PATH = config.GSM_SETTINGS_CSV


def _ensure_file():
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    if not os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["phone_number", "updated_at"])


def save_phone_number(phone: str) -> None:
    """Overwrites the stored number (single-operator setup). For multiple
    operators, switch this to append mode instead."""
    _ensure_file()
    with open(SETTINGS_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["phone_number", "updated_at"])
        writer.writerow([phone, datetime.now().isoformat(timespec="seconds")])


def load_phone_number() -> str | None:
    _ensure_file()
    with open(SETTINGS_PATH, "r", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None
    return rows[1][0] or None
