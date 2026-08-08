"""History service — delegates detection reading to DetectionRepository."""

from backend.storage.repository import DetectionRepository


class HistoryManager:
    """Delegates detection history and snapshot reading to DetectionRepository."""

    def __init__(self):
        self.repo = DetectionRepository()

    def read(self, limit: int = 10) -> list[dict]:
        raw_records = self.repo.get_all_records()
        rows = []
        for row in raw_records[-limit:]:
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
        return rows

    def latest_snapshot_base64(self) -> str:
        import base64
        import os
        snap = self.repo.get_latest_snapshot()
        if not snap or not snap.image_url:
            return ""
        filename = os.path.basename(snap.image_url)
        filepath = os.path.join(self.repo.detections_dir, filename)
        try:
            with open(filepath, "rb") as f:
                return base64.b64encode(f.read()).decode("ascii")
        except OSError:
            return ""
