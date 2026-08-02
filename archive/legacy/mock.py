# ARCHIVED — mock/demo data constants from the early UI prototype. Not used by
# the live application (ui/components read live controller state). Kept for
# reference in case a mock dashboard is ever needed.
VERSION = "1.0.0"
DEVELOPER = "AI TrackSense Team"

ALERT = {
    "severity": "HIGH",
    "class_name": "large crack",
    "confidence": 0.87,
    "recommendation": "Immediate inspection required. Dispatch maintenance crew and restrict traffic to 15 km/h.",
}

STATS = {
    "total": 47,
    "small": 21,
    "medium": 15,
    "large": 8,
    "broken": 3,
    "critical": 5,
}

HEALTH = {
    "score": 72,
    "status": "WARNING",
    "note": "Degradation trend detected in the last 2 km of track.",
}

GPS = {
    "lat": 27.204622,
    "lon": 77.497662,
    "altitude": 216.4,
    "speed": 38.2,
    "satellites": 12,
    "status": "3D FIX",
}

GSM = {
    "phone": "+91 98765 43210",
    "status": "MODULE STANDBY",
    "note": "GSM hardware not detected",
}

HISTORY = [
    {"time": "2026-07-22 20:42:35", "crack_type": "large crack", "confidence": 0.87, "image": "20260722_204235.jpg"},
    {"time": "2026-07-22 20:42:42", "crack_type": "small crack", "confidence": 0.71, "image": "20260722_204242.jpg"},
    {"time": "2026-07-22 20:42:47", "crack_type": "medium crack", "confidence": 0.82, "image": "20260722_204247.jpg"},
    {"time": "2026-07-22 20:42:52", "crack_type": "broken chain", "confidence": 0.91, "image": "20260722_204252.jpg"},
    {"time": "2026-07-22 20:42:58", "crack_type": "small crack", "confidence": 0.76, "image": "20260722_204258.jpg"},
    {"time": "2026-07-22 20:43:03", "crack_type": "medium crack", "confidence": 0.84, "image": "20260722_204303.jpg"},
    {"time": "2026-07-22 20:43:08", "crack_type": "large crack", "confidence": 0.89, "image": "20260722_204308.jpg"},
    {"time": "2026-07-22 20:43:13", "crack_type": "small crack", "confidence": 0.73, "image": "20260722_204313.jpg"},
    {"time": "2026-07-22 20:43:18", "crack_type": "medium crack", "confidence": 0.79, "image": "20260722_204318.jpg"},
    {"time": "2026-07-22 21:01:26", "crack_type": "broken chain", "confidence": 0.94, "image": "20260722_210126.jpg"},
]

BAR_DATA = [
    ("Small", 21),
    ("Medium", 15),
    ("Large", 8),
    ("Broken", 3),
]

PIE_DATA = [
    ("SAFE", 42),
    ("LOW", 21),
    ("MEDIUM", 15),
    ("HIGH", 8),
    ("CRITICAL", 3),
]
