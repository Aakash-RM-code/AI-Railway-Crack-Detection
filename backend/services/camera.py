"""Camera service — ESP32-CAM-first capture, detection pipeline, and runtime state.

Simplified for minimum practical latency:

* ``CameraManager`` — owns the active source (ESP32-CAM), runs an acquisition
  thread that retains ONLY the newest frame, and reconnects automatically with
  bounded backoff on failure.
* ``CameraPipeline`` — the long-running service. Runs the capture loop and an
  asynchronous latest-frame-wins inference worker, and holds the shared runtime
  state (latest frame, latest detection, alert, stats, health, FPS metrics).

Display is NOT produced by the backend: the browser renders the ESP32-CAM native
MJPEG stream directly (with a transparent byte-stream proxy fallback) and draws
the detection overlay from WebSocket metadata. The backend only captures frames
for AI inference, so the live video path never waits on YOLO.
"""

import threading
import time
from datetime import datetime
from urllib.request import urlopen

import cv2
import numpy as np

import config

from backend.detector.detector import CrackDetector
from backend.services.alert_manager import AlertManager
from backend.services.statistics_manager import StatisticsManager
from backend.services.logger import DetectionLogger

SEVERITY_LEVELS = ("SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL")


# --------------------------------------------------------------------------
# CameraManager — source management + detection pipeline
# --------------------------------------------------------------------------


