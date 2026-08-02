import flet as ft

from ui.theme import Palette
from ui.components.base import section_card, status_pill


HEALTH_COLORS = {
    "EXCELLENT": Palette.SUCCESS,
    "GOOD": Palette.INFO,
    "WARNING": Palette.WARNING,
    "CRITICAL": Palette.DANGER,
}


class HealthCard:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._ring = None
        self._score_text = None
        self._pill = None
        self._pill_text = None
        self._note_text = None

    def _build_body(self) -> ft.Control:
        health = self.controller.get_health()
        color = HEALTH_COLORS.get(health["status"].upper(), Palette.TEXT_MUTED)

        self._ring = ft.ProgressRing(
            value=health["score"] / 100,
            stroke_width=9,
            color=color,
            bgcolor=Palette.SURFACE_ALT,
        )
        self._score_text = ft.Text(
            f"{health['score']}%",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
        ring = ft.Container(
            width=104,
            height=104,
            alignment=ft.Alignment(0, 0),
            content=ft.Stack(
                controls=[
                    self._ring,
                    ft.Container(
                        alignment=ft.Alignment(0, 0),
                        content=self._score_text,
                    ),
                ],
                alignment=ft.Alignment(0, 0),
            ),
        )

        self._pill = status_pill(health["status"], color)
        self._pill_text = self._pill.content.controls[0]
        self._note_text = ft.Text(health["note"], size=11, color=Palette.TEXT_MUTED)

        body = ft.Row(
            controls=[
                ring,
                ft.Column(
                    controls=[
                        self._pill,
                        ft.Text("Track condition", size=12, color=Palette.TEXT_MUTED),
                        self._note_text,
                    ],
                    spacing=8,
                ),
            ],
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return body

    def build(self) -> ft.Control:
        return section_card(
            "Track Health",
            self._build_body(),
            icon=ft.Icon(ft.Icons.FAVORITE_OUTLINED, size=16, color=Palette.TEXT_MUTED),
        )

    def update(self) -> None:
        health = self.controller.get_health()
        color = HEALTH_COLORS.get(health["status"].upper(), Palette.TEXT_MUTED)
        self._ring.value = health["score"] / 100
        self._ring.color = color
        self._score_text.value = f"{health['score']}%"
        self._pill_text.value = health["status"]
        self._pill_text.color = color
        self._pill.bgcolor = color + "1F"
        self._note_text.value = health["note"]
