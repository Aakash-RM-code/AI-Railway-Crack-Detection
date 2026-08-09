"""
Benchmark OpenVINO FP32 vs INT8 inference on the same CPU/input.

Conditions: CPU, batch=1, imgsz=640, conf=0.70, same real frames, same
preprocessing. Measures end-to-end YOLO predict() latency (includes ultralytics
pre/post-processing, which is what CrackDetector.detect() uses) plus raw
OpenVINO infer() latency, P50/P95, and CPU utilization.

Usage (from project root, deployment Python):

    & "C:\\Users\\Aakash\\AppData\\Local\\Programs\\Python\\Python311\\python.exe" scripts/benchmark_int8.py
"""

from __future__ import annotations

import glob
import logging
import os
import statistics
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("benchmark_int8")

IMGSZ = int(config.INFERENCE_IMGSZ)
CONF = float(config.CONFIDENCE_THRESHOLD)
FP32 = config.OPENVINO_MODEL_PATH
INT8 = str(config.MODELS_DIR / "best_int8_openvino_model")
WARMUP = 10
RUNS = 100


def load_frames():
    files = sorted(glob.glob(os.path.join(config.DETECTIONS_DIR, "*.jpg")))[:32]
    if not files:
        logger.error("No frames available in %s", config.DETECTIONS_DIR)
        sys.exit(2)
    return [cv2.imread(f) for f in files if cv2.imread(f) is not None]


def bench_predict(model, frames, runs=RUNS):
    lat = []
    for _ in range(WARMUP):
        model(frames[0], conf=CONF, imgsz=IMGSZ, verbose=False)
    t0 = time.perf_counter()
    for _ in range(runs):
        frame = frames[_ % len(frames)]
        t = time.perf_counter()
        model(frame, conf=CONF, imgsz=IMGSZ, verbose=False)
        lat.append((time.perf_counter() - t) * 1000.0)
    wall = time.perf_counter() - t0
    lat.sort()
    return {
        "avg_ms": statistics.mean(lat),
        "p50_ms": lat[int(len(lat) * 0.50)],
        "p95_ms": lat[min(int(len(lat) * 0.95), len(lat) - 1)],
        "end_to_end_fps": runs / wall,
    }


def bench_raw_ov(path, frames, runs=RUNS):
    import openvino as ov

    core = ov.Core()
    model = core.read_model(os.path.join(path, "best.xml"))
    compiled = core.compile_model(model, "CPU")
    req = compiled.create_infer_request()
    input_name = model.input(0).get_any_name()

    def preprocess(img_bgr):
        import cv2 as _cv
        shape = img_bgr.shape[:2]
        r = min(IMGSZ / shape[0], IMGSZ / shape[1])
        nu = (int(round(shape[1] * r)), int(round(shape[0] * r)))
        im = _cv.resize(img_bgr, nu, interpolation=_cv.INTER_LINEAR)
        top = (IMGSZ - nu[1]) // 2
        left = (IMGSZ - nu[0]) // 2
        im = _cv.copyMakeBorder(im, top, IMGSZ - nu[1] - top, left,
                                IMGSZ - nu[0] - left, _cv.BORDER_CONSTANT,
                                value=(114, 114, 114))
        im = _cv.cvtColor(im, _cv.COLOR_BGR2RGB)
        im = im.transpose(2, 0, 1)[None].astype(np.float32) / 255.0
        return np.ascontiguousarray(im)

    blobs = [preprocess(f) for f in frames]
    lat = []
    for _ in range(WARMUP):
        req.infer({input_name: blobs[0]})
    t0 = time.perf_counter()
    for _ in range(runs):
        t = time.perf_counter()
        req.infer({input_name: blobs[_ % len(blobs)]})
        lat.append((time.perf_counter() - t) * 1000.0)
    wall = time.perf_counter() - t0
    lat.sort()
    return {
        "avg_ms": statistics.mean(lat),
        "p50_ms": lat[int(len(lat) * 0.50)],
        "p95_ms": lat[min(int(len(lat) * 0.95), len(lat) - 1)],
        "end_to_end_fps": runs / wall,
    }


def cpu_util(fn):
    import psutil

    p = psutil.Process()
    p.cpu_percent(interval=None)
    fn()
    return p.cpu_percent(interval=0.05)


def main() -> int:
    frames = load_frames()
    print(f"bench: imgsz={IMGSZ}, conf={CONF}, runs={RUNS}, warmup={WARMUP}, frames={len(frames)}, device=CPU")

    print("\n--- ultralytics YOLO predict() (matches CrackDetector.detect) ---")
    fp32 = YOLO(FP32, task="detect")
    r32 = bench_predict(fp32, frames)
    print(f"FP32 OpenVINO: avg={r32['avg_ms']:.1f}ms  p50={r32['p50_ms']:.1f}ms  "
          f"p95={r32['p95_ms']:.1f}ms  {r32['end_to_end_fps']:.1f} FPS")

    int8 = YOLO(INT8, task="detect")
    r8 = bench_predict(int8, frames)
    print(f"INT8 OpenVINO: avg={r8['avg_ms']:.1f}ms  p50={r8['p50_ms']:.1f}ms  "
          f"p95={r8['p95_ms']:.1f}ms  {r8['end_to_end_fps']:.1f} FPS")

    print("\n--- raw OpenVINO infer() (model-only) ---")
    raw32 = bench_raw_ov(FP32, frames)
    raw8 = bench_raw_ov(INT8, frames)
    print(f"FP32 OpenVINO: avg={raw32['avg_ms']:.1f}ms  p50={raw32['p50_ms']:.1f}ms  "
          f"p95={raw32['p95_ms']:.1f}ms  {raw32['end_to_end_fps']:.1f} FPS")
    print(f"INT8 OpenVINO: avg={raw8['avg_ms']:.1f}ms  p50={raw8['p50_ms']:.1f}ms  "
          f"p95={raw8['p95_ms']:.1f}ms  {raw8['end_to_end_fps']:.1f} FPS")

    if raw32["avg_ms"] > 0:
        print("\nimprovement (avg raw infer): %.1f%% faster" % (
            (raw32["avg_ms"] / raw8["avg_ms"] - 1.0) * 100.0))

    print("\nCPU util during single-threaded predict loop (approx, %):")
    print("  FP32: %.1f%%" % cpu_util(lambda: fp32(frames[0], conf=CONF, imgsz=IMGSZ, verbose=False)))
    print("  INT8: %.1f%%" % cpu_util(lambda: int8(frames[0], conf=CONF, imgsz=IMGSZ, verbose=False)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
