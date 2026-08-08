"""System status and health check routes."""

import time
from datetime import datetime
from fastapi import APIRouter

from backend.api import schemas
from backend.services.camera import get_pipeline

router = APIRouter(tags=["System"])

START_TIME = time.time()


@router.get("/health")
def health():
    """Liveness probe for backend services."""
    return {"status": "ok"}


@router.get("/system/status", response_model=schemas.SystemStatus)
def get_system_status():
    """Returns overall system online state, uptime, version, and hardware device statuses."""
    uptime = time.time() - START_TIME
    pipeline = get_pipeline()
    cam_info = pipeline.get_camera_info()
    esp = pipeline.get_esp32()

    camera_state = schemas.ConnectionState.CONNECTED if cam_info.get("running") else schemas.ConnectionState.DISCONNECTED
    if cam_info.get("error"):
        camera_state = schemas.ConnectionState.ERROR

    devices = [
        schemas.DeviceStatus(
            id=schemas.DeviceId.CAMERA,
            label="Camera Module",
            state=camera_state,
            detail=cam_info.get("resolution", "640x480"),
        ),
        schemas.DeviceStatus(
            id=schemas.DeviceId.ESP32,
            label="ESP32 Rover Controller",
            state=schemas.ConnectionState.CONNECTED if esp and esp.is_online() else schemas.ConnectionState.DISCONNECTED,
            detail="Wi-Fi Rover Link",
        ),
        schemas.DeviceStatus(
            id=schemas.DeviceId.GPS,
            label="NEO-6M GPS Receiver",
            state=schemas.ConnectionState.CONNECTED if esp and esp.get_cached_gps() != "NO_FIX" else schemas.ConnectionState.DISCONNECTED,
            detail="NMEA Receiver",
        ),
        schemas.DeviceStatus(
            id=schemas.DeviceId.GSM,
            label="SIM800L GSM Module",
            state=schemas.ConnectionState.CONNECTED if esp and esp.is_online() else schemas.ConnectionState.DISCONNECTED,
            detail="Cellular Gateway",
        ),
    ]

    return schemas.SystemStatus(
        online=True,
        uptime_seconds=round(uptime, 1),
        version="1.0.0",
        devices=devices,
    )
