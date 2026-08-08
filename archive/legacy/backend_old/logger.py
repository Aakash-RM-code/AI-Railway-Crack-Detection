import os
import csv
import cv2
from datetime import datetime
import glob

import config


class DetectionLogger:

    def __init__(self):
        self.last_saved = 0
        self.cooldown = 5

        self.image_folder = config.DETECTIONS_DIR
        self.log_folder = config.LOGS_DIR
        self.csv_file = config.HISTORY_CSV

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
            return False

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

            image_relative_path = os.path.join("detections", image_name)

            writer.writerow([
    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    class_name,
    round(confidence, 2),
    image_relative_path
])
            return True
       
        