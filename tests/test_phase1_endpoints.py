"""Comprehensive Phase 1 REST endpoint tests.

Verifies that all Phase 1 endpoints return 200 OK and adhere to the Pydantic schemas.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestPhase1Endpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), {"status": "ok"})

    def test_system_status(self):
        res = self.client.get("/api/system/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("online"))
        self.assertIn("uptimeSeconds", data)
        self.assertIn("version", data)
        self.assertIn("devices", data)

    def test_camera_state(self):
        res = self.client.get("/api/camera/state")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data.get("source"), "esp32-cam")
        self.assertIn("state", data)
        self.assertIn("fps", data)

    def test_camera_connect_disconnect(self):
        res_conn = self.client.post("/api/camera/connect", json={"source": "esp32-cam"})
        self.assertEqual(res_conn.status_code, 200)
        self.assertEqual(res_conn.json().get("source"), "esp32-cam")

        res_disc = self.client.post("/api/camera/disconnect")
        self.assertEqual(res_disc.status_code, 200)

    def test_alerts_latest(self):
        res = self.client.get("/api/alerts/latest")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("severity", data)
        self.assertIn("message", data)

    def test_track_health(self):
        res = self.client.get("/api/track-health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("overall", data)
        self.assertIn("status", data)
        self.assertIn("inspectedMeters", data)

    def test_gps(self):
        res = self.client.get("/api/gps")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)
        self.assertIn("hasFix", data)

    def test_gsm_status(self):
        res = self.client.get("/api/gsm/status")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("state", data)
        self.assertIn("signalStrength", data)

    def test_send_sms(self):
        # ESP32 is disabled in the test environment, so SMS dispatch must fail
        # explicitly (503) rather than fake a successful delivery.
        res = self.client.post("/api/gsm/send-sms", json={"phoneNumber": "+1234567890", "message": "Test SMS"})
        self.assertEqual(res.status_code, 503)
        self.assertIn("unavailable", res.json().get("detail", "").lower())

    def test_statistics(self):
        res = self.client.get("/api/statistics")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("totalDetections", data)
        self.assertIn("smallCrack", data)

    def test_statistics_distribution(self):
        res = self.client.get("/api/statistics/distribution")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_statistics_trend(self):
        res = self.client.get("/api/statistics/trend")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIsInstance(data, list)

    def test_detections_paginated(self):
        res = self.client.get("/api/detections?page=1&pageSize=5")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total", data)

    def test_latest_snapshot(self):
        res = self.client.get("/api/detections/latest-snapshot")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("id", data)

    def test_rover_state_and_command(self):
        res_state = self.client.get("/api/rover/state")
        self.assertEqual(res_state.status_code, 200)
        data = res_state.json()
        self.assertIn("state", data)
        self.assertIn("speed", data)
        self.assertEqual(data.get("speed"), 0)

        # No ESP32 in the test environment -> commands fail explicitly (503),
        # never a fake successful command.
        res_cmd = self.client.post("/api/rover/command", json={"command": "stop", "speed": 100})
        self.assertEqual(res_cmd.status_code, 503)
        self.assertIn("unavailable", res_cmd.json().get("detail", "").lower())

    def test_report_generation(self):
        res = self.client.post("/api/reports/generate")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("path", data)
        self.assertIn("url", data)


if __name__ == "__main__":
    unittest.main()
