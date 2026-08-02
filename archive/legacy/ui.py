# ARCHIVED — legacy cv2 overlay drawing used by the legacy main.py only.
# Superseded by the Flet dashboard (ui/). Kept for reference.
import cv2
from datetime import datetime

class UI:

    def __init__(self):
        pass

    def draw(self, frame, results, fps):

        crack_count = len(results[0].boxes)

        # ---------- Title ----------
        cv2.rectangle(frame, (0, 0), (1280, 60), (50, 50, 50), -1)

        cv2.putText(
            frame,
            "Railway Crack Detection System",
            (20,40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            2
        )

        # ---------- Status ----------

        if crack_count > 0:

            color = (0,0,255)
            text = "CRACK DETECTED"

        else:

            color = (0,255,0)
            text = "SAFE"

        cv2.rectangle(frame,(10,70),(420,125),color,-1)

        cv2.putText(
            frame,
            text,
            (25,108),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255,255,255),
            3
        )

        # ---------- Counter ----------

        cv2.putText(
            frame,
            f"Cracks : {crack_count}",
            (20,170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        # ---------- FPS ----------

        cv2.putText(
            frame,
            f"FPS : {fps:.1f}",
            (20,205),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        # ---------- Time ----------

        current_time = datetime.now().strftime("%H:%M:%S")

        cv2.putText(
            frame,
            current_time,
            (20,240),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255,255,255),
            2
        )

        return frame