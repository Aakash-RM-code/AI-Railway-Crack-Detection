"""Camera control and video streaming routes."""

import os
import time
import base64
import cv2
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

import config
from backend.api import schemas
from backend.api.auth import verify_hardware_token
from backend.services.camera import get_pipeline

router = APIRouter(tags=["Camera"])


def _map_source_to_backend(source: schemas.CameraSource) -> str:
    if source == schemas.CameraSource.ESP32_CAM:
        return "esp32cam"
    elif source == schemas.CameraSource.DEMO_VIDEO:
        return "demo"
    return "usb"


def _map_backend_to_frontend_source(mode: str) -> schemas.CameraSource:
    mode_str = (mode or "usb").lower()
    if mode_str == "esp32cam":
        return schemas.CameraSource.ESP32_CAM
    elif mode_str == "demo":
        return schemas.CameraSource.DEMO_VIDEO
    return schemas.CameraSource.USB


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

    fe_source = _map_backend_to_frontend_source(info.get("mode", "usb"))

    return schemas.CameraState(
        source=fe_source,
        state=conn_state,
        fps=round(info.get("fps", 0.0), 1),
        width=w,
        height=h,
        detection_active=info.get("running", False),
        stream_url="/api/camera/stream" if info.get("running") else None,
    )


@router.get("/camera/state", response_model=schemas.CameraState)
def get_camera_state():
    """Returns detailed camera state matching frontend CameraState model."""
    return _build_camera_state()


@router.post("/camera/connect", response_model=schemas.CameraState, dependencies=[Depends(verify_hardware_token)])
def connect_camera(request: schemas.CameraConnectRequest):
    """Connects or switches camera source."""
    pipeline = get_pipeline()
    be_mode = _map_source_to_backend(request.source)

    if request.video_path:
        pipeline.set_demo_video_path(request.video_path)

    ok = pipeline.set_camera_source(be_mode, force=True)
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


def _mjpeg_generator():
    """Generator yielding JPEG frames for HTTP MJPEG streaming.

    Paced at ~30 FPS and only transmits a JPEG when the camera has produced a
    genuinely new frame (tracked by a monotonic frame ID). Repeatedly polling
    the same cached JPEG is never sent again, so the browser never sees a
    fabricated frame rate.
    """
    pipeline = get_pipeline()
    last_sent_id = 0
    while True:
        jpg_bytes = pipeline.get_frame_jpeg()
        frame_id = pipeline.get_frame_jpeg_id()
        if jpg_bytes and frame_id != last_sent_id:
            last_sent_id = frame_id
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + jpg_bytes + b"\r\n"
            )
        else:
            if not pipeline.is_running() and pipeline.camera_error():
                break
        time.sleep(0.033)  # ~30 FPS pacing


@router.get("/camera/stream")
def camera_stream():
    """Streams live MJPEG video feed for direct browser <img> tag consumption."""
    pipeline = get_pipeline()
    if not pipeline.is_running():
        pipeline.start()
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


# --------------------------------------------------------------------------
# Legacy endpoints
# --------------------------------------------------------------------------


@router.get("/camera/status", response_model=schemas.CameraStatus)
def legacy_camera_status():
    return get_pipeline().get_camera_info()


@router.get("/camera/frame")
def legacy_camera_frame():
    return {"frame_base64": get_pipeline().get_frame_base64()}


@router.post("/camera/start")
def legacy_camera_start():
    return {"running": get_pipeline().start()}


@router.post("/camera/stop")
def legacy_camera_stop():
    pipeline = get_pipeline()
    pipeline.stop()
    return {"running": pipeline.is_running()}


@router.post("/camera/source", response_model=schemas.CameraStatus)
def legacy_camera_source(body: schemas.CameraSourceRequest):
    pipeline = get_pipeline()
    ok = pipeline.set_camera_source(body.mode, force=body.force)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Unknown camera source: {body.mode}")
    return pipeline.get_camera_info()


# --------------------------------------------------------------------------
# Demo video file upload
# --------------------------------------------------------------------------

_ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".webm"}


@router.post("/uploads/video", response_model=schemas.CameraState, dependencies=[Depends(verify_hardware_token)])
def upload_demo_video(file: UploadFile = File(...)):
    """Accept a video file upload, save to uploads/, switch pipeline to demo mode.

    The browser sends the file via multipart/form-data — no raw filesystem path
    is passed from the client. The backend validates the extension, saves the
    file to config.UPLOADS_DIR, and starts the demo pipeline.
    """
    filename = file.filename or "uploaded_video"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in _ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format '{ext}'. Allowed: {', '.join(sorted(_ALLOWED_VIDEO_EXTENSIONS))}",
        )

    os.makedirs(config.UPLOADS_DIR, exist_ok=True)
    save_path = os.path.join(config.UPLOADS_DIR, filename)

    try:
        with open(save_path, "wb") as out:
            while chunk := file.file.read(1024 * 1024):  # 1 MB chunks
                out.write(chunk)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {exc}")

    pipeline = get_pipeline()
    pipeline.set_demo_video_path(save_path)
    pipeline.set_camera_source("demo", force=True)

    if not pipeline.is_running():
        pipeline.start()

    return _build_camera_state()
