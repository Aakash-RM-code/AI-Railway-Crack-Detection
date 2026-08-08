"""
CrackDetector — YOLO inference wrapper around models/best.pt.

Runs the canonical PyTorch model (models/best.pt) through the OpenVINO IR export
(models/best_openvino_model/) when INFERENCE_BACKEND=openvino (default), which is
~1.5-1.6x faster at identical quality. Falls back to the PyTorch model
automatically if the OpenVINO export cannot be loaded. Set
INFERENCE_BACKEND=torch to force the PyTorch backend.

The confidence threshold and input size come from the single source of truth
(config.py) instead of being hardcoded or left to Ultralytics defaults, so all
detection code agrees on one value.
"""

import logging

from ultralytics import YOLO

import config

logger = logging.getLogger(__name__)


class CrackDetector:
    """Thin wrapper around a YOLO model used for rail crack detection."""

    def __init__(self, model_path: str | None = None):
        model_path = model_path or config.MODEL_PATH
        self.backend = getattr(config, "INFERENCE_BACKEND", "torch")
        if self.backend == "openvino":
            if not self._try_load_openvino():
                # Fallback: best.pt / PyTorch keeps the detector usable even
                # if the OpenVINO runtime or export is unavailable.
                logger.warning("OpenVINO model load failed (%s); falling back to PyTorch %s",
                               config.OPENVINO_MODEL_PATH, model_path)
                self.backend = "torch"
                self.model = YOLO(model_path)
        else:
            self.model = YOLO(model_path)

        self.imgsz = getattr(config, "INFERENCE_IMGSZ", 640)
        self.conf = getattr(config, "CONFIDENCE_THRESHOLD", 0.70)
        self.names = self.model.names

    def _try_load_openvino(self) -> bool:
        try:
            import openvino  # noqa: F401  (verify runtime is installed)
            self.model = YOLO(config.OPENVINO_MODEL_PATH, task="detect")
            return True
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("OpenVINO load failed: %r", exc)
            return False

    def detect(self, frame):
        """Run detection on a BGR frame and return the Ultralytics results list.

        imgsz / confidence are passed explicitly (config-derived), never relying
        on Ultralytics defaults.
        """
        return self.model(
            frame,
            conf=self.conf,
            imgsz=self.imgsz,
            verbose=False,
        )

    def warmup(self, size: int = 640, iterations: int = 1):
        """Absorb one-time load/compile latency (OpenVINO) before live frames.

        Runs ``iterations`` empty-frame inferences so the first real camera
        frame is not penalised by compilation. Uses the same imgsz/conf as
        normal inference.
        """
        import numpy as np

        dummy = np.zeros((size, size, 3), dtype=np.uint8)
        for _ in range(iterations):
            self.detect(dummy)
        logger.info("CrackDetector warmup complete (backend=%s, imgsz=%s, conf=%s)",
                    self.backend, self.imgsz, self.conf)