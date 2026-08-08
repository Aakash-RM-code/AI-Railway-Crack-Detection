"""
Generates a professional PDF inspection report summarizing detection stats,
current health, the latest detection, the latest snapshot, and the recent
detection history read from logs/detections.csv.

Requires: pip install reportlab

Standalone — accepts a plain runtime-state dict (no Flet controller) so it can
be reused by the FastAPI layer, the legacy Flet app, or a CLI.
"""
import warnings
warnings.filterwarnings("ignore")

import csv
import glob
import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image as RLImage,
)

import config

REPORTS_DIR = config.REPORTS_DIR
HISTORY_CSV = config.HISTORY_CSV
DETECTIONS_DIR = config.DETECTIONS_DIR

SOFTWARE_VERSION = "1.0.0"
HISTORY_LIMIT = 10
SNAPSHOT_MAX_WIDTH = 480
SNAPSHOT_MAX_HEIGHT = 320

_HEADER_BG = colors.HexColor("#171C24")
_GRID = colors.HexColor("#232A35")


def _read_history(limit: int = HISTORY_LIMIT) -> list[dict]:
    """Read the most recent `limit` rows directly from logs/detections.csv."""
    if not os.path.isfile(HISTORY_CSV):
        return []
    rows = []
    try:
        with open(HISTORY_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows.append(row)
    except OSError:
        return []
    return rows[-limit:]


def _latest_snapshot() -> str:
    """Return the path of the most recently saved image inside detections/."""
    files = glob.glob(os.path.join(DETECTIONS_DIR, "*.jpg"))
    if not files:
        return ""
    return max(files, key=os.path.getmtime)


def _severity_for(class_name: str) -> str:
    name = (class_name or "").lower()
    if "small" in name:
        return "LOW"
    if "medium" in name:
        return "MEDIUM"
    if "large" in name:
        return "HIGH"
    if "broken" in name:
        return "CRITICAL"
    return "UNKNOWN"


def _human_name(class_name: str) -> str:
    return " ".join(
        word.capitalize() for word in (class_name or "").split() if word
    ) or "--"


def _label_value_table(pairs: list[tuple[str, str]]) -> Table:
    data = [[Paragraph(label, _cell_style()), Paragraph(value, _cell_style())]
            for label, value in pairs]
    table = Table(data, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F0F1F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, _GRID),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def _snapshot_flowable(snapshot_path: str) -> RLImage:
    iw, ih = ImageReader(snapshot_path).getSize()
    scale = min(SNAPSHOT_MAX_WIDTH / iw, SNAPSHOT_MAX_HEIGHT / ih, 1.0)
    img = RLImage(snapshot_path, width=iw * scale, height=ih * scale)
    img.hAlign = "LEFT"
    return img


def _page_footer(canvas, doc):
    """Footer drawn at the bottom of every page."""
    canvas.saveState()
    canvas.setStrokeColor(_GRID)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 12 * mm, A4[0] - 15 * mm, 12 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(
        A4[0] / 2, 8 * mm, "Generated automatically by Railway Crack Detection System"
    )
    canvas.restoreState()


def _base_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom", parent=styles["Title"], fontSize=20, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom", parent=styles["Normal"], textColor=colors.grey,
            spaceAfter=16,
        ),
        "heading": styles["Heading2"],
        "normal": styles["Normal"],
        "empty": ParagraphStyle(
            "EmptyCustom", parent=styles["Normal"], textColor=colors.grey,
            spaceBefore=4,
        ),
    }


def _cell_style():
    return ParagraphStyle(
        "CellCustom", parent=getSampleStyleSheet()["Normal"],
        fontSize=10, leading=13,
    )


