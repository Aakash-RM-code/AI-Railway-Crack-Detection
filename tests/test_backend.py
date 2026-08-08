"""Backend smoke tests — import graph, config paths, and API surface.

Run from the project root:

    python -m pytest tests/ -q
    # or
    python -m unittest discover tests
"""
import os
import unittest

import config


class TestConfigPaths(unittest.TestCase):
    def test_model_path_exists(self):
        self.assertTrue(os.path.isfile(config.MODEL_PATH), f"missing model: {config.MODEL_PATH}")

    def test_model_path_points_at_best_pt(self):
        self.assertTrue(config.MODEL_PATH.endswith(os.path.join("models", "best.pt")))

    def test_directories_resolve(self):
        for key in ("MODELS_DIR", "DETECTIONS_DIR", "LOGS_DIR", "REPORTS_DIR", "CONFIG_DIR"):
            self.assertTrue(getattr(config, key), key)

    def test_confidence_threshold_valid(self):
        self.assertGreater(config.CONFIDENCE_THRESHOLD, 0.0)
        self.assertLessEqual(config.CONFIDENCE_THRESHOLD, 1.0)


class TestBackendImports(unittest.TestCase):
    def test_detector(self):
        from backend.detector.detector import CrackDetector
        self.assertTrue(callable(CrackDetector.detect))

    def test_hardware(self):
        from backend.hardware.esp32 import ESP32Controller
        from backend.hardware.gps import GpsService
        from backend.hardware.gsm import GsmService
        self.assertTrue(callable(ESP32Controller.submit))

    def test_services(self):
        from backend.services.camera import CameraManager, CameraPipeline, get_pipeline
        from backend.services.alert_manager import AlertManager
        from backend.services.statistics_manager import StatisticsManager
        from backend.services.history_manager import HistoryManager
        from backend.services.logger import DetectionLogger
        from backend.services.report_generator import generate_report
        self.assertTrue(callable(get_pipeline))
        self.assertTrue(callable(generate_report))

    def test_api(self):
        from backend.api import routes, schemas, websocket
        self.assertTrue(hasattr(routes, "router"))
        self.assertTrue(hasattr(schemas, "RuntimeState"))
        self.assertTrue(hasattr(websocket, "router"))

    def test_storage(self):
        from backend.storage.gsm_store import load_phone_number, save_phone_number
        self.assertTrue(callable(load_phone_number))
        self.assertTrue(callable(save_phone_number))


class TestFastApiApp(unittest.TestCase):
    def test_app_constructs(self):
        from backend.main import app
        self.assertIsNotNone(app)

    def test_health_endpoint(self):
        from fastapi.testclient import TestClient
        from backend.main import app

        client = TestClient(app)
        resp = client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
