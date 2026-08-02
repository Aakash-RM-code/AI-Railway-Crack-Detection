"""
GPS Card UI Component
"""
import flet as ft
from datetime import datetime


class GPSCard:
    """GPS status card UI component"""

    def __init__(self, controller=None):
        self.controller = controller
        self._lat_text = None
        self._lon_text = None
        self._fix_status = None
        self._last_update_text = None

    def _build_gps_display(self) -> ft.Container:
        """Build GPS information display (once, reusing the same controls)."""
        self._fix_status = ft.Text(
            value="📍 Waiting for GPS...",
            size=14,
            color=ft.Colors.RED_400,
            weight=ft.FontWeight.BOLD,
        )
        self._lat_text = ft.Text(
            value="Latitude: N/A",
            size=13,
            color=ft.Colors.GREY_400,
        )
        self._lon_text = ft.Text(
            value="Longitude: N/A",
            size=13,
            color=ft.Colors.GREY_400,
        )
        self._last_update_text = ft.Text(
            value="Last Update: --",
            size=11,
            color=ft.Colors.GREY_500,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._fix_status,
                    self._lat_text,
                    self._lon_text,
                    self._last_update_text,
                ],
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.Padding.all(12),
            bgcolor=ft.Colors.GREY_900,
            border_radius=ft.BorderRadius.all(12),
        )

    def _set_no_fix(self) -> None:
        self._fix_status.value = "📍 Waiting for GPS..."
        self._fix_status.color = ft.Colors.RED_400
        self._lat_text.value = "Latitude: N/A"
        self._lon_text.value = "Longitude: N/A"

    def build(self) -> ft.Container:
        """Build the complete GPS card"""
        display = self._build_gps_display()

        main_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MY_LOCATION, size=16, color=ft.Colors.GREEN_400),
                        ft.Text(
                            "GPS Status",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN_400,
                        ),
                    ],
                    spacing=6,
                ),
                ft.Divider(height=4, color=ft.Colors.GREY_800),
                display,
            ],
            spacing=6,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        return ft.Container(
            content=main_content,
            padding=ft.Padding.all(14),
            bgcolor=ft.Colors.GREY_800,
            border_radius=ft.BorderRadius.all(16),
            shadow=ft.BoxShadow(
                blur_radius=20,
                color=ft.Colors.BLACK38,
                offset=ft.Offset(0, 5),
            ),
            height=185,
        )

    def update(self) -> None:
        """Refresh GPS display live from the controller (NO_FIX handled)."""
        if self.controller is None:
            return
        gps_str = None
        try:
            gps_str = self.controller.get_gps()
        except Exception:
            return

        if gps_str and gps_str != "NO_FIX":
            try:
                lat_str, lon_str = gps_str.split(",")
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                self._fix_status.value = "📍 GPS Fix"
                self._fix_status.color = ft.Colors.GREEN_400
                self._lat_text.value = f"Lat: {lat:.6f}"
                self._lon_text.value = f"Lon: {lon:.6f}"
            except (ValueError, AttributeError):
                self._set_no_fix()
        else:
            self._set_no_fix()

        self._last_update_text.value = (
            f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
        )

    def update_gps(self, state: dict):
        """Legacy helper kept for compatibility with prior integrations."""
        self.update()
