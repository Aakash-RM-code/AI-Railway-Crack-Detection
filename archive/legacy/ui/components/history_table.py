import os

import flet as ft

from config import HISTORY_CSV
from ui.theme import Palette, crack_type_color
from ui.components.base import section_card

MAX_ROWS = 10


class HistoryTable:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._rows = []
        self._seen = set()
        self._last_sig = None
        self._csv_path = HISTORY_CSV

    def _csv_signature(self):
        """Cheap (mtime, size) fingerprint of the CSV — no content read."""
        try:
            st = os.stat(self._csv_path)
            return (st.st_mtime_ns, st.st_size)
        except OSError:
            return None

    def _row_key(self, row) -> tuple:
        return (
            row.get("time", ""),
            row.get("crack_type", ""),
            row.get("confidence", 0),
        )

    def _make_row(self, row: dict) -> ft.DataRow:
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(row["time"], size=12, color=Palette.TEXT_MUTED)),
                ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=8,
                                height=8,
                                border_radius=4,
                                bgcolor=crack_type_color(row["crack_type"]),
                            ),
                            ft.Text(
                                row["crack_type"],
                                size=12,
                                color=Palette.TEXT,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=8,
                    )
                ),
                ft.DataCell(
                    ft.Text(
                        f"{row['confidence']:.0%}",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=Palette.TEXT,
                    )
                ),
                ft.DataCell(
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.IMAGE_OUTLINED, size=14, color=Palette.TEXT_MUTED),
                            ft.Text(row["image"], size=11, color=Palette.TEXT_MUTED),
                        ],
                        spacing=6,
                    )
                ),
            ]
        )

    def build(self) -> ft.Control:
        # The table owns its own internal scroll area: `height` keeps the card
        # bounded (so the dashboard body scroll stays predictable) while the
        # DataTable scrolls its rows internally. No extra scroll wrapper, which
        # removes the previous nested horizontal scrollbar.
        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("TIME", size=11, color=Palette.TEXT_MUTED)),
                ft.DataColumn(ft.Text("CRACK TYPE", size=11, color=Palette.TEXT_MUTED)),
                ft.DataColumn(ft.Text("CONFIDENCE", size=11, color=Palette.TEXT_MUTED)),
                ft.DataColumn(ft.Text("IMAGE", size=11, color=Palette.TEXT_MUTED)),
            ],
            rows=self._rows,
            heading_row_color=Palette.SURFACE_ALT,
            heading_row_height=38,
            data_row_min_height=36,
            data_row_max_height=36,
            column_spacing=20,
            divider_thickness=0,
            horizontal_margin=4,
            height=280,
        )

        return section_card(
            "Detection History",
            table,
            icon=ft.Icon(ft.Icons.TABLE_CHART_OUTLINED, size=16, color=Palette.TEXT_MUTED),
            trailing=ft.Text("LAST 10 EVENTS", size=10, color=Palette.TEXT_MUTED),
        )

    def update(self) -> None:
        sig = self._csv_signature()
        if sig is None or sig == self._last_sig:
            return
        self._last_sig = sig

        rows = self.controller.get_history(limit=MAX_ROWS)
        for row in rows:
            key = self._row_key(row)
            if key in self._seen:
                continue
            self._seen.add(key)
            self._rows.append(self._make_row(row))

        if len(self._rows) > MAX_ROWS:
            del self._rows[:-MAX_ROWS]
            self._seen = {self._row_key(r) for r in rows}
