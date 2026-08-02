from ultralytics import YOLO

class CrackDetector:

    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def detect(self, frame):

        results = self.model(
            frame,
            conf=0.4,
            verbose=False
        )

        return results