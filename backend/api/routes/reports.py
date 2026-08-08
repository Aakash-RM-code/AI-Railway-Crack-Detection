"""PDF Inspection report generation and download routes."""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

import config
from backend.api import schemas
from backend.api.auth import verify_hardware_token
from backend.services.camera import get_pipeline
from backend.services.report_generator import generate_report

router = APIRouter(tags=["Reports"])


def _generate_pdf():
    pipeline = get_pipeline()
    esp = pipeline.get_esp32()
    state = pipeline.get_state()
    state["gps"] = None
    if esp and esp.get_cached_gps():
        state["gps"] = esp.get_cached_gps()

    state["session_start"] = pipeline.started_at()

    pdf_path = generate_report(state)
    filename = os.path.basename(pdf_path)
    url = f"/api/reports/download/{filename}"

    return schemas.ReportResponse(
        path=pdf_path,
        url=url,
    )


@router.post("/reports/generate", response_model=schemas.ReportResponse, dependencies=[Depends(verify_hardware_token)])
def generate_inspection_report():
    """Generates a professional PDF inspection report."""
    return _generate_pdf()


@router.post("/report", response_model=schemas.ReportResponse, dependencies=[Depends(verify_hardware_token)])
def legacy_report():
    return _generate_pdf()


@router.get("/reports/download/{filename}", dependencies=[Depends(verify_hardware_token)])
def download_report(filename: str):
    """Serves generated PDF inspection report file for download."""
    pdf_path = os.path.join(config.REPORTS_DIR, filename)
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=filename,
    )
