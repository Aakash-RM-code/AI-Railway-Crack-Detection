import flet as ft

from ui.theme import Palette
from ui.components.base import section_card


class SnapshotCard:
    def __init__(self, controller) -> None:
        self.controller = controller
        self._image = None
        self._placeholder = None
        self._build_ui()

    def _build_ui(self):
        self._placeholder = ft.Container(
            expand=True,
            bgcolor="#0A0E14",
            border_radius=10,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=48, color=Palette.BORDER),
                    ft.Text("NO SNAPSHOT CAPTURED", size=12, color=Palette.TEXT_MUTED),
                    ft.Text("Latest flagged detection will appear here", size=11, color=Palette.BORDER),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def update(self):
        snapshot_base64 = self.controller.get_latest_snapshot()
        if snapshot_base64:
            if self._image is None:
                self._image = ft.Image(
                    src="data:image/jpeg;base64," + snapshot_base64,
                    fit=ft.BoxFit.CONTAIN,
                    expand=True,
                    border_radius=10,
                )
                self._placeholder.content = self._image
            else:
                self._image.src = "data:image/jpeg;base64," + snapshot_base64
            self._placeholder.visible = True
        else:
            if self._image is not None:
                self._placeholder.content = ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.IMAGE_NOT_SUPPORTED_OUTLINED, size=48, color=Palette.BORDER),
                        ft.Text("NO SNAPSHOT CAPTURED", size=12, color=Palette.TEXT_MUTED),
                        ft.Text("Latest flagged detection will appear here", size=11, color=Palette.BORDER),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
                self._image = None
            self._placeholder.visible = True

    def build(self, compact: bool = False) -> ft.Control:
        body = self._placeholder
        if compact:
            # Scale the snapshot preview proportionally to its width so it
            # never overflows or collapses on narrow screens.
            body = ft.Container(aspect_ratio=1.333, content=self._placeholder)
        return section_card(
            "Latest Snapshot",
            body,
            height=None if compact else 200,
            icon=ft.Icon(ft.Icons.PHOTO_CAMERA_OUTLINED, size=16, color=Palette.TEXT_MUTED),
        )
