"""DetectionRepository — isolates CSV and file storage access behind a repository interface.

This layer is the single source of truth for reading and writing detection records
and snapshot files. Thread-safe execution prevents file access collisions.
"""

import csv
import glob
import os
import threading
import time
from datetime import datetime
from typing import Optional, List, Tuple

import cv2
import config
from backend.api.schemas import (
    Detection,
    CrackClass,
    Severity,
    DetectionStatus,
    Snapshot,
    Statistics,
    DetectionDistributionSlice,
    SeverityTrendPoint,
)

DETECTIONS_DIR = config.DETECTIONS_DIR
HISTORY_CSV = config.HISTORY_CSV
LOGS_DIR = config.LOGS_DIR


def map_crack_class(raw_name: str) -> CrackClass:
    name = (raw_name or "").lower().strip()
    if "small" in name:
        return CrackClass.SMALL_CRACK
    elif "medium" in name:
        return CrackClass.MEDIUM_CRACK
    elif "large" in name:
        return CrackClass.LARGE_CRACK
    elif "broken" in name:
        return CrackClass.BROKEN_CHAIN
    return CrackClass.SMALL_CRACK


def map_severity(crack_cls: CrackClass) -> Severity:
    if crack_cls == CrackClass.SMALL_CRACK:
        return Severity.LOW
    elif crack_cls == CrackClass.MEDIUM_CRACK:
        return Severity.MEDIUM
    elif crack_cls == CrackClass.LARGE_CRACK:
        return Severity.HIGH
    elif crack_cls == CrackClass.BROKEN_CHAIN:
        return Severity.CRITICAL
    return Severity.SAFE


