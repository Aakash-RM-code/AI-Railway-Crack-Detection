"""
Rover Control Card UI Component
Compact industrial control panel with direction controls, speed slider, and emergency stop
"""
import flet as ft
from typing import Optional, Callable
from datetime import datetime

from config import SPEED_SLOW, SPEED_MEDIUM, SPEED_FAST, MIN_SPEED, MAX_SPEED

from ui.theme import (
    Palette,
    CARD_SHADOW,
    border_all,
    SPACE_XS,
    SPACE_SM,
    SPACE_MD,
    PADDING_CARD,
    RADIUS_CARD,
    RADIUS_INNER,
)


class RoverControlCard:
    """Industrial rover control panel UI component (responsive layout)"""

    def __init__(
        self,
        on_forward: Optional[Callable] = None,
        on_backward: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        on_speed_change: Optional[Callable] = None,
        on_emergency_stop: Optional[Callable] = None
    ):
        self.on_forward = on_forward
        self.on_backward = on_backward
        self.on_stop = on_stop
        self.on_speed_change = on_speed_change
        self.on_emergency_stop = on_emergency_stop

        # UI elements
        self._speed_value_text = None
        self._status_text = None
        self._ip_text = None
        self._last_update_text = None
        self._speed_slider = None
        self._speed_hint = None

        # State
        self._current_speed = 150
        self._is_online = False
        self._direction = "STOP"
        self._moving = False

        # Build UI
        self._build_ui()

    def _build_ui(self):
        """Create the shared state text widgets."""
        self._status_text = ft.Text(
            value="● Offline",
            size=12,
            color=Palette.DANGER,
            weight=ft.FontWeight.BOLD,
        )
        self._ip_text = ft.Text(
            value="IP: --",
            size=11,
            color=Palette.TEXT_MUTED,
        )
        self._last_update_text = ft.Text(
            value="Last Update: --",
            size=11,
            color=Palette.TEXT_MUTED,
        )
        self._speed_value_text = ft.Text(
            value="150",
            size=18,
            weight=ft.FontWeight.BOLD,
            color=Palette.INFO,
        )
        self._speed_slider = ft.Slider(
            min=MIN_SPEED,
            max=MAX_SPEED,
            value=self._current_speed,
            label="{value}",
            on_change=self._on_speed_slider_change,
            active_color=Palette.INFO,
            inactive_color=Palette.BORDER,
            thumb_color=ft.Colors.CYAN_300,
            height=40,
        )
        self._speed_hint = ft.Text(
            value="● Disconnected",
            size=10,
            color=Palette.DANGER,
        )

    def _pad_button(self, icon, bgcolor, overlay, tooltip, on_click) -> ft.IconButton:
        return ft.IconButton(
            icon=icon,
            icon_size=22,
            icon_color="white",
            tooltip=tooltip,
            on_click=on_click,
            width=44,
            height=44,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS_INNER - 2),
                bgcolor=bgcolor,
                overlay_color=overlay,
                padding=ft.Padding.all(4),
            ),
        )

    def _build_direction_controls(self) -> ft.Container:
        """Compact directional pad."""
        forward_btn = self._pad_button(
            ft.icons.Icons.ARROW_UPWARD, ft.Colors.GREEN_700, ft.Colors.GREEN_400,
            "Forward", lambda e: self._on_forward(),
        )
        stop_btn = self._pad_button(
            ft.icons.Icons.STOP, ft.Colors.RED_700, ft.Colors.RED_400,
            "Stop", lambda e: self._on_stop(),
        )
        backward_btn = self._pad_button(
            ft.icons.Icons.ARROW_DOWNWARD, ft.Colors.ORANGE_700, ft.Colors.ORANGE_400,
            "Backward", lambda e: self._on_backward(),
        )
        left_btn = self._pad_button(
            ft.icons.Icons.ARROW_LEFT, ft.Colors.GREY_800, ft.Colors.GREY_600,
            "Left (disabled)", lambda e: None,
        )
        left_btn.disabled = True
        right_btn = self._pad_button(
            ft.icons.Icons.ARROW_RIGHT, ft.Colors.GREY_800, ft.Colors.GREY_600,
            "Right (disabled)", lambda e: None,
        )
        right_btn.disabled = True

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(controls=[forward_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    ft.Row(controls=[left_btn, stop_btn, right_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                    ft.Row(controls=[backward_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.all(6),
            bgcolor=Palette.SURFACE_ALT,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_INNER,
        )

    def _build_speed_controls(self) -> ft.Container:
        """Compact speed slider with preset buttons."""
        slow_btn = self._pad_button(
            ft.icons.Icons.SLOW_MOTION_VIDEO, ft.Colors.BLUE_700, ft.Colors.BLUE_400,
            f"Slow ({SPEED_SLOW})", lambda e: self._set_speed_preset(SPEED_SLOW),
        )
        medium_btn = self._pad_button(
            ft.icons.Icons.SPEED, ft.Colors.GREEN_700, ft.Colors.GREEN_400,
            f"Medium ({SPEED_MEDIUM})", lambda e: self._set_speed_preset(SPEED_MEDIUM),
        )
        fast_btn = self._pad_button(
            ft.icons.Icons.ROCKET, ft.Colors.RED_700, ft.Colors.RED_400,
            f"Fast ({SPEED_FAST})", lambda e: self._set_speed_preset(SPEED_FAST),
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Speed:", size=12, weight=ft.FontWeight.BOLD, color=Palette.TEXT),
                            ft.Container(expand=True),
                            self._speed_value_text,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    self._speed_slider,
                    ft.Row(
                        controls=[slow_btn, medium_btn, fast_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=SPACE_MD,
                    ),
                    self._speed_hint,
                ],
                spacing=SPACE_XS,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.Padding.all(6),
            bgcolor=Palette.SURFACE_ALT,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_INNER,
        )

    def _build_emergency_stop(self) -> ft.Container:
        """Compact emergency stop button."""
        emergency_btn = ft.IconButton(
            icon=ft.icons.Icons.WARNING,
            icon_size=30,
            icon_color="white",
            tooltip="EMERGENCY STOP",
            on_click=lambda e: self._on_emergency_stop(),
            width=56,
            height=56,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=RADIUS_INNER),
                bgcolor=Palette.DANGER,
                overlay_color=Palette.DANGER + "66",
                padding=ft.Padding.all(8),
            ),
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "EMERGENCY\nSTOP",
                        size=9,
                        weight=ft.FontWeight.BOLD,
                        color=Palette.DANGER,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    emergency_btn,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=SPACE_XS,
            ),
            padding=ft.Padding.all(6),
            bgcolor=Palette.SURFACE_ALT,
            border=border_all(Palette.DANGER),
            border_radius=RADIUS_INNER,
        )

    def build(self) -> ft.Container:
        """Build the complete control card.

        The direction pad, emergency stop and speed controls live in a nested
        ResponsiveRow that adapts to the *card's own width*: stacked on the
        narrowest widths, side-by-side on wider ones. Breakpoints beyond 'md'
        are unnecessary because the card never exceeds tablet width inside the
        dashboard's right-hand rail.
        """
        controls_area = ft.ResponsiveRow(
            spacing=SPACE_MD,
            run_spacing=SPACE_MD,
            controls=[
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    content=self._build_direction_controls(),
                ),
                ft.Container(
                    col={"xs": 12, "sm": 6, "md": 4},
                    content=self._build_emergency_stop(),
                ),
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 4},
                    content=self._build_speed_controls(),
                ),
            ],
        )

        main_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "🤖 Rover Control",
                            size=15,
                            weight=ft.FontWeight.BOLD,
                            color=Palette.INFO,
                        ),
                        ft.Container(expand=True),
                        self._status_text,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        self._ip_text,
                        ft.Container(expand=True),
                        self._last_update_text,
                    ],
                ),
                controls_area,
            ],
            spacing=SPACE_SM,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        return ft.Container(
            content=main_content,
            padding=ft.Padding.all(PADDING_CARD),
            bgcolor=Palette.SURFACE,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_CARD,
            shadow=CARD_SHADOW,
        )

    # ==================== Event Handlers ====================

    def _on_forward(self):
        if self.on_forward:
            self.on_forward()

    def _on_backward(self):
        if self.on_backward:
            self.on_backward()

    def _on_stop(self):
        if self.on_stop:
            self.on_stop()

    def _on_speed_slider_change(self, e):
        speed = int(e.control.value)
        self._current_speed = speed
        self._speed_value_text.value = str(speed)
        self._speed_value_text.update()
        if self.on_speed_change:
            self.on_speed_change(speed)

    def _set_speed_preset(self, speed: int):
        self._current_speed = speed
        self._speed_slider.value = speed
        self._speed_slider.update()
        self._speed_value_text.value = str(speed)
        self._speed_value_text.update()
        if self.on_speed_change:
            self.on_speed_change(speed)

    def _on_emergency_stop(self):
        if self.on_emergency_stop:
            self.on_emergency_stop()

    # ==================== UI Updates ====================

    def update_status(self, state: dict):
        """Update UI with new state from controller"""
        self._is_online = state.get('online', False)
        self._direction = state.get('direction', 'STOP')
        self._moving = state.get('moving', False)
        speed = state.get('speed', self._current_speed)
        ip = state.get('ip', '--')
        last_update = state.get('last_update')

        # Update status
        if self._is_online:
            self._status_text.value = "● Online"
            self._status_text.color = ft.Colors.GREEN_400
            self._speed_hint.value = "● Synced with ESP32"
            self._speed_hint.color = ft.Colors.GREEN_400
        else:
            self._status_text.value = "● Offline"
            self._status_text.color = ft.Colors.RED_400
            self._speed_hint.value = "● Disconnected — local preview only"
            self._speed_hint.color = ft.Colors.RED_400

        # Update IP
        self._ip_text.value = f"IP: {ip}" if ip else "IP: --"

        # Update last update time
        if last_update:
            self._last_update_text.value = f"Last Update: {last_update.strftime('%H:%M:%S')}"
        else:
            self._last_update_text.value = "Last Update: --"

        # Update speed
        self._current_speed = speed
        if self._speed_slider:
            self._speed_slider.value = speed
        if self._speed_value_text:
            self._speed_value_text.value = str(speed)

    def update_from_controller(self, controller) -> None:
        """Read status directly from controller and update UI"""
        status = controller.get_esp_status()
        self._is_online = status.get('online', False)
        self._ip_text.value = f"IP: {status.get('ip', '--')}" if status.get('ip') else "IP: --"
        self._last_update_text.value = f"Last Update: {datetime.now().strftime('%H:%M:%S')}"

        if self._is_online:
            self._status_text.value = "● Online"
            self._status_text.color = ft.Colors.GREEN_400
            self._speed_hint.value = "● Synced with ESP32"
            self._speed_hint.color = ft.Colors.GREEN_400
        else:
            self._status_text.value = "● Offline"
            self._status_text.color = ft.Colors.RED_400
            self._speed_hint.value = "● Disconnected — local preview only"
            self._speed_hint.color = ft.Colors.RED_400
