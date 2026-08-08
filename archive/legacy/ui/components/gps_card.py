"""
GPS Card UI Component
"""
import flet as ft
from datetime import datetime

from ui.theme import (
    Palette,
    CARD_SHADOW,
    border_all,
    SPACE_XS,
    SPACE_SM,
    SPACE_MD,
    PADDING_CARD,
    RADIUS_CARD,
    RADIUS_INNER,
)


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
            color=Palette.DANGER,
            weight=ft.FontWeight.BOLD,
        )
        self._lat_text = ft.Text(
            value="Latitude: N/A",
            size=13,
            color=Palette.TEXT_MUTED,
        )
        self._lon_text = ft.Text(
            value="Longitude: N/A",
            size=13,
            color=Palette.TEXT_MUTED,
        )
        self._last_update_text = ft.Text(
            value="Last Update: --",
            size=11,
            color=Palette.TEXT_MUTED,
        )

        return ft.Container(
            content=ft.Column(
                controls=[
                    self._fix_status,
                    self._lat_text,
                    self._lon_text,
                    self._last_update_text,
                ],
                spacing=SPACE_SM,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.padding.Padding.all(SPACE_MD),
            bgcolor=Palette.SURFACE_ALT,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_INNER,
        )

    def _set_no_fix(self) -> None:
        self._fix_status.value = "📍 Waiting for GPS..."
        self._fix_status.color = Palette.DANGER
        self._lat_text.value = "Latitude: N/A"
        self._lon_text.value = "Longitude: N/A"

    def build(self) -> ft.Container:
        """Build the complete GPS card"""
        display = self._build_gps_display()

        main_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MY_LOCATION, size=16, color=Palette.SUCCESS),
                        ft.Text(
                            "GPS Status",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=Palette.SUCCESS,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            "SATELLITE FIX",
                            size=10,
                            color=Palette.TEXT_MUTED,
                        ),
                    ],
                    spacing=SPACE_SM,
                ),
                ft.Divider(height=4, color=Palette.BORDER),
                display,
            ],
            spacing=SPACE_SM,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        return ft.Container(
            content=main_content,
            padding=ft.padding.Padding.all(PADDING_CARD),
            bgcolor=Palette.SURFACE,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_CARD,
            shadow=CARD_SHADOW,
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
                self._fix_status.color = Palette.SUCCESS
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
