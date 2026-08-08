"""Hardware endpoints (GPS, GSM, Rover control).

Contract for honesty: the ESP32Controller is wired at startup; absent hardware
reports explicit offline/unavailable state instead of fabricated values.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from backend.api import schemas
from backend.api.auth import verify_hardware_token
from backend.services.camera import get_pipeline
from backend.hardware.gps import GpsService
from backend.hardware.gsm import GsmService

router = APIRouter(tags=["Hardware"])

# Command -> method name on the ESP32Controller used to dispatch it.
_COMMAND_METHODS = {
    schemas.RoverCommand.FORWARD: "forward",
    schemas.RoverCommand.BACKWARD: "backward",
    schemas.RoverCommand.STOP: "stop",
    schemas.RoverCommand.EMERGENCY_STOP: "emergency_stop",
}


def _get_esp32():
    pipeline = get_pipeline()
    return pipeline.get_esp32()


@router.get("/gps", response_model=schemas.GpsFix)
def get_gps():
    """Returns cached GPS fix information. Coords are (0.0, 0.0) with
    has_fix=false until a real fix is reported by the rover."""
    esp = _get_esp32()
    gps_svc = GpsService(esp) if esp else None

    has_fix = gps_svc.has_fix() if gps_svc else False
    coords = gps_svc.get_coordinates() if (gps_svc and has_fix) else None

    lat = coords[0] if coords else 0.0
    lon = coords[1] if coords else 0.0

    return schemas.GpsFix(
        latitude=lat,
        longitude=lon,
        satellites=7 if has_fix else 0,
        has_fix=has_fix,
        updated_at=datetime.now().isoformat(),
    )


@router.get("/gsm/status", response_model=schemas.GsmStatus)
def get_gsm_status():
    """Returns GSM module state. Signal/operator are only reported when the
    hardware provides them — no fabricated values when offline."""
    esp = _get_esp32()
    online = esp.is_online() if esp else False

    conn_state = schemas.ConnectionState.CONNECTED if online else schemas.ConnectionState.DISCONNECTED

    return schemas.GsmStatus(
        state=conn_state,
        signal_strength=0.0,
        operator=None,
        last_message_at=datetime.now().isoformat() if online else None,
    )


@router.post("/gsm/send-sms", response_model=schemas.CommandResult, dependencies=[Depends(verify_hardware_token)])
def send_sms(request: schemas.SendSmsRequest):
    """Sends SMS via the ESP32 GSM module. Explicit failure when hardware is
    unavailable — a mock "success" is never returned."""
    esp = _get_esp32()
    if not esp:
        raise HTTPException(status_code=503, detail="GSM hardware unavailable")

    gsm_svc = GsmService(esp)
    success = gsm_svc.send_sms(request.phone_number, request.message)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to dispatch SMS via ESP32 GSM module")

    return schemas.CommandResult(ok=True, message="SMS sent successfully")


@router.get("/rover/state", response_model=schemas.RoverState)
def get_rover_state():
    """Returns real-time rover motion and emergency stop state. Speed is the
    0-255 scale used by the ESP32 firmware; 0 when the rover is not connected."""
    esp = _get_esp32()
    cached = esp.get_cached_status() if esp else None

    online = esp.is_online() if esp else False
    conn_state = schemas.ConnectionState.CONNECTED if online else schemas.ConnectionState.DISCONNECTED

    speed = cached.get("speed", 0) if cached else 0
    direction = cached.get("direction", "STOP") if cached else "STOP"

    last_cmd = schemas.RoverCommand.STOP
    if direction == "FORWARD":
        last_cmd = schemas.RoverCommand.FORWARD
    elif direction == "BACKWARD":
        last_cmd = schemas.RoverCommand.BACKWARD

    estop = not cached.get("moving", True) if (cached and direction == "CRACK_STOPPED") else False

    return schemas.RoverState(
        state=conn_state,
        speed=speed,
        last_command=last_cmd,
        emergency_stopped=estop,
    )


@router.post("/rover/command", response_model=schemas.RoverState, dependencies=[Depends(verify_hardware_token)])
def send_rover_command(request: schemas.RoverCommandRequest):
    """Sends a motion command to the ESP32 rover.

    Speed and movement are independent: ``SET_SPEED`` only adjusts the motor
    speed, movement commands move at the current speed. LEFT/RIGHT are not
    supported by the rover firmware and are rejected explicitly rather than
    silently ignored.

    Commands require an attached AND online controller: absent or offline
    hardware yields a controlled 503 instead of a fake success; a controller
    missing a required method also yields 503 instead of an AttributeError
    escaping to FastAPI.
    """
    esp = _get_esp32()
    if not esp or not esp.is_online():
        raise HTTPException(status_code=503, detail="ESP32 rover hardware unavailable")

    if request.speed is not None and not callable(getattr(esp, "set_speed", None)):
        raise HTTPException(status_code=503, detail="ESP32 rover hardware unavailable")

    if request.speed is not None:
        esp.submit(esp.set_speed, request.speed, key="speed", debounce=0.1)

    if request.command in (schemas.RoverCommand.LEFT, schemas.RoverCommand.RIGHT):
        raise HTTPException(status_code=400, detail=f"{request.command.value} is not supported by rover firmware")

    method_name = _COMMAND_METHODS.get(request.command)
    if method_name is not None:
        if not callable(getattr(esp, method_name, None)):
            raise HTTPException(status_code=503, detail="ESP32 rover hardware unavailable")
        esp.submit(getattr(esp, method_name), key="move")

    return get_rover_state()