import flet as ft


class Palette:
    BG = "#0B0E14"
    SURFACE = "#141A23"
    SURFACE_ALT = "#1D2530"
    BORDER = "#2A3442"
    PRIMARY = "#F5A623"
    PRIMARY_DARK = "#C88A1B"
    TEXT = "#E6EAF2"
    TEXT_MUTED = "#8A94A6"
    SUCCESS = "#2ECC71"
    WARNING = "#F5A623"
    ORANGE = "#E67E22"
    DANGER = "#E74C3C"
    CRITICAL = "#9B59B6"
    INFO = "#3498DB"
    BLACK = "#05070B"


SEVERITY_COLORS = {
    "SAFE": Palette.SUCCESS,
    "LOW": Palette.WARNING,
    "MEDIUM": Palette.ORANGE,
    "HIGH": Palette.DANGER,
    "CRITICAL": Palette.CRITICAL,
    "UNKNOWN": Palette.TEXT_MUTED,
}

CRACK_TYPE_COLORS = {
    "small crack": Palette.WARNING,
    "medium crack": Palette.ORANGE,
    "large crack": Palette.DANGER,
    "broken chain": Palette.CRITICAL,
}

CARD_SHADOW = ft.BoxShadow(
    blur_radius=14,
    color="#26000000",
    offset=ft.Offset(0, 4),
)


def severity_color(severity: str) -> str:
    return SEVERITY_COLORS.get(str(severity).upper(), Palette.TEXT_MUTED)


def crack_type_color(crack_type: str) -> str:
    return CRACK_TYPE_COLORS.get(str(crack_type).lower(), Palette.TEXT_MUTED)


def border_all(color: str, width: float = 1) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, left=side, right=side, bottom=side)


def configure_page(page: ft.Page) -> None:
    page.title = "Railway Crack Detection System"
    page.bgcolor = Palette.BG
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=Palette.PRIMARY)
    try:
        page.window.width = 1280
        page.window.height = 840
        page.window.min_width = 320
        page.window.min_height = 568
    except AttributeError:
        pass
