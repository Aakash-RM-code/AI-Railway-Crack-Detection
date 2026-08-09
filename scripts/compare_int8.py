"""
Compare FP32 vs INT8 OpenVINO detection output on the same calibration frames.

Reports per-image class-set agreement, per-class confidence drift, and the
number of boxes each model fires at the configured confidence threshold.

Usage (from project root, deployment Python):

    & "C:\\Users\\Aakash\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" scripts/compare_int8.py
"""

from __future__ import annotations

import glob
import logging
import os
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("compare_int8")

IMGSZ = int(config.INFERENCE_IMGSZ)
CONF = float(config.CONFIDENCE_THRESHOLD)
FP32 = config.OPENVINO_MODEL_PATH
INT8 = str(config.MODELS_DIR / "best_int8_openvino_model")
FILES = sorted(glob.glob(os.path.join(config.DETECTIONS_DIR, "*.jpg")))


def summarize(results):
    agg = {}
    n = 0
    for r in results:
        if r.boxes is None or len(r.boxes) == 0:
            continue
        cls = r.boxes.cls.cpu().numpy()
        confs = r.boxes.conf.cpu().numpy()
        n += len(cls)
        for i in range(len(cls)):
            c = int(cls[i])
            agg[c] = max(agg.get(c, 0.0), float(confs[i]))
    return agg, n


def main() -> int:
    if not FILES:
        logger.error("No images in %s", config.DETECTIONS_DIR)
        return 2

    fp32 = YOLO(FP32, task="detect")
    int8 = YOLO(INT8, task="detect")
    print(f"FP32 names: {fp32.names}")
    print(f"INT8 names: {int8.names}")

    status = Counter()
    conf_drift = []
    class_counts = {"fp32": Counter(), "int8": Counter()}
    box_counts = {"fp32": 0, "int8": 0}
    box_drift = []

    for path in FILES:
        img = cv2.imread(path)
        if img is None:
            continue
        agg32, n32 = summarize(fp32(img, conf=CONF, imgsz=IMGSZ, verbose=False))
        agg8, n8 = summarize(int8(img, conf=CONF, imgsz=IMGSZ, verbose=False))
        if not agg32 and not agg8:
            status["both_none"] += 1
        elif set(agg32) != set(agg8):
            status["class_set_mismatch"] += 1
        else:
            status["matched"] += 1
            conf_drift.extend(abs(agg32[k] - agg8[k]) for k in agg32)
        class_counts["fp32"].update(agg32)
        class_counts["int8"].update(agg8)
        box_counts["fp32"] += n32
        box_counts["int8"] += n8
        if n32 and n8:
            box_drift.append(abs(n32 - n8))

    print("\n=== FP32 vs INT8 agreement over %d frames ===" % len(FILES))
    print("status counts:", dict(status))
    if conf_drift:
        print("mean confidence drift (matched detections): %.4f" % np.mean(conf_drift))
        print("max confidence drift: %.4f" % np.max(conf_drift))
    print("total boxes fired @ conf=%.2f: FP32=%d INT8=%d" % (CONF, box_counts["fp32"], box_counts["int8"]))
    if box_drift:
        print("mean per-image box-count |delta|: %.3f" % np.mean(box_drift))
    print("\nper-class detection counts (images with at least one box):")
    for c in sorted(set(class_counts["fp32"]) | set(class_counts["int8"])):
        name = fp32.names.get(c, f"class{c}")
        print(f"  {name:16s} FP32={int(class_counts['fp32'][c]):4d}  INT8={int(class_counts['int8'][c]):4d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
