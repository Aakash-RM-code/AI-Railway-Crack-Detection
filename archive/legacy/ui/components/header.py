from datetime import datetime

import flet as ft

from ui.theme import Palette, border_all


class Header:
    def __init__(self, page: ft.Page, controller) -> None:
        self.page = page
        self.controller = controller
        self.clock = ft.Text("--:--:--", size=13, color=Palette.TEXT_MUTED)
        self.status_pill = self._pill("SYSTEM READY", Palette.INFO)
        self.esp_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=Palette.BORDER)
        self.gps_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=Palette.BORDER)
        self.gsm_dot = ft.Container(width=8, height=8, border_radius=4, bgcolor=Palette.BORDER)

    def build(self) -> ft.Control:
        # Left group: logo + title. Right group: status badges + pill + clock.
        # On narrow screens the two groups stack; on wide screens they share a
        # single row (right group stays right-aligned, as before).
        return ft.Container(
            bgcolor=Palette.SURFACE,
            border=ft.Border(
                bottom=ft.BorderSide(1, Palette.BORDER),
                left=ft.BorderSide(0),
                right=ft.BorderSide(0),
                top=ft.BorderSide(0),
            ),
            padding=ft.padding.Padding.symmetric(horizontal=16, vertical=10),
            content=ft.ResponsiveRow(
                spacing=8,
                run_spacing=8,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 7},
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=44,
                                    height=44,
                                    bgcolor=Palette.PRIMARY,
                                    border_radius=12,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Icon(ft.Icons.TRAIN, color=Palette.BLACK, size=26),
                                ),
                                ft.Container(
                                    expand=True,
                                    content=ft.Column(
                                        controls=[
                                            ft.Text(
                                                "Railway Crack Detection System",
                                                size=17,
                                                weight=ft.FontWeight.BOLD,
                                                color=Palette.TEXT,
                                            ),
                                            ft.Text(
                                                "AI TrackSense — Track Health Monitoring",
                                                size=11,
                                                color=Palette.TEXT_MUTED,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ),
                            ],
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 5},
                        content=ft.Row(
                            controls=[
                                self._badge("ESP32", self.esp_dot),
                                self._badge("GPS", self.gps_dot),
                                self._badge("GSM", self.gsm_dot),
                                self.status_pill,
                                self.clock,
                            ],
                            spacing=10,
                            run_spacing=6,
                            wrap=True,
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
            ),
        )

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def update_status(self) -> None:
        """Refresh the live clock and connection indicators.

        Called from the dashboard's single refresh loop so all header state
        ships with the same page.update() — no background thread required.
        """
        self.clock.value = datetime.now().strftime("%H:%M:%S")
        if self.controller is None:
            return
        try:
            online = bool(self.controller.get_esp_status().get("online", False))
        except Exception:
            online = False
        self.esp_dot.bgcolor = Palette.SUCCESS if online else Palette.BORDER
        self.gsm_dot.bgcolor = Palette.SUCCESS if online else Palette.BORDER
        try:
            gps = self.controller.get_gps()
            gps_fix = bool(gps) and gps != "NO_FIX"
        except Exception:
            gps_fix = False
        self.gps_dot.bgcolor = Palette.SUCCESS if gps_fix else Palette.BORDER

    def set_status(self, text: str, color: str) -> None:
        self.status_pill.content = self._pill(text, color)

    def _badge(self, label: str, dot: ft.Container) -> ft.Container:
        return ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=10, vertical=5),
            bgcolor=Palette.SURFACE_ALT,
            border_radius=20,
            content=ft.Row(
                controls=[
                    dot,
                    ft.Text(label, size=11, color=Palette.TEXT_MUTED),
                ],
                spacing=6,
                tight=True,
            ),
        )

    def _pill(self, text: str, color: str) -> ft.Container:
        return ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=14, vertical=6),
            bgcolor=color + "1A",
            border_radius=20,
            content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color=color),
        )
