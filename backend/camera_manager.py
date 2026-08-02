import threading
import time
from urllib.request import urlopen

import cv2
import numpy as np

import config

from backend.detector import CrackDetector
from backend.alert_manager import AlertManager
from backend.statistics_manager import StatisticsManager
from backend.logger import DetectionLogger


class CameraManager:

    SOURCES = ("usb", "esp32cam", "demo")

    def __init__(self, mode: str | None = None):
        self.detector = CrackDetector(config.MODEL_PATH)
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

    # ------------------------------------------------------------------ processing (unchanged pipeline)

    def process_frame(self, frame):

    # Run YOLO Detection
        results = self.detector.detect(frame)

    # Generate Alert
        alert = self.alert_manager.process(
        results,
        self.detector.model.names
    )

    # Update Statistics
        if alert["detected"]:
            self.statistics.update(alert["class_name"])

    # Save Detections
        for box in results[0].boxes:

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            self.logger.save_detection(
            frame,
            self.detector.model.names[cls],
            conf
        )

    # Draw Bounding Boxes
        annotated = results[0].plot()

    # Return everything
        logged = False

        if len(results[0].boxes) > 0:

            best = max(results[0].boxes, key=lambda b: float(b.conf[0]))

            cls = int(best.cls[0])
            conf = float(best.conf[0])

            logged = self.logger.save_detection(
        frame,
        self.detector.model.names[cls],
        conf
    )

        return {
    "frame": annotated,
    "alert": alert,
    "stats": self.statistics.get_stats(),
    "logged": logged
}

    def close(self):
        self.stop()
        self._close_source()
