import flet as ft

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
    RADIUS_PILL,
)


def section_card(
    title: str,
    body: ft.Control,
    icon: ft.Icon | None = None,
    trailing: ft.Control | None = None,
) -> ft.Container:
    header = ft.Row(
        controls=[
            icon,
            ft.Text(title.upper(), size=12, color=Palette.TEXT_MUTED),
            ft.Container(expand=True),
            trailing if trailing is not None else ft.Text(""),
        ],
        spacing=SPACE_SM,
    )
    return ft.Container(
        bgcolor=Palette.SURFACE,
        border=border_all(Palette.BORDER),
        border_radius=RADIUS_CARD,
        shadow=CARD_SHADOW,
        padding=ft.padding.Padding.all(PADDING_CARD),
        content=ft.Column(
            controls=[header, body],
            spacing=SPACE_MD,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )


def status_pill(
    text: str,
    color: str,
    icon: ft.Icon | None = None,
    small: bool = False,
) -> ft.Container:
    controls = []
    if icon is not None:
        controls.append(icon)
    controls.append(ft.Text(text, size=11 if small else 12, weight=ft.FontWeight.BOLD, color=color))
    return ft.Container(
        padding=ft.padding.Padding.symmetric(
            horizontal=10 if small else 12,
            vertical=4 if small else 6,
        ),
        bgcolor=color + "1F",
        border_radius=RADIUS_PILL,
        content=ft.Row(controls=controls, spacing=SPACE_XS, tight=True),
    )


def kpi_card(
    icon: ft.Icon,
    label: str,
    value,
    color: str,
    value_control: ft.Control | None = None,
) -> ft.Container:
    value_text = value_control if value_control is not None else ft.Text(
        str(value), size=20, weight=ft.FontWeight.BOLD, color=Palette.TEXT
    )
    return ft.Container(
        bgcolor=Palette.SURFACE,
        border=border_all(Palette.BORDER),
        border_radius=RADIUS_CARD - 2,
        shadow=CARD_SHADOW,
        padding=ft.padding.Padding.all(PADDING_CARD),
        content=ft.Row(
            controls=[
                ft.Container(
                    width=40,
                    height=40,
                    bgcolor=color + "1F",
                    border_radius=RADIUS_INNER,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icon, size=20, color=color),
                ),
                ft.Column(
                    controls=[
                        value_text,
                        ft.Text(label, size=11, color=Palette.TEXT_MUTED),
                    ],
                    spacing=SPACE_XS,
                ),
            ],
            spacing=SPACE_MD,
        ),
    )


def placeholder(icon: ft.Icon, label: str) -> ft.Container:
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            controls=[
                ft.Icon(icon, size=36, color=Palette.BORDER),
                ft.Text(label, size=12, color=Palette.TEXT_MUTED),
            ],
            spacing=SPACE_SM,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