def generate_report(state: dict) -> str:
    """Generate a PDF inspection report from a runtime-state dict.

    The dict should contain the same keys produced by
    ``CameraPipeline.get_state()`` plus ``gps`` and ``session_start``:

    * ``stats``          — dict of detection counters (total/small/medium/large/broken)
    * ``health``         — dict with score/status/note
    * ``alert``          — dict with severity/message/class_name/confidence
    * ``gps``            — GPS string or None
    * ``session_start``  — datetime (or string) of session start

    Returns the absolute path to the generated PDF inside reports/.
    """
    stats = state.get("stats") or {}
    health = state.get("health") or {}
    alert = state.get("alert") or {}
    gps = state.get("gps")
    session_start = state.get("session_start") or datetime.now()

    if isinstance(session_start, str):
        try:
            session_start = datetime.fromisoformat(session_start)
        except ValueError:
            session_start = datetime.now()

    history = _read_history(HISTORY_LIMIT)
    snapshot_path = _latest_snapshot()
    has_detections = (stats.get("total", 0) > 0) or bool(history)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now()
    output_path = os.path.join(
        REPORTS_DIR, f"Report_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    S = _base_styles()
    story = []

    # --- header ---
    story.append(Paragraph("Railway Crack Detection Report", S["title"]))
    story.append(Paragraph(
        f"Generated {timestamp.strftime('%d %b %Y, %H:%M:%S')}", S["subtitle"]
    ))

    # --- session info ---
    story.append(Paragraph("Session Information", S["heading"]))
    story.append(_label_value_table([
        ("Date", timestamp.strftime("%d %b %Y")),
        ("Time", timestamp.strftime("%H:%M:%S")),
        ("Session Start", session_start.strftime("%d %b %Y, %H:%M:%S")),
        ("Model Name", str(getattr(config, "MODEL_PATH", "best.pt"))),
        ("Software Version", SOFTWARE_VERSION),
    ]))
    story.append(Spacer(1, 12))

    # --- current health ---
    story.append(Paragraph("Current Health", S["heading"]))
    story.append(_label_value_table([
        ("Score", f"{health.get('score', '--')}/100"),
        ("Status", str(health.get("status", "--"))),
        ("Note", str(health.get("note", "--"))),
    ]))
    story.append(Spacer(1, 12))

    # --- current status ---
    story.append(Paragraph("Current Status", S["heading"]))
    status_line = f"{alert.get('severity', '--')} — {alert.get('message', '--')}"
    story.append(Paragraph(status_line, S["normal"]))
    story.append(Spacer(1, 12))

    # --- detection summary ---
    story.append(Paragraph("Detection Summary", S["heading"]))
    if has_detections:
        summary_data = [
            [Paragraph(h, _cell_style()) for h in
             ("Total", "Small", "Medium", "Large", "Broken")],
            [Paragraph(str(stats.get(k, "--")), _cell_style()) for k in
             ("total", "small", "medium", "large", "broken")],
        ]
        summary_table = Table(summary_data, colWidths=[96] * 5)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, _GRID),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(summary_table)
    else:
        story.append(Paragraph("No detections recorded.", S["empty"]))
    story.append(Spacer(1, 12))

    # --- latest detection ---
    story.append(Paragraph("Latest Detection", S["heading"]))
    if history:
        latest = history[-1]
        class_name = latest.get("Class", "")
        story.append(_label_value_table([
            ("Crack Type", _human_name(class_name)),
            ("Severity", _severity_for(class_name)),
            ("Confidence", str(latest.get("Confidence", "--"))),
            ("GPS", gps if gps else "N/A"),
            ("Timestamp", str(latest.get("Timestamp", "--"))),
        ]))
    else:
        story.append(Paragraph("No detections recorded.", S["empty"]))
    story.append(Spacer(1, 12))

    # --- latest snapshot ---
    story.append(Paragraph("Latest Snapshot", S["heading"]))
    if snapshot_path:
        story.append(_snapshot_flowable(snapshot_path))
    else:
        story.append(Paragraph("No snapshot available.", S["empty"]))
    story.append(Spacer(1, 12))

    # --- recent detection history ---
    story.append(Paragraph("Recent Detection History", S["heading"]))
    if history:
        history_data = [[
            Paragraph("Timestamp", _cell_style()),
            Paragraph("Crack Type", _cell_style()),
            Paragraph("Confidence", _cell_style()),
        ]]
        for row in history:
            history_data.append([
                Paragraph(str(row.get("Timestamp", "--")), _cell_style()),
                Paragraph(_human_name(row.get("Class", "")), _cell_style()),
                Paragraph(str(row.get("Confidence", "--")), _cell_style()),
            ])
        history_table = Table(history_data, colWidths=[190, 150, 140])
        history_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, _GRID),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(history_table)
    else:
        story.append(Paragraph("No detections recorded.", S["empty"]))

    doc.build(
        story,
        onFirstPage=_page_footer,
        onLaterPages=_page_footer,
    )
    return output_path
