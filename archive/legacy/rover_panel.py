# ARCHIVED — older rover control card, never mounted. The active component is
# ui/components/rover_control_card.py. Kept for reference only.
import flet as ft

import config
from ui.theme import Palette
from ui.components.base import section_card


class RoverPanel:
    def __init__(self, controller) -> None:
        self.controller = controller
        self.status_text = ft.Text("ESP32 OFFLINE", size=11, weight=ft.FontWeight.BOLD, color=Palette.DANGER)
        self.status_pill = ft.Container(
            padding=ft.padding.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=Palette.DANGER + "1F",
            border_radius=20,
            content=ft.Row(
                controls=[
                    ft.Container(width=8, height=8, border_radius=4, bgcolor=Palette.DANGER),
                    self.status_text,
                ],
                spacing=6,
                tight=True,
            ),
        )
        self.ip_text = ft.Text("—", size=11, color=Palette.TEXT_MUTED)
        self.error_text = ft.Text("", size=10, color=Palette.TEXT_MUTED, visible=False)

        self.speed_slider = ft.Slider(
            min=0,
            max=255,
            divisions=255,
            value=config.ESP32_DEFAULT_SPEED,
            label="{value}",
            on_change=self._on_speed_change,
        )
        self.speed_value = ft.Text(
            str(config.ESP32_DEFAULT_SPEED),
            size=22,
            weight=ft.FontWeight.BOLD,
            color=Palette.PRIMARY,
        )

    def build(self) -> ft.Control:
        dpad = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self._spacer(),
                        self._dir_button(ft.Icons.ARROW_UPWARD, self.controller.esp_forward, "Forward"),
                        self._spacer(),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        self._dir_button(ft.Icons.ARROW_BACK, self.controller.esp_stop, "Left"),
                        self._stop_button(),
                        self._dir_button(ft.Icons.ARROW_FORWARD, self.controller.esp_stop, "Right"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                ft.Row(
                    controls=[
                        self._spacer(),
                        self._dir_button(ft.Icons.ARROW_DOWNWARD, self.controller.esp_backward, "Backward"),
                        self._spacer(),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                ),
            ],
            spacing=10,
        )

        speed_panel = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("SPEED", size=11, color=Palette.TEXT_MUTED),
                        ft.Container(expand=True),
                        self.speed_value,
                    ],
                ),
                self.speed_slider,
                ft.Row(
                    controls=[
                        self._preset_button("Slow", 80),
                        self._preset_button("Medium", 150),
                        self._preset_button("Fast", 220),
                    ],
                    spacing=8,
                ),
                ft.Container(height=4),
                ft.FilledButton(
                    "EMERGENCY STOP",
                    icon=ft.Icons.SOS,
                    bgcolor=Palette.DANGER,
                    color=ft.Colors.WHITE,
                    height=48,
                    on_click=lambda e: self.controller.esp_emergency_stop(),
                ),
            ],
            spacing=6,
            expand=True,
        )

        body = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        self.status_pill,
                        ft.Container(width=8),
                        ft.Icon(ft.Icons.LAN_OUTLINED, size=14, color=Palette.TEXT_MUTED),
                        self.ip_text,
                        ft.Container(expand=True),
                        self.error_text,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[dpad, speed_panel],
                    spacing=24,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=14,
        )

        return section_card(
            "Rover Control",
            body,
            icon=ft.Icon(ft.Icons.ROBOT_OUTLINED, size=16, color=Palette.TEXT_MUTED),
        )

    def refresh(self, status: dict) -> None:
        online = status.get("online", False)
        error = status.get("last_error")
        self.status_text.value = "ESP32 ONLINE" if online else "ESP32 OFFLINE"
        self.status_text.color = Palette.SUCCESS if online else Palette.DANGER
        self.status_pill.bgcolor = (Palette.SUCCESS if online else Palette.DANGER) + "1F"
        self.status_pill.content.controls[0].bgcolor = (
            Palette.SUCCESS if online else Palette.DANGER
        )
        self.ip_text.value = status.get("ip", "—")
        if not online and error:
            self.error_text.value = str(error)[:44]
            self.error_text.visible = True
        else:
            self.error_text.visible = False

    def _dir_button(self, icon, on_click, tooltip: str) -> ft.IconButton:
        return ft.IconButton(
            icon=ft.Icon(icon, size=28, color=Palette.PRIMARY),
            icon_size=28,
            width=64,
            height=64,
            bgcolor=Palette.SURFACE_ALT,
            style=ft.ButtonStyle(shape=ft.CircleBorder(), side=ft.BorderSide(1, Palette.BORDER)),
            tooltip=tooltip,
            on_click=lambda e: on_click(),
        )

    def _stop_button(self) -> ft.IconButton:
        return ft.IconButton(
            icon=ft.Icon(ft.Icons.STOP, size=32, color=Palette.BLACK),
            icon_size=32,
            width=72,
            height=72,
            bgcolor=Palette.WARNING,
            style=ft.ButtonStyle(shape=ft.CircleBorder()),
            tooltip="Stop",
            on_click=lambda e: self.controller.esp_stop(),
        )

    def _spacer(self) -> ft.Container:
        return ft.Container(width=64, height=64)

    def _preset_button(self, label: str, speed: int) -> ft.FilledTonalButton:
        return ft.FilledTonalButton(
            label,
            on_click=lambda e: self._apply_speed(speed),
            style=ft.ButtonStyle(bgcolor=Palette.SURFACE_ALT, side=ft.BorderSide(1, Palette.BORDER)),
        )

    def _apply_speed(self, speed: int) -> None:
        self.speed_slider.value = speed
        self.speed_value.value = str(speed)
        self.controller.esp_set_speed(speed)

    def _on_speed_change(self, event) -> None:
        speed = int(event.control.value)
        self.speed_value.value = str(speed)
        self.controller.esp_set_speed(speed)
