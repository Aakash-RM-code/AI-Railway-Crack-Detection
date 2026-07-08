import os
import csv
import cv2
from datetime import datetime


class DetectionLogger:

    def __init__(self):
        self.last_saved = 0
        self.cooldown = 5

        self.image_folder = "detections"
        self.log_folder = "logs"
        self.csv_file = os.path.join(self.log_folder, "detections.csv")

        os.makedirs(self.image_folder, exist_ok=True)
        os.makedirs(self.log_folder, exist_ok=True)

        # Create CSV file if it doesn't exist
        if not os.path.exists(self.csv_file):

            with open(self.csv_file, "w", newline="") as file:

                writer = csv.writer(file)

                writer.writerow([
                    "Timestamp",
                    "Class",
                    "Confidence",
                    "Image"
                ])

    def save_detection(self, frame, class_name, confidence):
        import time

        current = time.time()

        if current - self.last_saved < self.cooldown:
            return

        self.last_saved = current

        timestamp = datetime.now()

        image_name = timestamp.strftime("%Y%m%d_%H%M%S") + ".jpg"

        image_path = os.path.join(
            self.image_folder,
            image_name
        )

        cv2.imwrite(image_path, frame)

        with open(self.csv_file, "a", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                class_name,
                round(confidence, 2),
                image_name
            ])