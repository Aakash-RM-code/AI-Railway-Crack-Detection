"""
CrackDetector — YOLO inference wrapper around models/best.pt.

Runs the canonical PyTorch model (models/best.pt) through an OpenVINO IR export
when INFERENCE_BACKEND=openvino (default). Two OpenVINO precisions are
supported, selected by OPENVINO_PRECISION:

  * "fp32" (default) -> models/best_openvino_model/     (verified production export)
  * "int8"           -> models/best_int8_openvino_model/  (experimental NNCF PTQ)

The FP32 export remains the default; INT8 is opt-in until it passes validation.
If the requested precision export is missing or fails to load, CrackDetector
falls back to the other OpenVINO precision, then to the PyTorch model. Set
INFERENCE_BACKEND=torch to force the PyTorch backend.

The confidence threshold and input size come from the single source of truth
(config.py) instead of being hardcoded or left to Ultralytics defaults, so all
detection code agrees on one value.
"""

import logging

from ultralytics import YOLO

import config

logger = logging.getLogger(__name__)

# Requested -> fallback chain for OpenVINO precisions. The first entry is the
# requested precision; the rest are tried in order if it is unavailable.
_PRECISION_CHAIN = {
    "fp32": ("fp32", "int8"),
    "int8": ("int8", "fp32"),
}


class CrackDetector:
    """Thin wrapper around a YOLO model used for rail crack detection."""

    def __init__(self, model_path: str | None = None):
        model_path = model_path or config.MODEL_PATH
        self.backend = getattr(config, "INFERENCE_BACKEND", "torch")
        self.precision = None
        if self.backend == "openvino":
            self.precision = getattr(config, "OPENVINO_PRECISION", "fp32").lower()
            if not self._try_load_openvino(self.precision):
                # Fallback: best.pt / PyTorch keeps the detector usable even
                # if the OpenVINO runtime or export is unavailable.
                logger.warning("OpenVINO model load failed; falling back to PyTorch %s",
                               model_path)
                self.backend = "torch"
                self.precision = None
                self.model = YOLO(model_path)
        else:
            self.model = YOLO(model_path)

        self.imgsz = getattr(config, "INFERENCE_IMGSZ", 640)
        self.conf = getattr(config, "CONFIDENCE_THRESHOLD", 0.70)
        self.names = self.model.names
        logger.info(
            "OpenVINO model: %s | Precision: %s | Backend: %s | Input size: %s | Confidence: %s",
            self._openvino_path(self.precision) if self.backend == "openvino" else model_path,
            self.precision if self.precision else "n/a",
            self.backend,
            self.imgsz,
            self.conf,
        )

    def _openvino_path(self, precision: str) -> str:
        if precision == "int8":
            return config.OPENVINO_INT8_MODEL_PATH
        return config.OPENVINO_MODEL_PATH

    def _try_load_openvino(self, requested: str) -> bool:
        try:
            import openvino  # noqa: F401  (verify runtime is installed)
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("OpenVINO runtime unavailable: %r", exc)
            return False

        for precision in _PRECISION_CHAIN.get(requested, (requested,)):
            path = self._openvino_path(precision)
            try:
                if precision != requested:
                    logger.warning("OpenVINO precision %r unavailable; "
                                   "trying %r export %s", requested, precision, path)
                self.model = YOLO(path, task="detect")
                self.precision = precision
                return True
            except Exception as exc:  # pragma: no cover - fallback path
                logger.warning("OpenVINO %s export load failed (%s): %r",
                               precision, path, exc)
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
        logger.info("CrackDetector warmup complete (backend=%s, precision=%s, "
                    "imgsz=%s, conf=%s)",
                    self.backend, self.precision, self.imgsz, self.conf)