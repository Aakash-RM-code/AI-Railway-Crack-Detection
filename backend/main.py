"""FastAPI application entry point.

Run with:

    uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload

Assembles the HTTP routes, WebSockets, CORS middleware, ESP32 hardware wiring,
and background telemetry tasks.

Lifecycle:
* Startup — construct the ESP32Controller (if enabled), start its polling
  thread, and attach it to the shared CameraPipeline so hardware endpoints
  operate against real device state.
* Shutdown — cancel the telemetry broadcaster, stop polling, and release both
  the controller and the camera pipeline.
"""

import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config
from backend.api.routes import router as api_router
from backend.api.websocket import router as ws_router, telemetry_broadcaster_task

# Make application INFO logs (detector model/precision selection, hardware
# status, pipeline events) visible under uvicorn, whose default root level is
# WARNING. uvicorn's own loggers are configured by uvicorn itself.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Railway Crack Detection & Rover Monitoring API",
    version="1.0.0",
    description="Production REST & WebSocket API backend for AI TrackSense railway monitoring system.",
)

# Configure CORS. `*` + allow_credentials is invalid for credentialed
# browsers, so we never combine them: wide-open only for local development,
# explicit-origin list otherwise.
_cors_origins = [o.strip() for o in config.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
_allow_credentials = "*" not in _cors_origins and bool(_cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["*"],
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API and WebSocket routers
app.include_router(api_router)
app.include_router(ws_router)

_broadcaster_task = None
_esp32_controller = None


@app.on_event("startup")
async def startup_event() -> None:
    """Start background async tasks and wire hardware on application startup."""
    global _broadcaster_task, _esp32_controller

    # Production requires an API token; fail fast rather than exposing a
    # hardware-control API with no auth. Development/tests keep working open.
    if config.APP_ENV == "production" and not config.API_AUTH_TOKEN:
        raise RuntimeError(
            "APP_ENV=production requires a non-empty API_AUTH_TOKEN. "
            "Set API_AUTH_TOKEN in the environment; never hardcode it."
        )

    from backend.hardware.esp32 import ESP32Controller
    from backend.services.camera import get_pipeline

    if config.ESP32_ENABLED:
        controller = ESP32Controller(config.ESP32_BASE_URL)
        controller.start_polling(config.POLLING_INTERVAL)
        # Queue a best-effort connect check on the background polling thread
        # instead of blocking startup for up to 9s when ESP32 is offline.
        controller.submit(controller.connect, key="initial_connect")
        _esp32_controller = controller
        # Attach before or after pipeline creation — set_esp32 handles both.
        get_pipeline(esp32_controller=controller)
    else:
        get_pipeline()

    _broadcaster_task = asyncio.create_task(telemetry_broadcaster_task())


@app.on_event("shutdown")
def shutdown_event() -> None:
    """Clean up camera pipeline, background tasks, and hardware connections on shutdown."""
    global _broadcaster_task, _esp32_controller
    if _broadcaster_task is not None:
        _broadcaster_task.cancel()

    from backend.services.camera import get_existing_pipeline

    pipeline = get_existing_pipeline()
    if pipeline is not None:
        pipeline.close()

    if _esp32_controller is not None:
        _esp32_controller.close()
        _esp32_controller = None