"""Hardware command-interface contract tests.

Verifies that the rover command endpoint:
* returns a controlled 503 (never fake success) when hardware is absent/offline,
* requires the command methods exposed by the controller (set_speed etc.) and
  converts a missing method into a 503 instead of an unhandled AttributeError,
* accepts speed-only set_speed and rejects unsupported LEFT/RIGHT explicitly,
  while keeping the real ESP32Controller and its semantics untouched.
"""

import unittest

from fastapi.testclient import TestClient

from backend.api import schemas
from backend.hardware.esp32 import ESP32Controller
from backend.main import app
from backend.services.camera import get_pipeline


class FakeESP32:
    """Dummy controller implementing exactly the interface the API requires.
    It records dispatched commands but never fakes a hardware success."""

    def __init__(self, online: bool = True):
        self._online = online
        self._status = {"speed": 150, "moving": True, "direction": "FORWARD"}
        self.dispatched = []

    def is_online(self) -> bool:
        return self._online

    def get_cached_status(self) -> dict:
        return dict(self._status)

    def get_cached_gps(self) -> None:
        return None

    def get_gps_coordinates(self) -> None:
        return None

    def submit(self, command, *args, key=None, debounce=0.0):
        self.dispatched.append((command, args, key))

    # Command methods the route calls via submit()
    def set_speed(self, speed):
        self._status["speed"] = speed

    def forward(self):
        return "OK"

    def backward(self):
        return "OK"

    def stop(self):
        return "OK"

    def emergency_stop(self):
        return "CRACK_STOPPED"


class FakeESP32NoSpeed(FakeESP32):
    """Controller without set_speed — the route must 503, not AttributeError."""

    set_speed = None  # attribute absent: getattr returns None


class TestRoverCommandInterface(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.fake = FakeESP32(online=True)
        get_pipeline(esp32_controller=self.fake)

    def tearDown(self):
        get_pipeline().set_esp32(None)

    def test_set_speed_interface_exists(self):
        self.assertTrue(callable(getattr(self.fake, "set_speed", None)))
        self.assertTrue(callable(getattr(ESP32Controller, "set_speed", None)))

    def test_set_speed_command_dispatches(self):
        res = self.client.post("/api/rover/command", json={"command": "set_speed", "speed": 200})
        self.assertEqual(res.status_code, 200)
        keys = [key for _, _, key in self.fake.dispatched if key == "speed"]
        self.assertEqual(keys, ["speed"])

    def test_offline_controller_returns_503(self):
        self.fake._online = False
        res = self.client.post("/api/rover/command", json={"command": "forward"})
        self.assertEqual(res.status_code, 503)
        self.assertIn("unavailable", res.json().get("detail", "").lower())

    def test_no_esp_returns_503(self):
        get_pipeline().set_esp32(None)
        res = self.client.post("/api/rover/command", json={"command": "stop"})
        self.assertEqual(res.status_code, 503)
        self.assertIn("unavailable", res.json().get("detail", "").lower())

    def test_missing_set_speed_is_503_not_attribute_error(self):
        self.fake = FakeESP32NoSpeed(online=True)
        get_pipeline().set_esp32(self.fake)
        res = self.client.post("/api/rover/command", json={"command": "set_speed", "speed": 100})
        self.assertEqual(res.status_code, 503)
        self.assertIn("unavailable", res.json().get("detail", "").lower())

    def test_left_right_rejected_400(self):
        for cmd in ("left", "right"):
            with self.subTest(command=cmd):
                res = self.client.post("/api/rover/command", json={"command": cmd})
                self.assertEqual(res.status_code, 400)

    def test_forward_dispatches_via_submit(self):
        res = self.client.post("/api/rover/command", json={"command": "forward"})
        self.assertEqual(res.status_code, 200)
        keys = ["any" for _, _, key in self.fake.dispatched if key == "move"]
        self.assertTrue(keys)

    def test_speed_out_of_range_rejected_by_schema(self):
        res = self.client.post("/api/rover/command", json={"command": "set_speed", "speed": 999})
        self.assertEqual(res.status_code, 422)


if __name__ == "__main__":
    unittest.main()