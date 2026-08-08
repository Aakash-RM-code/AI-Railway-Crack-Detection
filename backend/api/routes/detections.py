"""Detections, alerts, track health, and statistics routes."""

import os
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import FileResponse

import config
from backend.api import schemas
from backend.services.camera import get_pipeline
from backend.storage.repository import DetectionRepository, map_crack_class, map_severity

router = APIRouter(tags=["Detections & Analytics"])

_repo = DetectionRepository()


@router.get("/alerts/latest", response_model=schemas.Alert)
def get_latest_alert():
    """Returns the most recent alert evaluated by the system."""
    pipeline = get_pipeline()
    alert_dict = pipeline.get_alert()

    class_name = alert_dict.get("class_name")
    crack_cls = map_crack_class(class_name) if class_name else None
    sev_str = alert_dict.get("severity", "SAFE")
    try:
        sev = schemas.Severity(sev_str)
    except ValueError:
        sev = schemas.Severity.SAFE

    return schemas.Alert(
        id=f"alert-{int(datetime.now().timestamp())}",
        severity=sev,
        crack_class=crack_cls,
        confidence=round(alert_dict.get("confidence", 0.0), 2),
        message=alert_dict.get("message", "Track is Safe"),
        timestamp=datetime.now().isoformat(),
    )


@router.get("/track-health", response_model=schemas.TrackHealth)
def get_track_health():
    """Returns overall track health metrics."""
    pipeline = get_pipeline()
    health_dict = pipeline.get_health()

    status_str = health_dict.get("status", "EXCELLENT").lower()
    try:
        health_status = schemas.HealthStatus(status_str)
    except ValueError:
        health_status = schemas.HealthStatus.EXCELLENT

    stats = pipeline.get_stats()
    inspected_meters = round(stats.get("total", 0) * 1.5 + 250.0, 1)

    return schemas.TrackHealth(
        overall=health_dict.get("score", 100),
        status=health_status,
        inspected_meters=inspected_meters,
        updated_at=datetime.now().isoformat(),
    )


@router.get("/statistics", response_model=schemas.Statistics)
def get_statistics():
    """Returns aggregate detection counts across history."""
    return _repo.get_statistics()


@router.get("/statistics/distribution", response_model=List[schemas.DetectionDistributionSlice])
def get_detection_distribution():
    """Returns detection breakdown slices by crack class."""
    return _repo.get_detection_distribution()


@router.get("/statistics/trend", response_model=List[schemas.SeverityTrendPoint])
def get_severity_trend():
    """Returns historical severity trend time-series data points."""
    return _repo.get_severity_trend()


@router.get("/detections", response_model=schemas.Paginated[schemas.Detection])
def get_detections(
    search: Optional[str] = Query(default=None),
    severity: Optional[str] = Query(default="ALL"),
    page: int = Query(default=1, ge=1),
    pageSize: int = Query(default=10, ge=1, le=100),
):
    """Returns paginated, searchable, and filtered detection records."""
    items, total = _repo.get_detections(
        search=search,
        severity=severity,
        page=page,
        page_size=pageSize,
    )
    return schemas.Paginated[schemas.Detection](
        items=items,
        total=total,
        page=page,
        page_size=pageSize,
    )


@router.get("/detections/latest-snapshot", response_model=schemas.Snapshot)
def get_latest_snapshot():
    """Returns metadata for the most recently captured snapshot."""
    snapshot = _repo.get_latest_snapshot()
    if snapshot is None:
        return schemas.Snapshot(
            id="snap-none",
            image_url=None,
            timestamp=datetime.now().isoformat(),
            severity=schemas.Severity.SAFE,
            crack_class=None,
        )
    return snapshot


@router.get("/detections/snapshot-image/{filename}")
def get_snapshot_image(filename: str):
    """Serves static image files from the detections directory."""
    file_path = os.path.join(config.DETECTIONS_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Snapshot image not found")
    return FileResponse(file_path, media_type="image/jpeg")


# Legacy history endpoint
@router.get("/history", response_model=List[schemas.HistoryRow])
def legacy_history(limit: int = 10):
    from backend.services.history_manager import HistoryManager
    return HistoryManager().read(limit=limit)
