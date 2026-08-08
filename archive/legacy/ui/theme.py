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


# ------------------------------------------------------------------ spacing
# Single source of truth for the spacing/radius scale so every component stays
# consistent across all screen sizes.

SPACE_XS = 6
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16

PADDING_CARD = 14
PADDING_BODY = 12
RADIUS_CARD = 14
RADIUS_INNER = 10
RADIUS_PILL = 20


# ------------------------------------------------------------------ breakpoints
# Flet's ResponsiveRow default breakpoints (CSS pixels). Every tile decides how
# many of the 12 virtual columns it spans at each size via the col() helper.
# Reflow is handled natively by ResponsiveRow, so there is no manual breakpoint
# logic anywhere in the app.

BP_XS = 0    # < 576 px      mobile portrait
BP_SM = 576  # 576 - 767     mobile landscape
BP_MD = 768  # 768 - 991     tablet
BP_LG = 992  # 992 - 1199    small desktop
BP_XL = 1200 # >= 1200 px    large desktop


def col(*, xs: int = 12, sm=None, md=None, lg=None, xl=None) -> dict:
    """Build a ResponsiveRow column-span dict, omitting unset breakpoints."""
    result = {"xs": xs}
    for name, value in (("sm", sm), ("md", md), ("lg", lg), ("xl", xl)):
        if value is not None:
            result[name] = value
    return result


def grid(controls, spacing: int = SPACE_MD, run_spacing: int = SPACE_MD) -> ft.ResponsiveRow:
    """ResponsiveRow with the app's standard card spacing."""
    return ft.ResponsiveRow(spacing=spacing, run_spacing=run_spacing, controls=controls)


def tile(control, cols: dict) -> ft.Container:
    """Wrap a control in a grid cell that spans the given columns."""
    return ft.Container(col=cols, content=control)


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
    """Apply the app's global page configuration (web mode).

    The page is left unpadded: the dashboard owns the full viewport and pins
    its header/footer while the middle section scrolls. The browser viewport
    controls the size, so no window sizing is required.
    """
    page.title = "Railway Crack Detection System"
    page.bgcolor = Palette.BG
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=Palette.PRIMARY)
