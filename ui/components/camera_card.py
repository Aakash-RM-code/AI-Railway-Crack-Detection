import flet as ft

from ui.theme import Palette, border_all

SOURCE_LABELS = {
    "usb": "USB Camera",
    "esp32cam": "ESP32-CAM",
    "demo": "Video File",
}


class CameraCard:
    def __init__(self, controller, on_browse_video=None) -> None:
        self.controller = controller
        self.on_browse_video = on_browse_video
        self._picker_open = False

        self.source_select = ft.SegmentedButton(
            segments=[
                ft.Segment(value="usb", icon=ft.Icons.CAMERA_ALT, label="USB Camera"),
                ft.Segment(value="esp32cam", icon=ft.Icons.SURROUND_SOUND, label="ESP32-CAM"),
                ft.Segment(value="demo", icon=ft.Icons.VIDEO_LIBRARY, label="Video File"),
            ],
            selected=[self.controller.get_camera_source()],
            show_selected_icon=False,
            expand=True,
            on_change=self._on_source_select,
        )
        self.start_btn = ft.FilledButton(
            "Start Inspection",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_start,
        )
        self.stop_btn = ft.OutlinedButton(
            "Stop Inspection",
            icon=ft.Icons.STOP,
            disabled=True,
            on_click=self._on_stop,
        )
        self.browse_btn = ft.OutlinedButton(
            "Browse Video",
            icon=ft.Icons.VIDEO_FILE,
            visible=False,
            on_click=self._on_browse,
        )
        self.reconnect_btn = ft.OutlinedButton(
            "Reconnect",
            icon=ft.Icons.REFRESH,
            visible=False,
            on_click=self._on_reconnect,
        )
        self.fps_text = ft.Text("FPS --", size=11, color=Palette.TEXT)
        self.res_text = ft.Text("--", size=11, color=Palette.TEXT)
        self.status_icon = ft.Icon(
            ft.Icons.RADIO_BUTTON_UNCHECKED, size=12, color=Palette.WARNING
        )
        self.status_text = ft.Text(
            "STANDBY", size=11, weight=ft.FontWeight.BOLD, color=Palette.WARNING
        )
        self.status = ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=Palette.WARNING + "1F",
            border_radius=20,
            content=ft.Row(controls=[self.status_icon, self.status_text], spacing=6, tight=True),
        )
        self.camera_text = ft.Text("Camera not started", size=11, color=Palette.TEXT_MUTED)
        self.image = ft.Image(
            src="",
            fit=ft.BoxFit.CONTAIN,
            expand=True,
            border_radius=10,
            visible=False,
        )

    def _build_source_select(self, compact: bool = False) -> ft.SegmentedButton:
        if compact:
            labels = ("USB", "ESP32-CAM", "Video")
        else:
            labels = ("USB Camera", "ESP32-CAM", "Video File")
        return ft.SegmentedButton(
            segments=[
                ft.Segment(value="usb", icon=ft.Icons.CAMERA_ALT, label=labels[0]),
                ft.Segment(value="esp32cam", icon=ft.Icons.SURROUND_SOUND, label=labels[1]),
                ft.Segment(value="demo", icon=ft.Icons.VIDEO_LIBRARY, label=labels[2]),
            ],
            selected=[self.controller.get_camera_source()],
            show_selected_icon=False,
            expand=True,
            on_change=self._on_source_select,
        )

    def build(self, compact: bool = False) -> ft.Control:
        self.source_select = self._build_source_select(compact)

        placeholder = ft.Container(
            expand=True,
            bgcolor="#0A0E14",
            border_radius=10,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.VIDEOCAM_OUTLINED, size=52, color=Palette.BORDER),
                    ft.Text(
                        "CAMERA FEED",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=Palette.TEXT_MUTED,
                    ),
                    ft.Text(
                        "Press Start Inspection to begin",
                        size=11,
                        color=Palette.BORDER,
                    ),
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        fps_badge = ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=8, vertical=4),
            bgcolor="#66000000",
            border_radius=8,
            content=self.fps_text,
        )
        res_badge = ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=8, vertical=4),
            bgcolor="#66000000",
            border_radius=8,
            content=self.res_text,
        )

        preview_stack = ft.Stack(
            controls=[
                placeholder,
                self.image,
                ft.Container(content=fps_badge, left=12, top=12),
                ft.Container(content=res_badge, right=12, top=12),
                ft.Container(content=self.status, left=12, bottom=12),
            ],
            expand=True,
        )

        source_panel = ft.Container(
            bgcolor="#0D1117",
            border=border_all(Palette.BORDER),
            border_radius=10,
            padding=ft.padding.Padding.symmetric(horizontal=12, vertical=10),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PHOTO_CAMERA, size=13, color=Palette.TEXT_MUTED),
                            ft.Text("CAMERA SOURCE", size=11, color=Palette.TEXT_MUTED),
                            ft.Container(expand=True),
                            ft.Text(
                                "switch sources without restart",
                                size=10,
                                color=Palette.BORDER,
                            ),
                        ],
                        spacing=6,
                    ),
                    self.source_select,
                    ft.Row(
                        controls=[
                            self.browse_btn,
                            self.reconnect_btn,
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                ],
                spacing=8,
            ),
        )

        # Preview scales proportionally to its width on small screens and
        # fills the remaining column height on large screens.
        if compact:
            preview_wrap = ft.Container(aspect_ratio=1.333, content=preview_stack)
        else:
            preview_wrap = ft.Container(expand=True, content=preview_stack)

        controls_row = ft.ResponsiveRow(
            spacing=8,
            run_spacing=8,
            controls=[
                ft.Container(
                    col={"xs": 12, "md": 8},
                    content=ft.Row(
                        controls=[
                            self.start_btn,
                            self.stop_btn,
                        ],
                        spacing=8,
                        wrap=True,
                    ),
                ),
                ft.Container(
                    col={"xs": 12, "md": 4},
                    content=ft.Row(
                        controls=[
                            ft.Container(expand=True),
                            self.camera_text,
                        ],
                        spacing=8,
                    ),
                ),
            ],
        )

        return ft.Container(
            expand=not compact,
            bgcolor=Palette.SURFACE,
            border=border_all(Palette.BORDER),
            border_radius=14,
            shadow=ft.BoxShadow(blur_radius=14, color="#26000000", offset=ft.Offset(0, 4)),
            padding=ft.padding.Padding.all(14),
            content=ft.Column(
                expand=not compact,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.VIDEOCAM, size=16, color=Palette.TEXT_MUTED),
                            ft.Text("LIVE CAMERA", size=12, color=Palette.TEXT_MUTED),
                            ft.Container(expand=True),
                            ft.Text("CAM 01", size=11, color=Palette.TEXT_MUTED),
                        ],
                        spacing=8,
                    ),
                    source_panel,
                    preview_wrap,
                    controls_row,
                ],
                spacing=10,
            ),
        )

    def update_frame(self, frame_base64: str) -> None:
        if not self.image.visible:
            self.image.visible = True
        self.image.src = "data:image/jpeg;base64," + frame_base64

    def _sync_buttons(self) -> None:
        mode = self.controller.get_camera_source()
        self.browse_btn.visible = mode == "demo"
        self.reconnect_btn.visible = mode == "esp32cam"
        running = self.controller.is_running()
        self.start_btn.disabled = running
        self.stop_btn.disabled = not running

    def _resync_selected(self) -> None:
        mode = self.controller.get_camera_source()
        if self.source_select.selected != [mode]:
            self.source_select.selected = [mode]
            self.source_select.update()

    def update_from_controller(self) -> None:
        frame_base64 = self.controller.get_frame_base64()
        if frame_base64:
            self.update_frame(frame_base64)
        fps = self.controller.get_fps()
        resolution = self.controller.get_resolution()
        error = self.controller.camera_error()
        running = self.controller.is_running()
        info = self.controller.get_camera_info()
        if not self._picker_open and self.source_select.selected != [info["mode"]]:
            self.source_select.selected = [info["mode"]]
        self._sync_buttons()
        self.refresh(running, fps, resolution, error)

    def refresh(self, running: bool, fps: float, resolution: str, error: str | None) -> None:
        label = SOURCE_LABELS.get(self.controller.get_camera_source(), "Camera")
        if running:
            self.fps_text.value = f"FPS {fps:.1f}"
            self.res_text.value = resolution
            self.status_icon.name = ft.Icons.RADIO_BUTTON_CHECKED
            self.status_icon.color = Palette.SUCCESS
            self.status_text.value = "RUNNING"
            self.status_text.color = Palette.SUCCESS
            self.status.bgcolor = Palette.SUCCESS + "1F"
            self.camera_text.value = f"{label} · inspection active"
        else:
            self.fps_text.value = "FPS --"
            self.res_text.value = "--"
            self.status_icon.name = ft.Icons.RADIO_BUTTON_UNCHECKED
            self.status_icon.color = Palette.WARNING
            self.status_text.value = "STANDBY"
            self.status_text.color = Palette.WARNING
            self.status.bgcolor = Palette.WARNING + "1F"
            self.camera_text.value = error or f"{label} · camera not started"

    # ==================== source panel handlers ====================

    async def _on_source_select(self, event) -> None:
        selected = getattr(event.control, "selected", None)
        mode = (selected or [None])[0]
        if not mode:
            self._resync_selected()
            return
        await self._apply_source(mode)

    async def _apply_source(self, mode: str) -> None:
        if mode == "demo":
            await self._open_video_picker()
            return
        self.controller.set_camera_source(mode)
        if not self.controller.is_running():
            self.controller.start()
        self._resync_selected()
        self._sync_buttons()
        self.start_btn.update()
        self.stop_btn.update()

    async def _open_video_picker(self) -> None:
        if not self.on_browse_video:
            self._resync_selected()
            return
        self._picker_open = True
        try:
            await self.on_browse_video()
        finally:
            self._picker_open = False
        self._resync_selected()
        self._sync_buttons()

    def _on_start(self, event) -> None:
        self.controller.start()
        self._sync_buttons()
        self.start_btn.update()
        self.stop_btn.update()

    def _on_stop(self, event) -> None:
        self.controller.stop()
        self._sync_buttons()
        self.start_btn.update()
        self.stop_btn.update()

    async def _on_browse(self, event) -> None:
        await self._open_video_picker()

    def _on_reconnect(self, event) -> None:
        self.controller.reconnect_camera()
