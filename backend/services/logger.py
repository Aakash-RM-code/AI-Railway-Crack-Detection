"""Logging service — delegates detection writing to DetectionRepository."""

from backend.storage.repository import DetectionRepository


class DetectionLogger:
    """Delegates frame snapshot saving and detection history writing to DetectionRepository."""

    def __init__(self, cooldown: int = 3):
        self.repo = DetectionRepository(cooldown=cooldown)

    def save_detection(self, frame, class_name: str, confidence: float, latitude: float = 0.0, longitude: float = 0.0) -> bool:
        """Delegates detection logging to DetectionRepository."""
        return self.repo.save_detection(
            frame=frame,
            class_name=class_name,
            confidence=confidence,
            latitude=latitude,
            longitude=longitude,
        )
