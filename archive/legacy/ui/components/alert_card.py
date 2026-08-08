import flet as ft

from ui.theme import Palette, severity_color
from ui.components.base import section_card, status_pill


class AlertCard:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._pill = None
        self._pill_icon = None
        self._pill_text = None
        self._class_text = None
        self._confidence_text = None
        self._confidence_bar = None
        self._message_icon = None
        self._message_text = None

    def _build_body(self) -> ft.Control:
        alert = self.controller.get_alert()
        color = severity_color(alert["severity"])

        self._pill = status_pill(
            alert["severity"],
            color,
            icon=ft.Icon(ft.Icons.REPORT_GMAILERRORRED, size=14, color=color),
        )
        self._pill_icon = self._pill.content.controls[0]
        self._pill_text = self._pill.content.controls[1]

        self._class_text = ft.Text(
            alert["class_name"] if alert["class_name"] else "—",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
        self._confidence_text = ft.Text(
            f"{alert['confidence']:.1%}",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
        self._confidence_bar = ft.ProgressBar(
            value=alert["confidence"],
            color=color,
            bgcolor=Palette.SURFACE_ALT,
            height=6,
            border_radius=3,
        )
        self._message_icon = ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=color)
        self._message_text = ft.Text(alert["message"], size=11, color=Palette.TEXT)

        body = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._pill,
                        self._class_text,
                        ft.Container(expand=True),
                        ft.FilledButton(
                            "SOS",
                            icon=ft.Icons.SOS,
                            bgcolor=Palette.DANGER,
                            color=ft.Colors.WHITE,
                            on_click=lambda e: None,
                        ),
                    ],
                    spacing=10,
                    wrap=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        ft.Text("Confidence", size=11, color=Palette.TEXT_MUTED),
                        ft.Container(expand=True),
                        self._confidence_text,
                    ],
                ),
                self._confidence_bar,
                ft.Container(
                    padding=ft.padding.Padding.all(10),
                    bgcolor=Palette.SURFACE_ALT,
                    border_radius=8,
                    content=ft.Row(
                        controls=[
                            self._message_icon,
                            self._message_text,
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                ),
            ],
            spacing=10,
        )
        return body

    def build(self) -> ft.Control:
        return section_card(
            "Alert Status",
            self._build_body(),
            icon=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, size=16, color=Palette.TEXT_MUTED),
            trailing=ft.Text("LIVE", size=10, color=Palette.SUCCESS),
        )

    def update(self) -> None:
        alert = self.controller.get_alert()
        color = severity_color(alert["severity"])
        self._pill_text.value = alert["severity"]
        self._pill_text.color = color
        self._pill.bgcolor = color + "1F"
        self._pill_icon.color = color
        self._class_text.value = alert["class_name"] if alert["class_name"] else "—"
        self._confidence_text.value = f"{alert['confidence']:.1%}"
        self._confidence_bar.value = alert["confidence"]
        self._confidence_bar.color = color
        self._message_icon.color = color
        self._message_text.value = alert["message"]
