"""Minimal runner that mounts the real Dashboard on a separate port for layout testing.

ARCHIVED — kept as a manual layout-testing harness. Not part of the application,
not imported anywhere. Run manually if ever needed:
    python archive/legacy/layout_test.py [port]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import flet as ft
from ui.controller import get_controller
from ui.dashboard import Dashboard

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8090


def main(page: ft.Page):
    page.title = "Layout Test"
    page.window_width = 1280
    page.window_height = 840
    controller = get_controller()
    dashboard = Dashboard(page, controller)
    dashboard.mount()
    page.update()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=PORT)
