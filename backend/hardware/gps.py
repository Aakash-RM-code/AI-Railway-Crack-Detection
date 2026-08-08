"""GPS service — wraps the ESP32 cached GPS feed for the rest of the app."""


class GpsService:
    """Provides GPS position readings from the ESP32 rover.

    The ESP32 controller already polls and caches GPS data in the background;
    this service exposes that cache in a hardware-agnostic way so the rest of
    the backend (and a future React frontend) never talks to the ESP32 HTTP
    protocol directly.
    """

    def __init__(self, esp32_controller):
        self._esp = esp32_controller

    def get_gps(self, force_refresh: bool = False) -> str | None:
        """Return the GPS string (e.g. "12.923456,80.123456") or None."""
        return self._esp.get_gps(force_refresh=force_refresh)

    def get_cached_gps(self) -> str | None:
        """Return the cached GPS string without triggering a network call."""
        return self._esp.get_cached_gps()

    def get_coordinates(self) -> tuple[float, float] | None:
        """Return (lat, lon) if a fix is available, else None."""
        return self._esp.get_gps_coordinates()

    def has_fix(self) -> bool:
        """True when a valid GPS fix is cached."""
        gps = self.get_cached_gps()
        return bool(gps) and gps != "NO_FIX"
