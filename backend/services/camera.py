"""Camera service — source management, acquisition, detection pipeline, and
the background processing loop that used to live in the Flet AppController.

Split into two collaborators:

* ``CameraManager`` — owns the active source (usb | esp32cam | demo), runs an
  acquisition thread, and drives the full detection pipeline per frame.
* ``CameraPipeline`` — the long-running service. Holds the shared runtime state
  (latest frame, alert, stats, health, severity counts), runs the capture loop
  on a background thread, and triggers the ESP32 emergency stop on CRITICAL
  detections. A process-wide instance is available via ``get_pipeline()``.
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
from backend.utils.imaging import jpeg_base64

SEVERITY_LEVELS = ("SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL")


# --------------------------------------------------------------------------
# CameraManager — source management + detection pipeline
# --------------------------------------------------------------------------


class CameraManager:

    SOURCES = ("usb", "esp32cam", "demo")

    def __init__(self, mode: str | None = None):
        self.detector = CrackDetector(config.MODEL_PATH)
        # Absorb OpenVINO first-inference compile latency before live frames.
        self.detector.warmup()
        self.alert_manager = AlertManager()
        self.statistics = StatisticsManager()
        self.logger = DetectionLogger()

        self._lock = threading.RLock()
        self.mode = (mode or getattr(config, "CAMERA_MODE", "usb")).strip().lower()
        if self.mode not in self.SOURCES:
            raise ValueError(f"Unknown camera source: {self.mode}")

        self._cap = None
        self._snapshot_url = ""
        self._running = False
        self._acq_thread = None
        self._latest_frame = None
        self._error = None
        self._connected = False

        self._open_source()

    # ------------------------------------------------------------------ source management

    def _open_source(self) -> None:
        self._close_source()
        self._connected = False
        self._error = None

        if self.mode == "usb":
            index = int(getattr(config, "CAMERA_INDEX", 0))
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(index)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, getattr(config, "CAMERA_WIDTH", 640))
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, getattr(config, "CAMERA_HEIGHT", 480))
            if not cap.isOpened():
                raise RuntimeError(f"Could not open USB camera (index {index})")
            self._cap = cap

        elif self.mode == "esp32cam":
            stream_url = getattr(config, "ESP32CAM_STREAM_URL", "")
            cap = cv2.VideoCapture(stream_url)
            if cap.isOpened():
                self._cap = cap
            else:
                cap.release()
                self._snapshot_url = getattr(config, "ESP32CAM_SNAPSHOT_URL", "")
                if not self._snapshot_url:
                    raise RuntimeError("ESP32-CAM stream/snapshot URL not configured")

        elif self.mode == "demo":
            video_path = getattr(config, "DEFAULT_VIDEO_PATH", "")
            if not video_path:
                raise RuntimeError("DEFAULT_VIDEO_PATH not configured for demo mode")
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise RuntimeError(f"Could not open demo video: {video_path}")
            self._cap = cap

        self._connected = True

    def _close_source(self) -> None:
        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
            self._cap = None

    def set_mode(self, mode: str) -> None:
        mode = (mode or "").strip().lower()
        if mode not in self.SOURCES:
            raise ValueError(f"Unknown camera source: {mode}")
        if mode == self.mode:
            return
        was_running = self.is_running()
        self.stop()
        self.mode = mode
        self._open_source()
        if was_running:
            self.start()

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

    def set_video_path(self, path: str) -> None:
        config.DEFAULT_VIDEO_PATH = path

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
            time.sleep(0.005)

    def _read_once(self):
        if self._cap is not None:
            ret, frame = self._cap.read()
            if not ret:
                if self.mode == "demo":
                    self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self._cap.read()
                if not ret:
                    return None
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
            return frame
        except Exception:
            return None

    def read_frame(self):
        with self._lock:
            return self._latest_frame

    # ------------------------------------------------------------------ processing

    def process_frame(self, frame):
        """Run the full detection pipeline for a frame.

        Returns a dict with the annotated frame, raw results, the generated alert,
        and the updated statistics.
        """
        results = self.detector.detect(frame)
        alert = self.alert_manager.process(results, self.detector.model.names)

        if alert["detected"]:
            self.statistics.update(alert["class_name"])

        annotated = results[0].plot()

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
            "frame": annotated,
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
    - Camera capture + streaming loop runs continuously at ~25-30 FPS.
    - AI inference worker runs on a separate background thread at ~10-13 FPS
      using a latest-frame-wins strategy. Streaming never waits for inference.
    """

    STALE_DETECTION_TTL_SEC = 0.5

    def __init__(self, mode: str | None = None, esp32_controller=None):
        self._lock = threading.RLock()
        self._started_at = datetime.now()
        self._esp = esp32_controller or None
        self._running = False
        self._camera_error: str | None = None
        self._camera_mode = (mode or getattr(config, "CAMERA_MODE", "usb")).strip().lower()
        self._camera_thread = None
        self._inference_thread = None

        self._latest_raw_frame = None
        self._latest_raw_time = 0.0
        self._latest_detection_results = None
        self._frame_jpeg: bytes = b""
        self._frame_base64 = ""
        self._fps = 0.0
        self._inference_fps = 0.0
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
            self._latest_raw_time = 0.0
            self._latest_detection_results = None
            self._frame_jpeg = b""
            self._frame_base64 = ""
        if was_running:
            self.start()
        return True

    def reconnect_camera(self) -> bool:
        with self._lock:
            mode = self._camera_mode
        return self.set_camera_source(mode, force=True)

    def set_demo_video_path(self, path: str) -> bool:
        import os

        path = (path or "").strip()
        if not path or not os.path.isfile(path):
            return False
        config.DEFAULT_VIDEO_PATH = path
        return True

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

    def get_frame_jpeg(self) -> bytes:
        with self._lock:
            return self._frame_jpeg

    def get_frame_base64(self) -> str:
        with self._lock:
            if not self._frame_base64 and self._frame_jpeg:
                import base64
                self._frame_base64 = base64.b64encode(self._frame_jpeg).decode("utf-8")
            return self._frame_base64

    def get_fps(self) -> float:
        with self._lock:
            return self._fps

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

    def get_state(self) -> dict:
        """Full snapshot of the runtime state for the API/websocket layer."""
        with self._lock:
            return {
                "camera": {
                    "mode": self._camera_mode,
                    "running": self._running,
                    "fps": self._fps,
                    "resolution": self._resolution,
                    "error": self._camera_error,
                },
                "frame_base64": self.get_frame_base64(),
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

                with self._lock:
                    self._inference_fps = inf_fps
                    self._latest_detection_results = {
                        "results": result.get("results"),
                        "alert": result.get("alert"),
                        "stats": result.get("stats"),
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
        try:
            camera = CameraManager(mode=mode)
            camera.start()
        except Exception as exc:
            with self._lock:
                self._camera_error = str(exc)
                self._running = False
            return

        # Start asynchronous inference worker thread
        self._inference_thread = threading.Thread(
            target=self._inference_loop,
            args=(camera,),
            daemon=True,
            name="CameraInferenceWorker",
        )
        self._inference_thread.start()

        prev_time = time.time()
        last_frame_time = time.time()
        got_first_frame = False
        try:
            while self._running:
                frame = camera.read_frame()
                if frame is None:
                    timeout = 3.0 if got_first_frame else 10.0
                    if time.time() - last_frame_time > timeout:
                        with self._lock:
                            self._camera_error = camera.error() or "No frames from camera"
                        break
                    time.sleep(0.01)
                    continue

                got_first_frame = True
                last_frame_time = time.time()
                now = time.time()
                fps = 1.0 / max(now - prev_time, 1e-6)
                prev_time = now

                # Store raw frame for inference worker
                with self._lock:
                    self._latest_raw_frame = frame
                    self._latest_raw_time = now

                # Composite newest raw frame with latest valid detection overlay
                display_frame = frame
                det_res = None
                with self._lock:
                    if self._latest_detection_results is not None:
                        if (now - self._latest_detection_results["timestamp"]) <= self.STALE_DETECTION_TTL_SEC:
                            det_res = self._latest_detection_results.get("results")

                if det_res and len(det_res) > 0 and len(det_res[0].boxes) > 0:
                    try:
                        display_frame = det_res[0].plot(img=frame.copy())
                    except Exception:
                        display_frame = frame

                # Encode to JPEG bytes (NO LOCK HELD during JPEG encode)
                ret, jpeg_buf = cv2.imencode(".jpg", display_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    jpeg_bytes = jpeg_buf.tobytes()
                    with self._lock:
                        self._frame_jpeg = jpeg_bytes
                        self._frame_base64 = ""
                        self._fps = fps
                        height, width = display_frame.shape[:2]
                        self._resolution = f"{width} × {height}"

                time.sleep(0.005)

        except Exception as exc:
            with self._lock:
                self._camera_error = str(exc)
        finally:
            with self._lock:
                self._running = False
            if camera is not None:
                try:
                    camera.close()
                except Exception:
                    pass

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
