"""
GSM Card UI Component
"""
import flet as ft
from typing import Optional, Callable

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


class GSMCard:
    """GSM/SMS control card UI component"""
    
    def __init__(
        self,
        on_send_sms: Optional[Callable] = None,
        on_test_sms: Optional[Callable] = None,
        default_phone: str = "",
        controller=None
    ):
        self.on_send_sms = on_send_sms
        self.on_test_sms = on_test_sms

        self.controller = controller
        self._phone_input = None
        self._message_input = None
        self._status_text = None
        self._conn_pill = None

        self._default_phone = default_phone
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI components"""
        pass
    
    def update(self) -> None:
        """Refresh the connection indicator live from the controller."""
        if self.controller is None or self._conn_pill is None:
            return
        try:
            online = self.controller.get_esp_status().get("online", False)
        except Exception:
            online = False
        if online:
            self._conn_pill.value = "● ONLINE"
            self._conn_pill.color = ft.Colors.GREEN_400
        else:
            self._conn_pill.value = "● OFFLINE"
            self._conn_pill.color = ft.Colors.RED_400
    
    def _build_sms_form(self) -> ft.Container:
        """Build SMS sending form"""
        
        self._phone_input = ft.TextField(
            label="Phone Number",
            hint_text="Enter phone number",
            value=self._default_phone,
            expand=True,
            border_color=Palette.BORDER,
            focused_border_color=Palette.INFO,
            text_style=ft.TextStyle(color=Palette.TEXT),
            label_style=ft.TextStyle(color=Palette.TEXT_MUTED),
            prefix_icon=ft.icons.Icons.PHONE,
        )
        
        self._message_input = ft.TextField(
            label="Message",
            hint_text="Enter SMS message",
            multiline=True,
            min_lines=1,
            max_lines=1,
            expand=True,
            border_color=Palette.BORDER,
            focused_border_color=Palette.INFO,
            text_style=ft.TextStyle(color=Palette.TEXT),
            label_style=ft.TextStyle(color=Palette.TEXT_MUTED),
            prefix_icon=ft.icons.Icons.MESSAGE,
        )
        
        self._status_text = ft.Text(
            value="Ready",
            size=12,
            color=Palette.TEXT_MUTED,
        )

        self._conn_pill = ft.Text(
            value="● OFFLINE",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.RED_400,
        )
        
        # Send buttons
        send_btn = ft.ElevatedButton(
            "Send SMS",
            icon=ft.icons.Icons.SEND,
            on_click=lambda e: self._on_send(),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_700,
                color=ft.Colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_INNER),
            ),
        )
        
        test_btn = ft.OutlinedButton(
            "Send Test",
            icon=ft.icons.Icons.SCIENCE,
            on_click=lambda e: self._on_test(),
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, Palette.BORDER),
                color=Palette.TEXT_MUTED,
                shape=ft.RoundedRectangleBorder(radius=RADIUS_INNER),
            ),
        )
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.ResponsiveRow(
                        spacing=SPACE_SM,
                        run_spacing=SPACE_SM,
                        controls=[
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=self._phone_input,
                            ),
                            ft.Container(
                                col={"xs": 12, "sm": 6},
                                content=self._message_input,
                            ),
                        ],
                    ),
                    ft.Row(
                        controls=[send_btn, test_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=SPACE_MD,
                        wrap=True,
                    ),
                    self._status_text,
                ],
                spacing=SPACE_SM,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            ),
            padding=ft.padding.Padding.all(SPACE_MD),
            bgcolor=Palette.SURFACE_ALT,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_INNER,
        )
    
    def build(self) -> ft.Container:
        """Build the complete GSM card"""

        main_content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "📱 SMS Control",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=Palette.INFO,
                        ),
                        ft.Container(expand=True),
                        self._conn_pill,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=5, color=Palette.BORDER),
                self._build_sms_form(),
            ],
            spacing=SPACE_XS,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        return ft.Container(
            content=main_content,
            padding=ft.padding.Padding.all(PADDING_CARD),
            bgcolor=Palette.SURFACE,
            border=border_all(Palette.BORDER),
            border_radius=RADIUS_CARD,
            shadow=CARD_SHADOW,
        )
    
    # ==================== Event Handlers ====================
    
    def _on_send(self):
        phone = self._phone_input.value if self._phone_input else ""
        message = self._message_input.value if self._message_input else ""
        
        if not phone or not message:
            self._status_text.value = "❌ Phone and message required"
            self._status_text.color = ft.Colors.RED_400
            return
        
        if self.on_send_sms:
            success = self.on_send_sms(phone, message)
            if success:
                self._status_text.value = "✅ SMS sent successfully!"
                self._status_text.color = ft.Colors.GREEN_400
                if self._message_input:
                    self._message_input.value = ""
            else:
                self._status_text.value = "❌ Failed to send SMS"
                self._status_text.color = ft.Colors.RED_400
    
    def _on_test(self):
        if self.on_test_sms:
            success = self.on_test_sms()
            if success:
                self._status_text.value = "✅ Test SMS sent successfully!"
                self._status_text.color = ft.Colors.GREEN_400
            else:
                self._status_text.value = "❌ Failed to send test SMS"
                self._status_text.color = ft.Colors.RED_400
