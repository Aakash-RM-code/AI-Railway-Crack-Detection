"""Imaging helpers shared across backend services."""

import cv2


def cv2_imencode(frame) -> tuple[bool, bytes]:
    """Encode a BGR frame to JPEG bytes. Returns (ok, buffer)."""
    return cv2.imencode(".jpg", frame)


def jpeg_base64(frame) -> str:
    """Encode a BGR frame to a base64 data string, or "" on failure."""
    import base64

    ok, buf = cv2_imencode(frame)
    if not ok:
        return ""
    return base64.b64encode(buf).decode("ascii")
