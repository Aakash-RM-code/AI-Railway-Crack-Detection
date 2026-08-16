"""Camera control and video streaming routes."""

import requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

import config
from backend.api import schemas
from backend.api.auth import verify_hardware_token
from backend.services.camera import get_pipeline

router = APIRouter(tags=["Camera"])

# ESP32-CAM is the only production camera source.
CAMERA_SOURCE_MODE = "esp32cam"


def _build_camera_state() -> schemas.CameraState:
    pipeline = get_pipeline()
    info = pipeline.get_camera_info()
    res = info.get("resolution", "640 x 480")
    w, h = 640, 480
    if "×" in res:
        parts = res.split("×")
        try:
            w, h = int(parts[0].strip()), int(parts[1].strip())
        except (ValueError, IndexError):
            pass
    elif "x" in res:
        parts = res.split("x")
        try:
            w, h = int(parts[0].strip()), int(parts[1].strip())
        except (ValueError, IndexError):
            pass

    conn_state = schemas.ConnectionState.CONNECTED if info.get("running") else schemas.ConnectionState.DISCONNECTED
    if info.get("error"):
        conn_state = schemas.ConnectionState.ERROR

    return schemas.CameraState(
        source=schemas.CameraSource.ESP32_CAM,
        state=conn_state,
        fps=round(info.get("fps", 0.0), 1),
        width=w,
        height=h,
        detection_active=info.get("running", False),
        stream_url="/api/camera/stream" if info.get("running") else None,
        camera_fps=round(info.get("camera_fps", 0.0), 1),
        display_fps=round(info.get("display_fps", 0.0), 1),
        inference_fps=round(info.get("inference_fps", 0.0), 1),
        native_stream_url=config.ESP32CAM_STREAM_URL,
    )


@router.get("/camera/state", response_model=schemas.CameraState)
def get_camera_state():
    """Returns detailed camera state matching frontend CameraState model."""
    return _build_camera_state()


@router.post("/camera/connect", response_model=schemas.CameraState, dependencies=[Depends(verify_hardware_token)])
def connect_camera(request: schemas.CameraConnectRequest):
    """Connects the ESP32-CAM source (the only production camera source)."""
    pipeline = get_pipeline()

    ok = pipeline.set_camera_source(CAMERA_SOURCE_MODE, force=True)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Failed to connect to camera source: {request.source}")

    if not pipeline.is_running():
        pipeline.start()

    return _build_camera_state()


@router.post("/camera/disconnect", response_model=schemas.CameraState, dependencies=[Depends(verify_hardware_token)])
def disconnect_camera():
    """Disconnects the active camera."""
    pipeline = get_pipeline()
    pipeline.stop()
    return _build_camera_state()


@router.get("/camera/stream")
def camera_stream():
    """Transparent byte-stream proxy forwarding the ESP32-CAM MJPEG feed.

    The browser renders the ESP32-CAM native MJPEG stream directly whenever
    possible. This endpoint is a fallback proxy for environments where the
    browser cannot reach the camera. No decode, re-encode, or Base64.
    """
    pipeline = get_pipeline()
    if not pipeline.is_running():
        pipeline.start()

    try:
        resp = requests.get(config.ESP32CAM_STREAM_URL, stream=True, timeout=(3, 30))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"ESP32-CAM stream unavailable: {exc}")

    content_type = resp.headers.get("Content-Type", "multipart/x-mixed-replace; boundary=frame")

    def _proxy():
        try:
            if resp.status_code != 200:
                return
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    for _ in range(chunk.count(b"\xff\xd8")):
                        pipeline.note_display_frame()
                    yield chunk
        finally:
            resp.close()

    return StreamingResponse(_proxy(), media_type=content_type)


# --------------------------------------------------------------------------
# Legacy endpoints
# --------------------------------------------------------------------------


@router.get("/camera/status", response_model=schemas.CameraStatus)
def legacy_camera_status():
    return get_pipeline().get_camera_info()


@router.post("/camera/start")
def legacy_camera_start():
    return {"running": get_pipeline().start()}


@router.post("/camera/stop")
def legacy_camera_stop():
    pipeline = get_pipeline()
    pipeline.stop()
    return {"running": pipeline.is_running()}

