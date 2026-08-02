# ARCHIVED — legacy OpenCV-window application superseded by the Flet app
# (app.py). Kept for reference only; references modules by their pre-refactor
# names and calls esp.update() which no longer exists — NOT runnable as-is.
import cv2
import time

import config
from detector import CrackDetector
from logger import DetectionLogger
from ui import UI
from esp32 import ESP32Controller
from alert_manager import AlertManager


def main():

    # -----------------------------
    # Initialize Components
    # -----------------------------
    detector = CrackDetector(config.MODEL_PATH)
    ui = UI()
    logger = DetectionLogger()
    esp = ESP32Controller()
    alert_manager = AlertManager()

    # -----------------------------
    # Open Camera
    # -----------------------------
    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    if not cap.isOpened():
        print("❌ Error: Cannot open webcam")
        return

    prev_time = time.time()

    print("===================================")
    print(" Railway Crack Detection Started ")
    print(" Press 'Q' to Exit")
    print("===================================")

    while True:

        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame.")
            break

        # -----------------------------
        # FPS
        # -----------------------------
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # -----------------------------
        # Run YOLO
        # -----------------------------
        results = detector.detect(frame)

        # -----------------------------
        # Alert Manager
        # -----------------------------
        alert = alert_manager.process(
            results,
            detector.model.names
        )

        # Debug (remove later if you want)
        print(alert)

        # -----------------------------
        # Update ESP32
        # -----------------------------
        esp.update(alert["severity"])

        # -----------------------------
        # Logger
        # -----------------------------
        for box in results[0].boxes:

            conf = float(box.conf[0])

            if conf >= config.CONFIDENCE_THRESHOLD:

                cls = int(box.cls[0])
                class_name = detector.model.names[cls]

                logger.save_detection(
                    frame,
                    class_name,
                    conf
                )

        # -----------------------------
        # Draw YOLO
        # -----------------------------
        annotated_frame = results[0].plot()

        # -----------------------------
        # Draw Custom UI
        # -----------------------------
        annotated_frame = ui.draw(
            annotated_frame,
            results,
            fps
        )

        # -----------------------------
        # Display Alert
        # -----------------------------
        cv2.putText(
            annotated_frame,
            f"Status : {alert['severity']}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            alert["message"],
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # -----------------------------
        # Display Window
        # -----------------------------
        cv2.imshow(
            "Railway Crack Detection System",
            annotated_frame
        )

        # -----------------------------
        # Exit
        # -----------------------------
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    esp.close()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()