"""Phase 2 WebSocket Channel Tests.

Verifies connection and communication across separate WebSocket channels:
/ws/telemetry, /ws/detections, /ws/camera-status, /ws/stream.
"""

import unittest
from fastapi.testclient import TestClient
from backend.main import app


class TestPhase2WebSockets(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_telemetry_websocket(self):
        with self.client.websocket_connect("/ws/telemetry") as websocket:
            websocket.send_text("ping")
            data = websocket.receive_text()
            self.assertEqual(data, "pong")

    def test_detections_websocket(self):
        with self.client.websocket_connect("/ws/detections") as websocket:
            websocket.send_text("ping")
            data = websocket.receive_text()
            self.assertEqual(data, "pong")

    def test_camera_status_websocket(self):
        with self.client.websocket_connect("/ws/camera-status") as websocket:
            websocket.send_text("ping")
            data = websocket.receive_text()
            self.assertEqual(data, "pong")

    def test_legacy_stream_websocket(self):
        with self.client.websocket_connect("/ws/stream") as websocket:
            websocket.send_text("ping")
            data = websocket.receive_json()
            self.assertIn("camera", data)
            self.assertIn("alert", data)


if __name__ == "__main__":
    unittest.main()
