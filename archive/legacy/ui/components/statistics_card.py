import flet as ft

from ui.theme import Palette, col
from ui.components.base import kpi_card


class StatisticsCard:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._value_texts = {}

    def _kpi(self, key: str, icon, label: str, color: str) -> ft.Container:
        value = ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=Palette.TEXT)
        self._value_texts[key] = value
        return kpi_card(icon, label, 0, color, value_control=value)

    def build(self) -> ft.Control:
        cards = [
            self._kpi("total", ft.Icons.INSIGHTS, "Total Detections", Palette.INFO),
            self._kpi("small", ft.Icons.REMOVE, "Small Crack", Palette.WARNING),
            self._kpi("medium", ft.Icons.REMOVE_CIRCLE_OUTLINE, "Medium Crack", Palette.ORANGE),
            self._kpi("large", ft.Icons.REMOVE_CIRCLE, "Large Crack", Palette.DANGER),
            self._kpi("broken", ft.Icons.BROKEN_IMAGE, "Broken Rail", Palette.CRITICAL),
            self._kpi("critical", ft.Icons.ERROR, "Critical Alerts", Palette.DANGER),
        ]
        return ft.ResponsiveRow(
            controls=[
                ft.Container(content=card, col=col(xs=6, sm=6, md=4, lg=2))
                for card in cards
            ],
            spacing=12,
            run_spacing=12,
        )

    def update(self) -> None:
        stats = self.controller.get_stats()
        severity_counts = self.controller.get_severity_counts()
        self._value_texts["total"].value = str(stats["total"])
        self._value_texts["small"].value = str(stats["small"])
        self._value_texts["medium"].value = str(stats["medium"])
        self._value_texts["large"].value = str(stats["large"])
        self._value_texts["broken"].value = str(stats["broken"])
        self._value_texts["critical"].value = str(severity_counts.get("CRITICAL", 0))
