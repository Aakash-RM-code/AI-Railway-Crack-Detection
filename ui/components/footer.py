from datetime import datetime

import flet as ft

from ui.theme import Palette

APP_VERSION = "1.0.0"
DEVELOPER = "AI TrackSense Team"


class Footer:
    def __init__(self, controller, on_report=None) -> None:
        self.controller = controller
        self._on_report = on_report

    def build(self) -> ft.Control:
        return ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=16, vertical=10),
            border=ft.Border(
                top=ft.BorderSide(1, Palette.BORDER),
                left=ft.BorderSide(0),
                right=ft.BorderSide(0),
                bottom=ft.BorderSide(0),
            ),
            content=ft.ResponsiveRow(
                spacing=8,
                run_spacing=8,
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 5},
                        content=ft.Text(
                            f"TrackSense v{APP_VERSION} — AI Railway Crack Detection",
                            size=11,
                            color=Palette.TEXT_MUTED,
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 7},
                        content=ft.Row(
                            controls=[
                                ft.OutlinedButton(
                                    "Generate Report",
                                    icon=ft.Icons.PICTURE_AS_PDF,
                                    on_click=self._on_report,
                                    style=ft.ButtonStyle(
                                        color=Palette.TEXT,
                                        side=ft.BorderSide(1, Palette.BORDER),
                                    ),
                                ),
                                ft.Text(
                                    f"Session started {self.controller.started_at().strftime('%d %b %Y, %H:%M:%S')}",
                                    size=11,
                                    color=Palette.TEXT_MUTED,
                                ),
                                ft.Text(
                                    f"Developed by {DEVELOPER}",
                                    size=11,
                                    color=Palette.TEXT_MUTED,
                                ),
                            ],
                            spacing=16,
                            run_spacing=6,
                            wrap=True,
                            alignment=ft.MainAxisAlignment.END,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ],
            ),
        )
