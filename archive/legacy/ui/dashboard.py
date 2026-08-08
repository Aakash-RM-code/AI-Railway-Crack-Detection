import flet as ft
import threading
import time
import os

import config

from ui.theme import (
    configure_page,
    col,
    grid,
    tile,
    SPACE_MD,
)
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
        self.page.add(self.build())
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

    # ==================== Layout ====================

    def build(self) -> ft.Control:
        """Build the full dashboard.

        The page is a viewport-filling column: the header stays pinned to the
        top, the footer to the bottom, and the middle section is the
        dashboard's single bounded scroll region.

        Layout rule (from Flet's `Control.expand` docs): `expand` only has
        effect when the direct parent is a Column/Row/View/Page. The middle
        Column is therefore a *direct* child of the outer Column (no Container
        in between) so its `expand=True` really fills the viewport minus the
        header/footer and the scroll area stays height-bounded. Cards inside
        never expand along the scroll axis, so the page itself cannot grow.
        """
        body = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.Padding.symmetric(horizontal=12, vertical=12),
                    content=self._build_grid(),
                ),
            ],
        )

        return ft.Column(
            expand=True,
            spacing=0,
            controls=[
                self.header.build(),
                body,
                self.footer.build(),
            ],
        )

    def _build_grid(self) -> ft.ResponsiveRow:
        """Responsive 12-column grid containing every dashboard card.

        Breakpoints are Flet defaults (xs<576, sm>=576, md>=768, lg>=992,
        xl>=1200). Cards reflow automatically as the window is resized, so no
        manual breakpoint handling is required:
          - Phone portrait   : everything stacks to full width.
          - Phone landscape  : GPS/Health share a row; the rest stack.
          - Tablet           : camera + rover/alert rail go 2-up, GPS/Health/
                               GSM share a row, Snapshot + History go 2-up.
          - Desktop          : full multi-column layout.
        """
        return grid(
            controls=[
                # Camera (largest) + Rover/Alert rail
                tile(self.camera_card.build(), col(xs=12, md=8, lg=8, xl=8)),
                tile(
                    ft.Column(
                        spacing=SPACE_MD,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self.rover_control.build(),
                            self.alert_card.build(),
                        ],
                    ),
                    col(xs=12, md=4, lg=4, xl=4),
                ),
                # Status cards: GPS / Track Health / GSM
                tile(self.gps_card.build(), col(xs=12, sm=6, md=4, lg=4, xl=4)),
                tile(self.health_card.build(), col(xs=12, sm=6, md=4, lg=4, xl=4)),
                tile(self.gsm_card.build(), col(xs=12, sm=12, md=4, lg=4, xl=4)),
                # Snapshot + Detection History
                tile(self.snapshot_card.build(), col(xs=12, md=6, lg=5, xl=5)),
                tile(self.history_table.build(), col(xs=12, md=6, lg=7, xl=7)),
                # Analytics charts (full width, two-up on tablet/desktop)
                tile(
                    grid(
                        controls=[
                            tile(self.charts_panel.build_distribution(), col(xs=12, md=6, lg=6)),
                            tile(self.charts_panel.build_severity(), col(xs=12, md=6, lg=6)),
                        ],
                    ),
                    col(xs=12),
                ),
                # KPI strip
                tile(self.statistics_card.build(), col(xs=12)),
            ],
        )
