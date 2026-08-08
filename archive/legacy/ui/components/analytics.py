import flet as ft

from ui.theme import Palette, severity_color
from ui.components.base import section_card


class AnalyticsPanel:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._dist = {}
        self._dist_total = None
        self._sev = {}
        self._sev_total = None
        self._dist_card = None
        self._sev_card = None

    def _new_row(self, label: str, color: str):
        value_text = ft.Text("0", size=12, weight=ft.FontWeight.BOLD, color=Palette.TEXT)
        pct_text = ft.Text("0%", size=11, weight=ft.FontWeight.BOLD, color=color)
        bar = ft.ProgressBar(
            value=0.0,
            color=color,
            bgcolor=Palette.SURFACE_ALT,
            height=6,
            border_radius=4,
        )
        row = ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(label.upper(), size=11, color=Palette.TEXT_MUTED),
                            ft.Container(expand=True),
                            value_text,
                            pct_text,
                        ],
                        spacing=8,
                    ),
                    bar,
                ],
                spacing=4,
            )
        return row, {"value": value_text, "pct": pct_text, "bar": bar}

    def build_distribution(self) -> ft.Control:
        if self._dist_card is not None:
            return self._dist_card
        rows = []
        for label, color in [
            ("Small", Palette.WARNING),
            ("Medium", Palette.ORANGE),
            ("Large", Palette.DANGER),
            ("Broken", Palette.CRITICAL),
        ]:
            row, rec = self._new_row(label, color)
            self._dist[label] = rec
            rows.append(row)

        self._dist_total = ft.Text(
            "0 total",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
        body = ft.Column(
            controls=[
                *rows,
                ft.Row(
                    controls=[
                        ft.Text("SHARE OF SESSION DETECTIONS", size=10, color=Palette.TEXT_MUTED),
                        ft.Container(expand=True),
                        self._dist_total,
                    ],
                ),
            ],
            spacing=6,
        )
        self._dist_card = section_card(
            "Crack Distribution",
            body,
            icon=ft.Icon(ft.Icons.BAR_CHART, size=16, color=Palette.TEXT_MUTED),
        )
        return self._dist_card

    def build_severity(self) -> ft.Control:
        if self._sev_card is not None:
            return self._sev_card
        rows = []
        for label in ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            row, rec = self._new_row(label, severity_color(label))
            self._sev[label] = rec
            rows.append(row)

        self._sev_total = ft.Text(
            "0 samples",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
        body = ft.Column(
            controls=[
                *rows,
                ft.Row(
                    controls=[
                        ft.Text("SHARE OF ALL SAMPLES", size=10, color=Palette.TEXT_MUTED),
                        ft.Container(expand=True),
                        self._sev_total,
                    ],
                ),
            ],
            spacing=6,
        )
        self._sev_card = section_card(
            "Severity Distribution",
            body,
            icon=ft.Icon(ft.Icons.DONUT_LARGE, size=16, color=Palette.TEXT_MUTED),
        )
        return self._sev_card

    def update(self) -> None:
        stats = self.controller.get_stats()
        total = stats["total"]
        for label, key in [
            ("Small", "small"),
            ("Medium", "medium"),
            ("Large", "large"),
            ("Broken", "broken"),
        ]:
            rec = self._dist.get(label)
            if rec is None:
                continue
            value = stats[key]
            ratio = (value / total) if total else 0.0
            rec["value"].value = str(value)
            rec["pct"].value = f"{ratio * 100:.0f}%"
            rec["bar"].value = ratio
        if self._dist_total is not None:
            self._dist_total.value = f"{total} total"

        severity_counts = self.controller.get_severity_counts()
        samples = sum(severity_counts.values())
        for label in ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            rec = self._sev.get(label)
            if rec is None:
                continue
            value = severity_counts.get(label, 0)
            ratio = (value / samples) if samples else 0.0
            rec["value"].value = str(value)
            rec["pct"].value = f"{ratio * 100:.0f}%"
            rec["bar"].value = ratio
        if self._sev_total is not None:
            self._sev_total.value = f"{samples} samples"