class DetectionRepository:
    """Single source of truth repository for detection records, snapshots, and metrics."""

    _instance = None
    _class_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._class_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance

    def __init__(self, csv_path: str = HISTORY_CSV, detections_dir: str = DETECTIONS_DIR, cooldown: float = 3.0):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.csv_path = csv_path
        self.detections_dir = detections_dir
        self.cooldown = cooldown
        self._last_saved_time = 0.0
        self._lock = threading.RLock()
        self._ensure_storage()
        self._initialized = True

    def _ensure_storage(self) -> None:
        with self._lock:
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            os.makedirs(self.detections_dir, exist_ok=True)

            if not os.path.exists(self.csv_path):
                with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Timestamp",
                        "Class",
                        "Confidence",
                        "Image",
                        "Latitude",
                        "Longitude",
                    ])

    def save_detection(
        self,
        frame,
        class_name: str,
        confidence: float,
        latitude: float = 0.0,
        longitude: float = 0.0,
    ) -> bool:
        """Thread-safe method to save detection frame JPEG and append metadata to CSV."""
        now = time.time()
        with self._lock:
            if now - self._last_saved_time < self.cooldown:
                return False
            self._last_saved_time = now

            timestamp = datetime.now()
            image_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"
            image_path = os.path.join(self.detections_dir, image_name)

            # Save snapshot frame to disk
            if frame is not None:
                cv2.imwrite(image_path, frame)

            image_relative_path = os.path.join("detections", image_name)

            # Append to CSV
            with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    class_name,
                    round(confidence, 2),
                    image_relative_path,
                    round(latitude, 6),
                    round(longitude, 6),
                ])
            return True

    def get_all_records(self) -> List[dict]:
        """Read raw dictionary records from the CSV storage."""
        with self._lock:
            if not os.path.exists(self.csv_path):
                return []
            records = []
            try:
                with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(row)
            except OSError:
                return []
            return records

    def get_detections(
        self,
        search: Optional[str] = None,
        severity: Optional[str] = "ALL",
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[Detection], int]:
        """Return a paginated list of Detection domain models with filtering."""
        with self._lock:
            raw_records = self.get_all_records()
            detections: List[Detection] = []

            for idx, row in enumerate(reversed(raw_records)):
                raw_class = row.get("Class", "small_crack")
                crack_cls = map_crack_class(raw_class)
                sev = map_severity(crack_cls)

                if severity and severity.upper() != "ALL":
                    if sev.value.upper() != severity.upper():
                        continue

                if search:
                    query = search.lower()
                    ts_str = row.get("Timestamp", "").lower()
                    cls_str = crack_cls.value.lower()
                    if query not in ts_str and query not in cls_str:
                        continue

                conf = 0.0
                try:
                    conf = float(row.get("Confidence", 0.0))
                except (ValueError, TypeError):
                    pass

                lat = 0.0
                lon = 0.0
                try:
                    lat = float(row.get("Latitude", 0.0))
                    lon = float(row.get("Longitude", 0.0))
                except (ValueError, TypeError):
                    pass

                item_id = f"det-{len(raw_records) - idx}"
                detections.append(
                    Detection(
                        id=item_id,
                        timestamp=row.get("Timestamp", datetime.now().isoformat()),
                        crack_class=crack_cls,
                        confidence=conf,
                        severity=sev,
                        latitude=lat,
                        longitude=lon,
                        status=DetectionStatus.NEW,
                    )
                )

            total = len(detections)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_items = detections[start_idx:end_idx]

            return paginated_items, total

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Retrieve metadata for the most recently saved snapshot image."""
        with self._lock:
            try:
                files = glob.glob(os.path.join(self.detections_dir, "*.jpg"))
                if not files:
                    return None
                latest_file = max(files, key=os.path.getmtime)
                rel_name = os.path.basename(latest_file)
                mtime = os.path.getmtime(latest_file)
                ts_str = datetime.fromtimestamp(mtime).isoformat()

                records = self.get_all_records()
                last_class = CrackClass.SMALL_CRACK
                if records:
                    last_class = map_crack_class(records[-1].get("Class", ""))

                return Snapshot(
                    id=f"snap-{int(mtime)}",
                    image_url=f"/api/detections/snapshot-image/{rel_name}",
                    timestamp=ts_str,
                    severity=map_severity(last_class),
                    crack_class=last_class,
                )
            except Exception:
                return None

    def get_statistics(self) -> Statistics:
        """Compute aggregate detection statistics across historical logs."""
        with self._lock:
            records = self.get_all_records()
            counts = {
                CrackClass.SMALL_CRACK: 0,
                CrackClass.MEDIUM_CRACK: 0,
                CrackClass.LARGE_CRACK: 0,
                CrackClass.BROKEN_CHAIN: 0,
            }
            critical_alerts = 0

            for r in records:
                cls = map_crack_class(r.get("Class", ""))
                counts[cls] += 1
                if map_severity(cls) == Severity.CRITICAL:
                    critical_alerts += 1

            return Statistics(
                total_detections=len(records),
                small_crack=counts[CrackClass.SMALL_CRACK],
                medium_crack=counts[CrackClass.MEDIUM_CRACK],
                large_crack=counts[CrackClass.LARGE_CRACK],
                broken_chain=counts[CrackClass.BROKEN_CHAIN],
                critical_alerts=critical_alerts,
            )

    def get_detection_distribution(self) -> List[DetectionDistributionSlice]:
        """Compute distribution slices grouped by crack class."""
        stats = self.get_statistics()
        return [
            DetectionDistributionSlice(crack_class=CrackClass.SMALL_CRACK, count=stats.small_crack),
            DetectionDistributionSlice(crack_class=CrackClass.MEDIUM_CRACK, count=stats.medium_crack),
            DetectionDistributionSlice(crack_class=CrackClass.LARGE_CRACK, count=stats.large_crack),
            DetectionDistributionSlice(crack_class=CrackClass.BROKEN_CHAIN, count=stats.broken_chain),
        ]

    def get_severity_trend(self) -> List[SeverityTrendPoint]:
        """Compute time-series severity points grouped by date/hour."""
        with self._lock:
            records = self.get_all_records()
            trend_map = {}

            for r in records:
                ts_str = r.get("Timestamp", "")
                try:
                    dt = datetime.strptime(ts_str[:13], "%Y-%m-%d %H")
                    key = dt.strftime("%H:00")
                except Exception:
                    key = ts_str[:10] if len(ts_str) >= 10 else "Today"

                if key not in trend_map:
                    trend_map[key] = {"low": 0, "medium": 0, "high": 0, "critical": 0}

                cls = map_crack_class(r.get("Class", ""))
                sev = map_severity(cls)
                if sev == Severity.LOW:
                    trend_map[key]["low"] += 1
                elif sev == Severity.MEDIUM:
                    trend_map[key]["medium"] += 1
                elif sev == Severity.HIGH:
                    trend_map[key]["high"] += 1
                elif sev == Severity.CRITICAL:
                    trend_map[key]["critical"] += 1

            points = []
            for key, counts in trend_map.items():
                points.append(
                    SeverityTrendPoint(
                        timestamp=key,
                        low=counts["low"],
                        medium=counts["medium"],
                        high=counts["high"],
                        critical=counts["critical"],
                    )
                )

            if not points:
                points.append(
                    SeverityTrendPoint(
                        timestamp=datetime.now().strftime("%H:00"),
                        low=0,
                        medium=0,
                        high=0,
                        critical=0,
                    )
                )

            return points
