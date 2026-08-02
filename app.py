"""
ESP32 Rover Control System - Main Application Entry Point
"""
import atexit
import flet as ft
import logging
import os
import socket
import sys
import threading
import time
import traceback
import webbrowser

from ui.controller import get_controller, get_existing_controller
from ui.dashboard import Dashboard
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PORT = 8080
APP_URL = f"http://localhost:{PORT}"
LOCK_FILE = config.APP_LOCK_FILE


def open_browser():
    """Open browser after a short delay"""
    time.sleep(3)
    webbrowser.open(APP_URL)


def _pid_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _port_in_use(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(("127.0.0.1", port)) == 0
    except OSError:
        return False


def _acquire_instance_lock() -> str:
    """Prevent duplicate launches.

    Returns one of:
      - 'acquired'       -> we are the sole instance, lock written
      - 'already_running'-> our PID lock exists and the process is alive
      - 'port_busy'      -> port is bound by some other process
    """
    if _port_in_use(PORT):
        if os.path.exists(LOCK_FILE):
            try:
                with open(LOCK_FILE, "r") as f:
                    pid = int(f.read().strip() or 0)
                if _pid_is_alive(pid):
                    return "already_running"
            except (OSError, ValueError):
                pass
        return "port_busy"
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except OSError:
        pass
    return "acquired"


def _release_instance_lock() -> None:
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip() or 0)
            if pid == os.getpid():
                os.remove(LOCK_FILE)
    except (OSError, ValueError):
        try:
            os.remove(LOCK_FILE)
        except OSError:
            pass


def _shutdown() -> None:
    """Stop background threads and release the single-instance lock."""
    _release_instance_lock()
    ctrl = get_existing_controller()
    if ctrl is not None:
        try:
            ctrl.close()
        except Exception:
            logger.exception("Error during controller shutdown")


def main(page: ft.Page):
    """Main application entry point"""
    try:
        logger.info("Starting application...")

        # Configure page
        page.title = "ESP32 Rover Control System"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.padding = 10
        page.spacing = 10

        logger.info("Creating controller...")
        controller = get_controller()

        logger.info("Creating dashboard...")
        dashboard = Dashboard(page, controller)
        dashboard.mount()

        logger.info("Connecting to ESP32...")
        try:
            controller.connect()
        except Exception as e:
            logger.warning(f"Could not connect to ESP32: {e}")
            page.snack_bar = ft.SnackBar(
                ft.Text(f"⚠️ Could not connect to ESP32: {e}"),
                bgcolor=ft.Colors.ORANGE_900,
            )
            page.snack_bar.open = True

        logger.info("Application started successfully!")
        page.update()

    except Exception as e:
        logger.error(f"Error starting application: {e}")
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("ESP32 Rover Control System")
    logger.info("=" * 50)

    # The project is verified on Python 3.11 (see run_app.bat / run_app.ps1).
    if sys.version_info[:2] != (3, 11):
        logger.warning(
            f"Running on Python {sys.version_info.major}.{sys.version_info.minor} - "
            "this application is verified on Python 3.11."
        )

    instance_state = _acquire_instance_lock()
    if instance_state == "already_running":
        logger.info(f"Application is already running on {APP_URL}. Opening browser...")
        webbrowser.open(APP_URL)
        sys.exit(0)
    if instance_state == "port_busy":
        logger.error(
            f"Port {PORT} is already in use by another process. "
            "Close the other application or free the port, then retry."
        )
        sys.exit(1)

    atexit.register(_shutdown)

    try:
        # Open browser automatically
        threading.Thread(target=open_browser, daemon=True).start()

        # Run in web browser mode (NOT desktop)
        logger.info(f"Starting in web mode on {APP_URL}...")
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=PORT)

    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
    finally:
        _shutdown()
