# -*- coding: utf-8 -*-
"""frontend/components/settings_row.py — Reusable settings list row."""

import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.sizes import (
    FONT_SM, FONT_LG, LETTER_SPACING,
    PAD_PAGE_H, PAD_SECTION_TOP, BTN_PAD_V,
)


def settings_section(label: str, first: bool = False) -> ft.Column:
    """Section header for settings lists."""
    header = ft.Container(
        content=ft.Text(label, size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           top=scaled(PAD_SECTION_TOP), bottom=scaled(5)),
    )
    if first:
        return ft.Column([header], spacing=0)
    return ft.Column([
        ft.Divider(height=1, thickness=scaled(1), color=t.BORDER),
        header,
    ], spacing=0)


def settings_row(label: str, sub: str = "",
                 right=None, on_click=None) -> ft.Container:
    """Standard settings row: label + optional subtitle, right widget, tap handler."""
    return ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(label, size=scaled(FONT_LG), color=t.TEXT,
                        weight=ft.FontWeight.W_500),
                *([ft.Text(sub, size=scaled(FONT_SM), color=t.TEXT_DIMMER)] if sub else []),
            ], spacing=1, expand=True),
            right or ft.Container(),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(BTN_PAD_V)),
        on_click=on_click,
        ink=bool(on_click),
    )
