"""Thin launcher for the Railway Crack Detection backend.

Usage:
    python run_backend.py

Starts the existing FastAPI application (backend.main:app) under uvicorn and
prints a startup banner summarising the active camera, AI, and server settings.
This file is an orchestrator — it contains NO duplicate business logic.
"""

import sys
import config


def _banner() -> None:
    """Print a human-readable startup summary."""
    lines = [
        "",
        "=" * 56,
        "  Railway Crack Detection — Backend Launcher",
        "=" * 56,
        f"  Camera:          ESP32-CAM",
        f"  ESP32-CAM URL:   {config.ESP32CAM_STREAM_URL}",
        f"  Snapshot URL:    {config.ESP32CAM_SNAPSHOT_URL}",
        f"  AI backend:      {config.INFERENCE_BACKEND.upper()}",
        f"  Precision:       {config.OPENVINO_PRECISION.upper()}",
        f"  imgsz:           {config.INFERENCE_IMGSZ}",
        f"  confidence:      {config.CONFIDENCE_THRESHOLD}",
        f"  ESP32 rover:     {'enabled' if config.ESP32_ENABLED else 'disabled'}",
    ]
    if config.ESP32_ENABLED:
        lines.append(f"  Rover URL:       {config.ESP32_BASE_URL}")
    lines += [
        f"  FastAPI:         http://127.0.0.1:8080",
        "=" * 56,
        "",
    ]
    print("\n".join(lines), flush=True)


def main() -> None:
    _banner()

    try:
        import uvicorn
    except ImportError:
        print("ERROR: uvicorn is not installed. Run: pip install uvicorn", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )


if __name__ == "__main__":
    main()
