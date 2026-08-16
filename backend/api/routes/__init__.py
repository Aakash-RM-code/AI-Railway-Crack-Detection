"""Centralized HTTP router for the Railway Crack Detection API.

Imports and includes modular route modules for System, Camera, Detections, Hardware, and Reports.
"""

from fastapi import APIRouter

from backend.api.routes.system import router as system_router
from backend.api.routes.camera import router as camera_router
from backend.api.routes.detections import router as detections_router
from backend.api.routes.hardware import router as hardware_router
from backend.api.routes.reports import router as reports_router

router = APIRouter(prefix="/api")

router.include_router(system_router)
router.include_router(camera_router)
router.include_router(detections_router)
router.include_router(hardware_router)
router.include_router(reports_router)

