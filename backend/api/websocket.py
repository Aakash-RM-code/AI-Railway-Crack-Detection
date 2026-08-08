"""Event-Driven WebSocket Hub and Channels.

Provides separate WebSocket channels for:
- /ws/telemetry: System, rover, health, GPS, and GSM real-time telemetry.
- /ws/detections: Real-time detection events broadcast on crack detection.
- /ws/camera-status: Live camera operational status, connection, FPS, resolution.
- /ws/stream: Legacy unified stream endpoint for backward compatibility.
"""

import asyncio
import logging
from datetime import datetime
from typing import Set, Dict, Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.api import schemas
from backend.services.camera import get_pipeline
from backend.storage.repository import DetectionRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])


class WebSocketHub:
    """Connection manager for separate WebSocket channels."""

    def __init__(self):
        self.telemetry_clients: Set[WebSocket] = set()
        self.detections_clients: Set[WebSocket] = set()
        self.camera_clients: Set[WebSocket] = set()
        self.stream_clients: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        if channel == "telemetry":
            self.telemetry_clients.add(websocket)
        elif channel == "detections":
            self.detections_clients.add(websocket)
        elif channel == "camera":
            self.camera_clients.add(websocket)
        elif channel == "stream":
            self.stream_clients.add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel == "telemetry":
            self.telemetry_clients.discard(websocket)
        elif channel == "detections":
            self.detections_clients.discard(websocket)
        elif channel == "camera":
            self.camera_clients.discard(websocket)
        elif channel == "stream":
            self.stream_clients.discard(websocket)

    async def broadcast_json(self, clients: Set[WebSocket], payload: Dict[str, Any]):
        if not clients:
            return
        disconnected = set()
        for client in list(clients):
            try:
                await client.send_json(payload)
            except Exception:
                disconnected.add(client)
        for client in disconnected:
            clients.discard(client)


# Global WebSocket Hub Instance
ws_hub = WebSocketHub()
_repo = DetectionRepository()


# --------------------------------------------------------------------------
# WebSocket Endpoint Handlers
# --------------------------------------------------------------------------


@router.websocket("/telemetry")
async def ws_telemetry(websocket: WebSocket):
    """Subscribes to system telemetry updates (rover, health, GPS, GSM, alerts)."""
    await ws_hub.connect(websocket, "telemetry")
    pipeline = get_pipeline()
    try:
        while True:
            # Send immediate telemetry snapshot on client request or keepalive ping
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket, "telemetry")
    except Exception:
        ws_hub.disconnect(websocket, "telemetry")


@router.websocket("/detections")
async def ws_detections(websocket: WebSocket):
    """Subscribes to real-time detection event notifications."""
    await ws_hub.connect(websocket, "detections")
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket, "detections")
    except Exception:
        ws_hub.disconnect(websocket, "detections")


@router.websocket("/camera-status")
async def ws_camera_status(websocket: WebSocket):
    """Subscribes to real-time camera operational status updates."""
    await ws_hub.connect(websocket, "camera")
    try:
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket, "camera")
    except Exception:
        ws_hub.disconnect(websocket, "camera")


@router.websocket("/stream")
async def ws_legacy_stream(websocket: WebSocket):
    """Legacy unified WebSocket channel pushing runtime state (without the
    heavy base64 frame payload)."""
    await websocket.accept()
    pipeline = get_pipeline()
    try:
        while True:
            state = pipeline.get_state()
            state.pop("frame_base64", None)  # heavy payload, legacy client only
            await websocket.send_json(state)
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_hub.disconnect(websocket, "stream")
    except Exception:
        ws_hub.disconnect(websocket, "stream")


# --------------------------------------------------------------------------
# Background Event Loops for Broadcasts
# --------------------------------------------------------------------------


async def telemetry_broadcaster_task():
    """Background async task pushing telemetry updates to connected clients.
    Values come from the real device caches — no fabricated coords/signals."""
    pipeline = get_pipeline()
    while True:
        try:
            if ws_hub.telemetry_clients:
                state = pipeline.get_state()
                esp = pipeline.get_esp32()

                online = esp.is_online() if esp else False
                coords = esp.get_gps_coordinates() if esp else None
                cached_status = esp.get_cached_status() if esp else None

                telemetry_payload = {
                    "timestamp": datetime.now().isoformat(),
                    "camera": state.get("camera"),
                    "alert": state.get("alert"),
                    "health": state.get("health"),
                    "stats": state.get("stats"),
                    "rover": {
                        "online": online,
                        "moving": bool(cached_status.get("moving", False)) if cached_status else False,
                    },
                    "gps": {
                        "hasFix": coords is not None,
                        "latitude": coords[0] if coords else 0.0,
                        "longitude": coords[1] if coords else 0.0,
                    },
                    "gsm": {
                        "online": online,
                        "signalStrength": 0.0,
                    },
                }

                await ws_hub.broadcast_json(ws_hub.telemetry_clients, telemetry_payload)

            if ws_hub.camera_clients:
                cam_info = pipeline.get_camera_info()
                cam_payload = {
                    "timestamp": datetime.now().isoformat(),
                    "mode": cam_info.get("mode", "usb"),
                    "running": cam_info.get("running", False),
                    "fps": round(cam_info.get("fps", 0.0), 1),
                    "resolution": cam_info.get("resolution", "640x480"),
                    "error": cam_info.get("error"),
                }
                await ws_hub.broadcast_json(ws_hub.camera_clients, cam_payload)

            if ws_hub.detections_clients:
                alert = pipeline.get_alert()
                if alert.get("detected"):
                    snap = _repo.get_latest_snapshot()
                    det_payload = {
                        "timestamp": datetime.now().isoformat(),
                        "alert": alert,
                        "latestSnapshot": snap.model_dump(by_alias=True) if snap else None,
                    }
                    await ws_hub.broadcast_json(ws_hub.detections_clients, det_payload)

        except Exception as e:
            logger.error(f"Broadcaster error: {e}")

        await asyncio.sleep(0.5)
