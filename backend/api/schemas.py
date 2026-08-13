"""Pydantic schemas for the Railway Crack Detection API.

All domain models inherit from BaseCamelModel which automatically generates
camelCase aliases for JSON serialization, matching the React frontend contract while
accepting either camelCase or snake_case inputs.
"""

from enum import Enum
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseCamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


# --------------------------------------------------------------------------
# Enums mirroring frontend types (frontend/src/types/monitoring.ts)
# --------------------------------------------------------------------------


class Severity(str, Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CrackClass(str, Enum):
    SMALL_CRACK = "small_crack"
    MEDIUM_CRACK = "medium_crack"
    LARGE_CRACK = "large_crack"
    BROKEN_CHAIN = "broken_chain"


class ConnectionState(str, Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class DeviceId(str, Enum):
    CAMERA = "camera"
    ESP32 = "esp32"
    GPS = "gps"
    GSM = "gsm"


class CameraSource(str, Enum):
    USB = "usb"
    ESP32_CAM = "esp32-cam"
    DEMO_VIDEO = "demo-video"


class RoverCommand(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"
    STOP = "stop"
    EMERGENCY_STOP = "emergency_stop"
    SET_SPEED = "set_speed"


class HealthStatus(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"


class DetectionStatus(str, Enum):
    NEW = "new"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"


# --------------------------------------------------------------------------
# Core Domain Models
# --------------------------------------------------------------------------


class DeviceStatus(BaseCamelModel):
    id: DeviceId
    label: str
    state: ConnectionState
    detail: Optional[str] = None


class SystemStatus(BaseCamelModel):
    online: bool
    uptime_seconds: float
    version: str
    devices: List[DeviceStatus]


class CameraState(BaseCamelModel):
    source: CameraSource
    state: ConnectionState
    fps: float
    width: int
    height: int
    detection_active: bool
    stream_url: Optional[str] = None
    camera_fps: float = 0.0
    display_fps: float = 0.0
    inference_fps: float = 0.0
    native_stream_url: Optional[str] = None


class Alert(BaseCamelModel):
    id: str
    severity: Severity
    crack_class: Optional[CrackClass] = None
    confidence: float
    message: str
    timestamp: str


class TrackHealth(BaseCamelModel):
    overall: float
    status: HealthStatus
    inspected_meters: float
    updated_at: str


class GpsFix(BaseCamelModel):
    latitude: float
    longitude: float
    satellites: int
    has_fix: bool
    updated_at: str


class GsmStatus(BaseCamelModel):
    state: ConnectionState
    signal_strength: float
    operator: Optional[str] = None
    last_message_at: Optional[str] = None


class Statistics(BaseCamelModel):
    total_detections: int
    small_crack: int
    medium_crack: int
    large_crack: int
    broken_chain: int
    critical_alerts: int


class SeverityTrendPoint(BaseCamelModel):
    timestamp: str
    low: int
    medium: int
    high: int
    critical: int


class DetectionDistributionSlice(BaseCamelModel):
    crack_class: CrackClass
    count: int


class Detection(BaseCamelModel):
    id: str
    timestamp: str
    crack_class: CrackClass
    confidence: float
    severity: Severity
    latitude: float
    longitude: float
    status: DetectionStatus = DetectionStatus.NEW


class Snapshot(BaseCamelModel):
    id: str
    image_url: Optional[str] = None
    timestamp: str
    severity: Severity
    crack_class: Optional[CrackClass] = None


class RoverState(BaseCamelModel):
    state: ConnectionState
    speed: int
    last_command: Optional[RoverCommand] = None
    emergency_stopped: bool


# --------------------------------------------------------------------------
# Query & Request/Response Payloads
# --------------------------------------------------------------------------


T = TypeVar("T")


class Paginated(BaseCamelModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int


class SendSmsRequest(BaseCamelModel):
    phone_number: str
    message: str


class CommandResult(BaseCamelModel):
    ok: bool
    message: str


class RoverCommandRequest(BaseCamelModel):
    command: RoverCommand
    speed: Optional[int] = Field(default=None, ge=0, le=255)


class CameraConnectRequest(BaseCamelModel):
    source: CameraSource
    video_path: Optional[str] = None


class ReportResponse(BaseCamelModel):
    path: str
    url: str


# --------------------------------------------------------------------------
# Legacy / Backward Compatibility Schemas
# --------------------------------------------------------------------------


class CameraStatus(BaseCamelModel):
    mode: str
    running: bool
    fps: float
    resolution: str
    error: Optional[str] = None


class LegacyAlert(BaseCamelModel):
    detected: bool
    severity: str
    class_name: Optional[str] = None
    confidence: float
    message: str


class Stats(BaseCamelModel):
    total: int
    small: int
    medium: int
    large: int
    broken: int


class Health(BaseCamelModel):
    score: int
    status: str
    note: str


class RuntimeState(BaseCamelModel):
    camera: CameraStatus
    frame_base64: str = ""
    alert: LegacyAlert
    stats: Stats
    severity_counts: dict[str, int]
    health: Health


class HistoryRow(BaseCamelModel):
    time: str
    crack_type: str
    confidence: float
    image: str


class CameraSourceRequest(BaseCamelModel):
    mode: str
    force: bool = False


class SpeedRequest(BaseCamelModel):
    speed: int = Field(ge=0, le=255)
