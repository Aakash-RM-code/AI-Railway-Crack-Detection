"""
Generate an INT8 OpenVINO IR of the railway crack detection YOLO model using
OpenVINO NNCF Post-Training Quantization (PTQ).

Calibration uses real frames captured by the system (detections/*.jpg) — the
same input distribution the detector runs on — so no labelled dataset is
required for PTQ. The input preprocessing mirrors Ultralytics/OpenVINO
inference exactly (letterbox to 640, BGR->RGB, CHW, /255, fp32, batch=1).

Output is written to models/best_int8_model/ (best.xml + best.bin), leaving
the existing FP32 OpenVINO export (models/best_openvino_model/) untouched.

Usage (from project root, using the deployment Python):

    & "C:\\Users\\Aakash\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" scripts/quantize_int8.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("quantize_int8")

IMGSZ = int(getattr(config, "INFERENCE_IMGSZ", 640))
SRC_IR_DIR = Path(config.OPENVINO_MODEL_PATH)
OUT_DIR = config.MODELS_DIR / "best_int8_openvino_model"
CALIB_GLOB = sorted(Path(config.DETECTIONS_DIR).glob("*.jpg"))
BATCH = 1


def _read_names(metadata_path: Path) -> dict:
    """Read the class-name mapping from an Ultralytics metadata.yaml."""
    if not metadata_path.exists():
        return {}
    import yaml

    with open(metadata_path, "r", encoding="utf-8") as fh:
        meta = yaml.safe_load(fh) or {}
    return {int(k): v for k, v in (meta.get("names") or {}).items()}


def letterbox(im, new_shape=IMGSZ, color=(114, 114, 114)):
    """Resize keeping aspect ratio, pad to new_shape — matches Ultralytics."""
    shape = im.shape[:2]
    r = min(new_shape / shape[0], new_shape / shape[1])
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape - new_unpad[0], new_shape - new_unpad[1]
    dw, dh = dw // 2, dh // 2
    if shape[::-1] != new_unpad:
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = dh, dh + (new_shape - new_unpad[1]) - dh * 2
    left, right = dw, dw + (new_shape - new_unpad[0]) - dw * 2
    return cv2.copyMakeBorder(im, top, bottom, left, right,
                              cv2.BORDER_CONSTANT, value=color)


def preprocess(img_bgr):
    """BGR HWC frame -> model input (1,3,640,640) fp32 in [0,1], RGB."""
    im = letterbox(img_bgr)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im = im.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
    return im


def main() -> int:
    import openvino as ov
    import nncf

    if not CALIB_GLOB:
        logger.error("No calibration images found in %s", config.DETECTIONS_DIR)
        return 2
    if not (SRC_IR_DIR / "best.xml").exists():
        logger.error("Source OpenVINO IR not found in %s", SRC_IR_DIR)
        return 2

    core = ov.Core()
    fp32_model = core.read_model(str(SRC_IR_DIR / "best.xml"))
    fp32_model_names = _read_names(SRC_IR_DIR / "metadata.yaml")
    logger.info("Source model: %s (%s)",
                fp32_model.input(0).get_partial_shape(),
                fp32_model.input(0).get_element_type())
    logger.info("Calibration images: %d from %s", len(CALIB_GLOB), config.DETECTIONS_DIR)

    def loader():
        for path in CALIB_GLOB:
            img = cv2.imread(str(path))
            if img is None:
                continue
            yield preprocess(img)

    def transform_fn(batch):
        return {"x.1": np.ascontiguousarray(batch)}

    calibration_dataset = nncf.Dataset(loader(), transform_func=transform_fn)

    logger.info("Running NNCF PTQ (INT8)...")
    quantized_model = nncf.quantize(fp32_model, calibration_dataset)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ov.save_model(quantized_model, str(OUT_DIR / "best.xml"))
    names = "".join(f"  {i}: {n}\n" for i, n in sorted(fp32_model_names.items()))
    (OUT_DIR / "metadata.yaml").write_text(
        "description: INT8 (NNCF PTQ) export of the crack detection model\n"
        "author: opencode-INT8\n"
        "version: 8.4.90\n"
        "license: AGPL-3.0 License (https://ultralytics.com/license)\n"
        "stride: 32\n"
        "task: detect\n"
        "head: Detect\n"
        "batch: 1\n"
        "imgsz:\n"
        "- 640\n"
        "- 640\n"
        f"names:\n{names}"
        "int8: true\n"
        "precision: int8\n"
        "source: best_openvino_model/best.xml (FP32)\n"
        "quantization: nncf_ptq\n"
        "calibration: detections/*.jpg\n",
        encoding="utf-8",
    )
    logger.info("INT8 model saved to %s", OUT_DIR)
    logger.info("INT8 output precision: %s",
                quantized_model.output(0).get_element_type())
    return 0


if __name__ == "__main__":
    sys.exit(main())
