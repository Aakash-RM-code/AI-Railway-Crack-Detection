import config


class AlertManager:

    def __init__(self):
        self.last_alert = None

    def process(self, results, model_names):

        alert = {
            "detected": False,
            "severity": "SAFE",
            "class_name": None,
            "confidence": 0.0,
            "message": "Track is Safe"
        }

        if len(results[0].boxes) == 0:
            return alert

        # Find the highest-confidence detection
        best_box = max(results[0].boxes, key=lambda box: float(box.conf[0]))

        confidence = float(best_box.conf[0])

        if confidence < config.CONFIDENCE_THRESHOLD:
            return alert

        class_id = int(best_box.cls[0])
        class_name = model_names[class_id].lower()

        alert["detected"] = True
        alert["class_name"] = class_name
        alert["confidence"] = confidence

        # Assign severity
        if "small" in class_name:
            alert["severity"] = "LOW"
            alert["message"] = "Minor Crack Detected"

        elif "medium" in class_name:
            alert["severity"] = "MEDIUM"
            alert["message"] = "Moderate Crack Detected"

        elif "large" in class_name:
            alert["severity"] = "HIGH"
            alert["message"] = "Immediate Inspection Required"

        elif "broken" in class_name:
            alert["severity"] = "CRITICAL"
            alert["message"] = "Track Failure Detected"

        else:
            alert["severity"] = "UNKNOWN"
            alert["message"] = "Unknown Object"

        return alert