class CameraManager:

    SOURCES = ("esp32cam",)

    MAX_REOPEN_DELAY = 30.0

    def __init__(self, mode: str | None = None):
        self.detector = CrackDetector(config.MODEL_PATH)
        # Absorb OpenVINO first-inference compile latency before live frames.
        self.detector.warmup()
        self.alert_manager = AlertManager()
        self.statistics = StatisticsManager()
        self.logger = DetectionLogger()

        self._lock = threading.RLock()
        self.mode = (mode or getattr(config, "CAMERA_MODE", "esp32cam")).strip().lower()
        if self.mode not in self.SOURCES:
            raise ValueError(f"Unknown camera source: {self.mode}")

        self._cap = None
        self._snapshot_url = ""
        self._running = False
        self._acq_thread = None
        self._latest_frame = None
        self._latest_frame_id = 0
        self._error = None
        self._connected = False
        self._read_fail_count = 0
        self._reopen_delay = 2.0
        self._last_reopen_time = 0.0

        self._open_source()

    # ------------------------------------------------------------------ source management

    def _open_source(self) -> None:
        self._close_source()
        self._connected = False
        self._error = None

        if self.mode == "esp32cam":
            stream_url = getattr(config, "ESP32CAM_STREAM_URL", "")
            cap = cv2.VideoCapture(stream_url)
            if cap.isOpened():
                self._cap = cap
            else:
                cap.release()
                self._snapshot_url = getattr(config, "ESP32CAM_SNAPSHOT_URL", "")
                if not self._snapshot_url:
                    raise RuntimeError("ESP32-CAM stream/snapshot URL not configured")
        else:
            raise ValueError(f"Unknown camera source: {self.mode}")

        self._connected = True

    def _close_source(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None
        self._snapshot_url = ""

    def _reopen_source(self) -> None:
        """Best-effort reopen of the active source after read failures.

        Uses bounded backoff (2s → 4s → … capped at MAX_REOPEN_DELAY) so a dead
        camera never spins the acquisition thread hot. Resets the backoff on a
        successful reopen. Safe to call only from the acquisition thread.
        """
        try:
            self._open_source()
            self._reopen_delay = 2.0
        except Exception as exc:
            self._error = f"Cannot reopen camera: {exc}"
            self._reopen_delay = min(self._reopen_delay * 2.0, self.MAX_REOPEN_DELAY)

    def start(self) -> None:
        with self._lock:
            if self._running:
                return
            self._running = True
        self._acq_thread = threading.Thread(target=self._acquire_loop, daemon=True, name="CameraAcquisition")
        self._acq_thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False
        thread = self._acq_thread
        if thread and thread.is_alive():
            thread.join(timeout=3.0)

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def is_connected(self) -> bool:
        return self._connected

    def error(self) -> str | None:
        return self._error

    # ------------------------------------------------------------------ acquisition

    def _acquire_loop(self) -> None:
        while True:
            with self._lock:
                if not self._running:
                    return
            frame = self._read_once()
            with self._lock:
                if not self._running:
                    return
                if frame is not None:
                    self._latest_frame = frame
                    self._latest_frame_id += 1
            time.sleep(0.005)

    def _read_once(self):
        if self._cap is not None:
            ret, frame = self._cap.read()
            if not ret:
                self._connected = False
                self._read_fail_count += 1
                if self._read_fail_count == 1:
                    self._error = "Camera frame read failed"
                now = time.time()
                if now - self._last_reopen_time > self._reopen_delay:
                    self._last_reopen_time = now
                    self._reopen_source()
                return None
            self._connected = True
            self._error = None
            self._read_fail_count = 0
            return frame
        if self._snapshot_url:
            return self._fetch_snapshot()
        return None

    def _fetch_snapshot(self):
        try:
            with urlopen(self._snapshot_url, timeout=3) as resp:
                data = resp.read()
            arr = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                return None
            self._connected = True
            self._error = None
            self._read_fail_count = 0
            return frame
        except Exception:
            self._connected = False
            if self._read_fail_count == 0:
                self._error = "ESP32-CAM unreachable"
            self._read_fail_count += 1
            return None

    def read_frame(self):
        with self._lock:
            return self._latest_frame

    def read_frame_id(self):
        """Return the monotonic ID of the latest acquired camera frame.

        Increments exactly once per successful read() in the acquisition loop,
        so callers can detect genuinely new frames versus repeated polling of
        the same cached frame.
        """
        with self._lock:
            return self._latest_frame_id

    # ------------------------------------------------------------------ processing

    def process_frame(self, frame):
        """Run the detection pipeline for a frame.

        Returns a dict with the raw frame, raw results, the generated alert, and
        the updated statistics. Detection, alert, persistence and statistics are
        unchanged; the annotated plot is no longer produced here — overlays are
        drawn in the browser from detection metadata.
        """
        results = self.detector.detect(frame)
        alert = self.alert_manager.process(results, self.detector.model.names)

        if alert["detected"]:
            self.statistics.update(alert["class_name"])

        logged = False
        if len(results[0].boxes) > 0:
            best = max(results[0].boxes, key=lambda b: float(b.conf[0]))
            cls = int(best.cls[0])
            conf = float(best.conf[0])
            logged = self.logger.save_detection(
                frame,
                self.detector.model.names[cls],
                conf,
            )

        return {
            "frame": frame,
            "results": results,
            "alert": alert,
            "stats": self.statistics.get_stats(),
            "logged": logged,
        }

    def close(self):
        self.stop()
        self._close_source()


# --------------------------------------------------------------------------
# CameraPipeline — long-running capture loop + shared runtime state
# --------------------------------------------------------------------------


class CameraPipeline:
    """Background pipeline that reads frames from a CameraManager, runs the
    decoupled detection pipeline, and maintains the shared runtime state that
    the API layer exposes.

    Decoupled Architecture:
    - Camera capture runs continuously on a background thread and retains ONLY
      the newest raw frame. The live display is the ESP32-CAM native stream and
      never touches this thread.
    - AI inference runs on a separate background thread using a
      latest-frame-wins strategy (~10-16 FPS). Streaming never waits for
      inference and inference never blocks capture.
    """

    def __init__(self, mode: str | None = None, esp32_controller=None):
        self._lock = threading.RLock()
        self._started_at = datetime.now()
        self._esp = esp32_controller or None
        self._running = False
        self._camera_error: str | None = None
        self._camera_mode = (mode or getattr(config, "CAMERA_MODE", "esp32cam")).strip().lower()
        self._camera_thread = None
        self._inference_thread = None

        self._latest_raw_frame = None
        self._latest_raw_id = 0
        self._latest_raw_time = 0.0
        self._latest_detection = {"detections": [], "timestamp": 0.0}
        self._last_frame_time = time.time()
        self._fps = 0.0
        self._inference_fps = 0.0
        self._display_fps = 0.0
        self._proxy_used = False
        self._display_frame_count = 0
        self._display_start_time = 0.0
        self._resolution = "--"
        self._alert = {
            "detected": False,
            "severity": "SAFE",
            "class_name": None,
            "confidence": 0.0,
            "message": "Track is Safe",
        }
        self._stats = {"total": 0, "small": 0, "medium": 0, "large": 0, "broken": 0}
        self._severity_counts = {level: 0 for level in SEVERITY_LEVELS}
        self._health_score = 100
        self._health_status = "EXCELLENT"
        self._health_note = "Track in good condition"
        self._estop_armed = True

    # ------------------------------------------------------------------ lifecycle

    def set_esp32(self, controller) -> None:
        """Attach (or replace) the ESP32 controller, enabling hardware wiring
        for a pipeline that was already created without one."""
        with self._lock:
            self._esp = controller

    def get_esp32(self):
        """Return the attached ESP32 controller, or None if not wired."""
        with self._lock:
            return self._esp

    def start(self) -> bool:
        with self._lock:
            if self._running:
                return True
            self._running = True
            self._camera_error = None
            self._camera_thread = threading.Thread(target=self._camera_loop, daemon=True, name="CameraStreamLoop")
        self._camera_thread.start()
        return True

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def close(self) -> None:
        """Stop the camera loop and inference worker thread."""
        self.stop()
        self._join_threads()

    def _join_threads(self, timeout: float = 5.0) -> None:
        c_thread = self._camera_thread
        if c_thread and c_thread.is_alive():
            c_thread.join(timeout=timeout)
        self._camera_thread = None

        i_thread = self._inference_thread
        if i_thread and i_thread.is_alive():
            i_thread.join(timeout=timeout)
        self._inference_thread = None

    # ------------------------------------------------------------------ camera source switching

    def set_camera_source(self, mode: str, force: bool = False) -> bool:
        """Switch the active camera source without restarting the service."""
        mode = (mode or "").strip().lower()

        if mode not in CameraManager.SOURCES:
            return False
        with self._lock:
            if mode == self._camera_mode and not force and self._running:
                return True
            was_running = self._running
            self._running = False
        self._join_threads()
        with self._lock:
            self._camera_mode = mode
            self._camera_error = None
            self._latest_raw_frame = None
            self._latest_raw_id = 0
            self._latest_raw_time = 0.0
            self._latest_detection = {"detections": [], "timestamp": 0.0}
            self._last_frame_time = time.time()
            self._proxy_used = False
            self._display_start_time = 0.0
            self._display_frame_count = 0
        if was_running:
            self.start()
        return True

    def reconnect_camera(self) -> bool:
        with self._lock:
            mode = self._camera_mode
        return self.set_camera_source(mode, force=True)

    # ------------------------------------------------------------------ state accessors

    def get_camera_source(self) -> str:
        with self._lock:
            return self._camera_mode

    def get_camera_info(self) -> dict:
        with self._lock:
            return {
                "mode": self._camera_mode,
                "running": self._running,
                "fps": self._fps,
                "camera_fps": self._fps,
                "display_fps": self._display_fps,
                "inference_fps": self._inference_fps,
                "resolution": self._resolution,
                "error": self._camera_error,
            }

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def started_at(self) -> datetime:
        return self._started_at

    def camera_error(self) -> str | None:
        with self._lock:
            return self._camera_error

    def get_camera_fps(self) -> float:
        with self._lock:
            return self._fps

    def get_display_fps(self) -> float:
        with self._lock:
            return self._display_fps

    def get_inference_fps(self) -> float:
        with self._lock:
            return self._inference_fps

    def get_resolution(self) -> str:
        with self._lock:
            return self._resolution

    def get_alert(self) -> dict:
        with self._lock:
            return dict(self._alert)

    def get_stats(self) -> dict:
        with self._lock:
            return dict(self._stats)

    def get_severity_counts(self) -> dict:
        with self._lock:
            return dict(self._severity_counts)

    def get_health(self) -> dict:
        with self._lock:
            return {
                "score": self._health_score,
                "status": self._health_status,
                "note": self._health_note,
            }

    def get_latest_detection(self) -> dict:
        """Return the most recent inference result with per-box metadata.

        Payload: ``{"detections": [{class_name, confidence, severity, bbox}], "timestamp"}``.
        ``bbox`` is ``[x1, y1, x2, y2]`` in the source frame's pixel space.
        """
        with self._lock:
            return {
                "detections": [dict(d) for d in self._latest_detection["detections"]],
                "timestamp": self._latest_detection["timestamp"],
            }

    def get_state(self) -> dict:
        """Full snapshot of the runtime state for the API/websocket layer."""
        with self._lock:
            return {
                "camera": {
                    "mode": self._camera_mode,
                    "running": self._running,
                    "fps": self._fps,
                    "camera_fps": self._fps,
                    "display_fps": self._display_fps,
                    "inference_fps": self._inference_fps,
                    "resolution": self._resolution,
                    "error": self._camera_error,
                },
                "alert": dict(self._alert),
                "stats": dict(self._stats),
                "severity_counts": dict(self._severity_counts),
                "health": {
                    "score": self._health_score,
                    "status": self._health_status,
                    "note": self._health_note,
                },
            }

    # ------------------------------------------------------------------ background workers

    def note_display_frame(self) -> None:
        """Record one display frame for the display-FPS metric.

        Called by the byte-stream proxy for every JPEG frame it forwards. When
        the proxy is not in use (native stream path), display_fps mirrors the
        captured stream rate, which the browser renders directly.
        """
        now = time.time()
        with self._lock:
            self._proxy_used = True
            if self._display_start_time == 0.0:
                self._display_start_time = now
                self._display_frame_count = 0
                return
            self._display_frame_count += 1
            elapsed = now - self._display_start_time
            if elapsed >= 1.0:
                self._display_fps = self._display_frame_count / elapsed
                self._display_start_time = now
                self._display_frame_count = 0

    @staticmethod
    def _severity_for_class(class_name: str) -> str:
        name = (class_name or "").lower()
        if "small" in name:
            return "LOW"
        if "medium" in name:
            return "MEDIUM"
        if "large" in name:
            return "HIGH"
        if "broken" in name:
            return "CRITICAL"
        return "UNKNOWN"

    @staticmethod
    def _build_detections_meta(results, model_names) -> list:
        detections = []
        if not results or len(results) == 0:
            return detections
        boxes = getattr(results[0], "boxes", None)
        if boxes is None or len(boxes) == 0:
            return detections
        for box in boxes:
            cls_id = int(box.cls[0])
            class_name = model_names[cls_id]
            detections.append({
                "class_name": class_name,
                "confidence": round(float(box.conf[0]), 3),
                "severity": CameraPipeline._severity_for_class(class_name),
                "bbox": [float(v) for v in box.xyxy[0].tolist()],
            })
        return detections

    def _inference_loop(self, camera: CameraManager) -> None:
        """Background worker running OpenVINO YOLO inference asynchronously.

        Implements LATEST-FRAME-WINS: when inference finishes, it skips all
        intermediate camera frames and picks the newest available raw frame.
        NO LOCK is held during inference, alert processing, or disk logging.
        """
        last_processed_time = 0.0
        prev_time = time.time()

        while self._running:
            raw_frame = None
            raw_time = 0.0

            with self._lock:
                if self._latest_raw_frame is not None and self._latest_raw_time > last_processed_time:
                    raw_frame = self._latest_raw_frame.copy()
                    raw_time = self._latest_raw_time

            if raw_frame is None:
                time.sleep(0.005)
                continue

            last_processed_time = raw_time

            try:
                # Run detection + alert + statistics + logger without holding lock
                result = camera.process_frame(raw_frame)
                now = time.time()
                inf_fps = 1.0 / max(now - prev_time, 1e-6)
                prev_time = now

                detections_meta = self._build_detections_meta(
                    result.get("results"), camera.detector.model.names
                )

                with self._lock:
                    self._inference_fps = inf_fps
                    self._latest_detection = {
                        "detections": detections_meta,
                        "timestamp": now,
                    }

                    alert = result["alert"]
                    stats = result["stats"]
                    self._alert = alert
                    self._stats = stats

                    sev = alert.get("severity", "SAFE")
                    self._severity_counts[sev] = self._severity_counts.get(sev, 0) + 1
                    self._update_health(stats.get("total", 0))

                    if alert["severity"] == "CRITICAL" and self._estop_armed:
                        self._estop_armed = False
                        self._trigger_estop()
                    elif alert["severity"] != "CRITICAL":
                        self._estop_armed = True

            except Exception:
                pass

            time.sleep(0.002)

    def _camera_loop(self) -> None:
        with self._lock:
            mode = self._camera_mode

        camera = None
        while self._running:
            if camera is None:
                try:
                    camera = CameraManager(mode=mode)
                    camera.start()
                except Exception as exc:
                    with self._lock:
                        self._camera_error = f"Cannot open camera: {exc}"
                    time.sleep(2.0)
                    continue

                # Start asynchronous inference worker thread
                self._inference_thread = threading.Thread(
                    target=self._inference_loop,
                    args=(camera,),
                    daemon=True,
                    name="CameraInferenceWorker",
                )
                self._inference_thread.start()

            frame = camera.read_frame()
            if frame is None:
                if not camera.is_connected():
                    with self._lock:
                        self._camera_error = camera.error() or "ESP32-CAM offline"
                time.sleep(0.02)
                continue

            now = time.time()
            frame_id = camera.read_frame_id()
            with self._lock:
                if self._latest_raw_id == frame_id:
                    continue
                self._latest_raw_id = frame_id
                self._latest_raw_frame = frame
                self._latest_raw_time = now
                self._camera_error = None
                height, width = frame.shape[:2]
                self._resolution = f"{width} × {height}"
                self._fps = 1.0 / max(now - self._last_frame_time, 1e-6)
                self._last_frame_time = now
                # Native (direct-to-browser) display path: the browser renders
                # the same ESP32-CAM stream we capture, so its display rate is
                # the captured stream rate. The proxy overwrites this when used.
                if not self._proxy_used:
                    self._display_fps = self._fps

            time.sleep(0.002)

    def _update_health(self, total: int) -> None:
        """Score track health from cumulative detection count."""
        if total == 0:
            self._health_score = 100
            self._health_status = "EXCELLENT"
            self._health_note = "Track in good condition"
        elif total < 5:
            self._health_score = 80
            self._health_status = "GOOD"
            self._health_note = "Minor degradation detected"
        elif total < 15:
            self._health_score = 60
            self._health_status = "WARNING"
            self._health_note = "Moderate degradation trend"
        else:
            self._health_score = 30
            self._health_status = "CRITICAL"
            self._health_note = "Severe degradation — inspection required"

    def _trigger_estop(self) -> None:
        """Fire the ESP32 emergency stop if a controller is attached."""
        if self._esp is not None:
            self._esp.submit(self._esp.emergency_stop, key="estop")


# --------------------------------------------------------------------------
# Singleton accessor (replaces AppController.get_controller)
# --------------------------------------------------------------------------

_pipeline_instance = None
_pipeline_lock = threading.Lock()


def get_pipeline(esp32_controller=None) -> CameraPipeline:
    """Return the single shared CameraPipeline for the process.

    If a controller is supplied and the singleton already exists, the
    controller is attached to the existing instance (see set_esp32), so a
    startup task can wire hardware even after routes created the pipeline.
    """
    global _pipeline_instance
    with _pipeline_lock:
        if _pipeline_instance is None:
            _pipeline_instance = CameraPipeline(esp32_controller=esp32_controller)
        elif esp32_controller is not None:
            _pipeline_instance.set_esp32(esp32_controller)
    return _pipeline_instance


def get_existing_pipeline():
    """Return the shared pipeline only if it has already been created."""
    with _pipeline_lock:
        return _pipeline_instance
