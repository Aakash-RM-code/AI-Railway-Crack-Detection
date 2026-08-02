import flet as ft
import threading
import time
import os

import config

from ui.theme import Palette, configure_page
from ui.components.header import Header
from ui.components.footer import Footer
from ui.components.camera_card import CameraCard
from ui.components.alert_card import AlertCard
from ui.components.statistics_card import StatisticsCard
from ui.components.history_table import HistoryTable
from ui.components.snapshot_card import SnapshotCard
from ui.components.gps_card import GPSCard
from ui.components.gsm_card import GSMCard
from ui.components.health_card import HealthCard
from ui.components.analytics import AnalyticsPanel

# Import new Rover components
from ui.components.rover_control_card import RoverControlCard


class Dashboard:
    def __init__(self, page: ft.Page, controller) -> None:
        self.page = page
        self.controller = controller
        
        # Existing components
        self.header = Header(page, controller)
        self.footer = Footer(controller, on_report=self._on_generate_report)
        self.camera_card = CameraCard(controller, on_browse_video=self._on_browse_video)
        self.alert_card = AlertCard(controller)
        self.statistics_card = StatisticsCard(controller)
        self.history_table = HistoryTable(controller)
        self.snapshot_card = SnapshotCard(controller)
        self.gps_card = GPSCard(controller)
        self.gsm_card = GSMCard(
            on_send_sms=self.controller.esp_send_sms,
            on_test_sms=self.controller.esp_send_test_sms,
            controller=self.controller,
        )
        self.health_card = HealthCard(controller)
        self.charts_panel = AnalyticsPanel(controller)
        
        # New Rover Control Component
        self.rover_control = RoverControlCard(
            on_forward=self._on_rover_forward,
            on_backward=self._on_rover_backward,
            on_stop=self._on_rover_stop,
            on_speed_change=self._on_rover_speed_change,
            on_emergency_stop=self._on_rover_emergency_stop,
        )

    def mount(self) -> None:
        configure_page(self.page)
        self._closed = False
        self.page.on_close = self._on_close
        self.page.on_disconnect = self._on_close
        self.page.on_resize = self._on_resize
        self.page.add(self.build())
        self._apply_layout()
        self.header.start()
        self.controller.start()
        self._refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self._refresh_thread.start()

    def _refresh_loop(self):
        import traceback
        while not self._closed:
            try:
                self._refresh()
            except Exception as e:
                traceback.print_exc()
            time.sleep(0.1)

    def _refresh(self):
        self.header.update_status()
        self.camera_card.update_from_controller()
        self.snapshot_card.update()
        self.rover_control.update_from_controller(self.controller)
        self.statistics_card.update()
        self.health_card.update()
        self.alert_card.update()
        self.charts_panel.update()
        self.history_table.update()
        self.gps_card.update()
        self.gsm_card.update()
        self.page.update()

    def _on_close(self, event) -> None:
        # Per-session cleanup only. The shared AppController (camera loop +
        # ESP32 polling thread) is process-wide and is stopped on app exit by
        # app.py's shutdown handler, so closing one browser tab must not kill
        # the controller for other open tabs.
        self._closed = True
        self.header.stop()

    # ==================== Camera Source Handlers ====================

    async def _on_browse_video(self):
        """Open file picker to select a demo video file."""
        picker = ft.FilePicker()
        files = await picker.pick_files(
            allow_multiple=False,
            dialog_title="Select Demo Video",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["mp4", "avi", "mov", "mkv"],
            with_data=True,
        )
        if not files:
            return
        selected = files[0]
        path = self._persist_selected_video(selected)
        if not path:
            self.page.snack_bar = ft.SnackBar(
                ft.Text("Could not read selected video file"),
                bgcolor=ft.Colors.RED_900,
            )
            self.page.snack_bar.open = True
            self.page.update()
            return
        if self.controller.set_demo_video_path(path):
            self.controller.set_camera_source("demo")
            if not self.controller.is_running():
                self.controller.start()
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"Demo video selected: {os.path.basename(path)}"),
                bgcolor=ft.Colors.GREEN_900,
            )
            self.page.snack_bar.open = True
            self.page.update()

    def _persist_selected_video(self, selected) -> str:
        """Persist the picked file to a server-side path readable by OpenCV.

        Desktop/native picks expose a real `path`; web picks expose file bytes
        that must be written to disk first.
        """
        if getattr(selected, "path", None):
            return selected.path
        data = getattr(selected, "bytes", None)
        if not data:
            return ""
        import time as _time

        uploads_dir = config.UPLOADS_DIR
        os.makedirs(uploads_dir, exist_ok=True)
        name = getattr(selected, "name", "demo_video.mp4")
        safe = os.path.basename(name) or "demo_video.mp4"
        dest = os.path.join(uploads_dir, f"demo_{int(_time.time())}_{safe}")
        try:
            with open(dest, "wb") as f:
                f.write(data)
            return dest
        except OSError:
            return ""

    # ==================== Rover Control Callbacks ====================
    
    def _on_rover_forward(self):
        """Handle forward command"""
        self.controller.esp_forward()

    def _on_rover_backward(self):
        """Handle backward command"""
        self.controller.esp_backward()

    def _on_rover_stop(self):
        """Handle stop command"""
        self.controller.esp_stop()

    def _on_rover_speed_change(self, speed: int):
        """Handle speed change"""
        self.controller.esp_set_speed(speed)

    def _on_rover_emergency_stop(self):
        """Handle emergency stop"""
        self.controller.esp_emergency_stop()
        self._show_emergency_alert()

    def _show_emergency_alert(self):
        """Show emergency stop alert"""
        alert = ft.AlertDialog(
            title=ft.Text("⚠️ EMERGENCY STOP", color=ft.Colors.RED_400),
            content=ft.Text(
                "Emergency stop activated!\n"
                "Motors stopped, GPS recorded, SMS sent.",
                color=ft.Colors.WHITE,
            ),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_alert(alert)),
            ],
            bgcolor=ft.Colors.GREY_900,
        )
        self.page.dialog = alert
        alert.open = True
        self.page.update()

    def _close_alert(self, alert):
        """Close alert dialog"""
        alert.open = False
        self.page.update()

    # ==================== Report Generation ====================

    def _on_generate_report(self, event=None):
        """Generate the PDF report in a background thread so the UI stays responsive."""
        threading.Thread(target=self._generate_report_worker, daemon=True).start()

    def _generate_report_worker(self) -> None:
        try:
            from backend.report_generator import generate_report

            path = generate_report(self.controller)
            self._show_snack(
                f"Report generated successfully\n{os.path.basename(path)}",
                success=True,
            )
        except Exception as exc:
            self._show_snack(f"Report generation failed: {exc}", success=False)

    def _show_snack(self, message: str, success: bool) -> None:
        try:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(message),
                bgcolor=ft.Colors.GREEN_900 if success else ft.Colors.RED_900,
            )
            self.page.snack_bar.open = True
            self.page.update()
        except Exception:
            pass

    def build(self) -> ft.Control:
        # Responsive breakpoint: >= 992px keeps the classic fill-height,
        # bounded 3-column layout; below that cards stack and the page scrolls.
        self._wide = self._is_wide()

        self._middle_slot = ft.Container(
            expand=self._wide,
            padding=ft.Padding.all(12),
            content=self._build_middle_row(self._wide),
        )

        self._main_column = ft.Column(
            expand=True,
            spacing=0,
            scroll=None if self._wide else ft.ScrollMode.AUTO,
            controls=[
                self.header.build(),

                # Middle: 3-column grid (wide) or stacked cards (narrow).
                self._middle_slot,

                # Analytics: Crack + Severity distribution charts (full width).
                ft.Container(
                    padding=ft.padding.Padding.symmetric(horizontal=12, vertical=4),
                    content=ft.ResponsiveRow(
                        spacing=12,
                        run_spacing=12,
                        controls=[
                            ft.Container(
                                col={"xs": 12, "lg": 6},
                                content=self.charts_panel.build_distribution(),
                            ),
                            ft.Container(
                                col={"xs": 12, "lg": 6},
                                content=self.charts_panel.build_severity(),
                            ),
                        ],
                    ),
                ),

                # KPI strip above the footer (already a ResponsiveRow).
                ft.Container(
                    padding=ft.padding.Padding.symmetric(horizontal=12, vertical=6),
                    content=self.statistics_card.build(),
                ),

                self.footer.build(),
            ],
        )

        return ft.Container(
            expand=True,
            bgcolor=Palette.BG,
            content=self._main_column,
        )

    # ==================== Responsive layout helpers ====================

    def _is_wide(self) -> bool:
        """True when the viewport is large enough for the 3-column layout."""
        width = getattr(self.page, "width", None) or 1280
        return width >= 992

    def _on_resize(self, event=None) -> None:
        """Rebuild the middle section when the viewport crosses a breakpoint."""
        self._apply_layout()

    def _apply_layout(self) -> None:
        """Switch between the fill-height 3-column layout and the stacked,
        scrolling layout based on the current viewport width."""
        if self._main_column is None or self._middle_slot is None:
            return
        wide = self._is_wide()
        if wide == self._wide:
            return
        self._wide = wide
        self._main_column.scroll = None if wide else ft.ScrollMode.AUTO
        self._middle_slot.expand = wide
        self._middle_slot.content = self._build_middle_row(wide)
        self.page.update()

    def _build_middle_row(self, wide: bool):
        return self._build_wide_middle() if wide else self._build_narrow_middle()

    def _build_wide_middle(self) -> ft.Row:
        return ft.Row(
            expand=True,
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                # LEFT: Camera (fills) | GPS | GSM
                ft.Container(
                    expand=4,
                    content=ft.Column(
                        expand=True,
                        spacing=12,
                        controls=[
                            self.camera_card.build(),
                            self.gps_card.build(),
                            self.gsm_card.build(),
                        ],
                    ),
                ),
                # CENTER: Rover Controls | Detection Status
                ft.Container(
                    expand=3,
                    content=ft.Column(
                        expand=True,
                        spacing=12,
                        controls=[
                            self.rover_control.build(),
                            self.alert_card.build(),
                        ],
                    ),
                ),
                # RIGHT: Rover Status | Logs | Latest Snapshot
                ft.Container(
                    expand=3,
                    content=ft.Column(
                        expand=True,
                        spacing=12,
                        controls=[
                            self.health_card.build(),
                            self.history_table.build(),
                            self.snapshot_card.build(),
                        ],
                    ),
                ),
            ],
        )

    def _build_narrow_middle(self) -> ft.ResponsiveRow:
        """Stacked, compact layout for tablets/mobiles. Camera stays largest
        (full width); companion cards go 2-up on tablets and 1-up on phones."""
        return ft.ResponsiveRow(
            spacing=12,
            run_spacing=12,
            controls=[
                # CAMERA GROUP: Camera (largest) | GPS | GSM
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 12},
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self.camera_card.build(compact=True),
                            self.gps_card.build(),
                            self.gsm_card.build(compact=True),
                        ],
                    ),
                ),
                # CENTER GROUP: Rover Controls | Alert Status
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 6},
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self.rover_control.build(compact=True),
                            self.alert_card.build(compact=True),
                        ],
                    ),
                ),
                # RIGHT GROUP: Track Health | Detection History | Snapshot
                ft.Container(
                    col={"xs": 12, "sm": 12, "md": 6},
                    content=ft.Column(
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self.health_card.build(),
                            self.history_table.build(compact=True),
                            self.snapshot_card.build(compact=True),
                        ],
                    ),
                ),
            ],
        )