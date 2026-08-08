import base64
import csv
import glob
import os
import threading
import time
from datetime import datetime

import config
from backend.esp32 import ESP32Controller

DETECTIONS_DIR = config.DETECTIONS_DIR
HISTORY_CSV = config.HISTORY_CSV

# ------------------------------------------------------------------ single instance
# Flet web mode creates one session per browser connection. Each session
# previously built its own AppController (and therefore its own camera loop
# and ESP32 polling thread). Those must be shared process-wide: exactly one
# controller, one camera loop, and one polling thread regardless of how many
# browser tabs are open.

_controller_singleton = None
_controller_singleton_lock = threading.Lock()


def get_controller() -> "AppController":
    """Return the single shared AppController instance for the process."""
    global _controller_singleton
    with _controller_singleton_lock:
        if _controller_singleton is None:
            _controller_singleton = AppController()
    return _controller_singleton


def get_existing_controller():
    """Return the shared controller only if it has already been created."""
    with _controller_singleton_lock:
        return _controller_singleton


class AppController:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._started_at = datetime.now()
        self._running = False
        self._camera_error: str | None = None
        self._camera_mode = getattr(config, "CAMERA_MODE", "usb")
        self._camera_thread = None

        self._esp = ESP32Controller()

        self._frame_base64 = ""
        self._fps = 0.0
        self._resolution = "--"
        self._alert = {
            "detected": False,
            "severity": "SAFE",
            "class_name": None,
            "confidence": 0.0,
            "message": "Track is Safe",
        }
        self._stats = {"total": 0, "small": 0, "medium": 0, "large": 0, "broken": 0}
        self._severity_counts = {"SAFE": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        self._health_score = 100
        self._health_status = "EXCELLENT"
        self._health_note = "Track in good condition"
        self._estop_armed = True
        self._esp_polling_started = False

    # ------------------------------------------------------------------ lifecycle
    def start(self) -> bool:
        with self._lock:
            if self._running:
                return True
            self._running = True
            self._camera_error = None
            self._camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self._camera_thread.start()
        self._ensure_esp_polling()
        return True

    def stop(self) -> None:
        with self._lock:
            self._running = False

    def close(self) -> None:
        """Stop the camera loop and the single ESP32 polling thread."""
        self.stop()
        self._join_camera_thread()
        self._esp.stop_polling()
        self._esp.close()

    def _join_camera_thread(self, timeout: float = 5.0) -> None:
        thread = self._camera_thread
        if thread and thread.is_alive():
            thread.join(timeout=timeout)
        self._camera_thread = None

    # ------------------------------------------------------------------ camera source switching

    def set_camera_source(self, mode: str, force: bool = False) -> bool:
        """Switch the active camera source without restarting the app.

        Stop -> release -> init new source -> auto-continue if the pipeline
        was running. `force=True` re-initializes the current source (used by
        the ESP32-CAM Reconnect button).
        """
        mode = (mode or "").strip().lower()
        from backend.camera_manager import CameraManager

        if mode not in CameraManager.SOURCES:
            return False
        with self._lock:
            if mode == self._camera_mode and not force and self._running:
                return True
            was_running = self._running
            self._running = False
        self._join_camera_thread()
        with self._lock:
            self._camera_mode = mode
            self._camera_error = None
        if was_running:
            self.start()
        return True

    def reconnect_camera(self) -> bool:
        with self._lock:
            mode = self._camera_mode
        return self.set_camera_source(mode, force=True)

    def set_demo_video_path(self, path: str) -> bool:
        path = (path or "").strip()
        if not path or not os.path.isfile(path):
            return False
        config.DEFAULT_VIDEO_PATH = path
        return True

    def get_camera_source(self) -> str:
        with self._lock:
            return self._camera_mode

    def get_camera_info(self) -> dict:
        with self._lock:
            return {
                "mode": self._camera_mode,
                "running": self._running,
                "fps": self._fps,
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

    # ------------------------------------------------------------------ ESP32

    def _ensure_esp_polling(self) -> None:
        """Start the single ESP32 polling thread exactly once."""
        if not self._esp_polling_started:
            self._esp_polling_started = True
            self._esp.start_polling(interval=config.POLLING_INTERVAL)

    def connect(self) -> bool:
        """Non-blocking connect: starts the single ESP32 polling thread.
        The polling loop updates connection state in the background."""
        self._ensure_esp_polling()
        return True

    def get_esp_status(self) -> dict:
        with self._lock:
            return {
                "online": self._esp.is_online(),
                "ip": self._esp.base_url,
                "last_error": self._esp.last_error(),
                "last_response_time": self._esp.get_last_communication(),
            }

    def esp_forward(self) -> None:
        self._esp.submit(self._esp.forward)

    def esp_backward(self) -> None:
        self._esp.submit(self._esp.backward)

    def esp_stop(self) -> None:
        self._esp.submit(self._esp.stop)

    def esp_set_speed(self, speed: int) -> None:
        self._esp.submit(self._esp.set_speed, speed, key="speed", debounce=0.2)

    def esp_emergency_stop(self) -> None:
        self._esp.submit(self._esp.emergency_stop, key="estop")

    def esp_send_sms(self, phone: str, message: str) -> bool:
        self._esp.submit(self._esp.send_sms, phone, message)
        return True

    def esp_send_test_sms(self) -> bool:
        self._esp.submit(self._esp.send_test_sms)
        return True

    def get_gps(self) -> str | None:
        return self._esp.get_cached_gps()

    # ------------------------------------------------------------------ detection state

    def get_frame_base64(self) -> str:
        with self._lock:
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

    def get_history(self, limit: int = 10) -> list:
        rows = []
        try:
            with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        rows.append(
                            {
                                "time": row.get("Timestamp", ""),
                                "crack_type": row.get("Class", ""),
                                "confidence": round(float(row.get("Confidence", 0)), 2),
                                "image": row.get("Image", ""),
                            }
                        )
                    except (TypeError, ValueError):
                        continue
        except OSError:
            return []
        return rows[-limit:]

    def get_latest_snapshot(self) -> str:
        try:
            files = glob.glob(os.path.join(DETECTIONS_DIR, "*.jpg"))
            if not files:
                return ""
            latest = max(files, key=os.path.getmtime)
            with open(latest, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")
        except OSError:
            return ""

    # ------------------------------------------------------------------ camera pipeline

    def _camera_loop(self) -> None:
        from backend.camera_manager import CameraManager

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

        prev_time = time.time()
        last_frame_time = time.time()
        try:
            while self._running:
                frame = camera.read_frame()
                if frame is None:
                    if time.time() - last_frame_time > 3.0:
                        with self._lock:
                            self._camera_error = camera.error() or "No frames from camera"
                        break
                    time.sleep(0.01)
                    continue

                last_frame_time = time.time()
                now = time.time()
                fps = 1.0 / max(now - prev_time, 1e-6)
                prev_time = now

                result = camera.process_frame(frame)
                annotated = result["frame"]
                alert = result["alert"]
                stats = result["stats"]

                ok, buf = cv2_imencode(annotated)
                if ok:
                    with self._lock:
                        self._frame_base64 = base64.b64encode(buf).decode("ascii")
                        self._fps = fps
                        height, width = annotated.shape[:2]
                        self._resolution = f"{width} × {height}"
                        self._alert = alert
                        self._stats = stats

                        with self._lock:
                            sev = alert.get("severity", "SAFE")
                            self._severity_counts[sev] = self._severity_counts.get(sev, 0) + 1
                            total = stats.get("total", 0)
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

                if alert["severity"] == "CRITICAL" and self._estop_armed:
                    self._estop_armed = False
                    self.esp_emergency_stop()
                elif alert["severity"] != "CRITICAL":
                    self._estop_armed = True
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


def cv2_imencode(frame):
    import cv2

    return cv2.imencode(".jpg", frame)
