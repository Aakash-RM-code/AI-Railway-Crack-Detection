import cv2
import time
from logger import DetectionLogger
from detector import CrackDetector
from ui import UI
from esp32 import ESP32Controller


def main():

    # -----------------------------
    # Initialize detector and UI
    # -----------------------------
    detector = CrackDetector("best.pt")
    ui = UI()
    logger = DetectionLogger()
    esp = ESP32Controller(port="COM3")

    # -----------------------------
    # Open Camera
    # Change 0 or 1 depending on your webcam
    # -----------------------------
    cap = cv2.VideoCapture(1)

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
        # FPS Calculation
        # -----------------------------
        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # -----------------------------
        # Run YOLO Detection
        # -----------------------------
        results = detector.detect(frame)
        # Check if any crack is detected with sufficient confidence
        crack_detected = False

        for box in results[0].boxes:
            confidence = float(box.conf[0])

            if confidence >= 0.70:
                crack_detected = True
                break

# Update ESP32 LEDs
        esp.update(crack_detected)

        # -----------------------------
        # detectors.py
        # -----------------------------
        for box in results[0].boxes:

            cls = int(box.cls[0])

            conf = float(box.conf[0])

            class_name = detector.model.names[cls]

            logger.save_detection(
            frame,
            class_name,
            conf
            )


        # -----------------------------
        # Draw YOLO Bounding Boxes
        # -----------------------------
        annotated_frame = results[0].plot()

        # -----------------------------
        # Draw Professional UI
        # -----------------------------
        annotated_frame = ui.draw(
            annotated_frame,
            results,
            fps
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