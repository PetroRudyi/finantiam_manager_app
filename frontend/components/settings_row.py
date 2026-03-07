# -*- coding: utf-8 -*-
"""frontend/components/settings_row.py — Reusable settings list row."""

import flet as ft
from frontend import theme as t


def settings_section(label: str) -> ft.Container:
    """Section header for settings lists."""
    return ft.Container(
        content=ft.Text(label, size=9, color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=1.2)),
        padding=t.pad_only(left=18, right=18, top=12, bottom=5),
    )


def settings_row(label: str, sub: str = "",
                 right=None, on_click=None) -> ft.Container:
    """Standard settings row: label + optional subtitle, right widget, tap handler."""
    return ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(label, size=13, color=t.TEXT,
                        weight=ft.FontWeight.W_500),
                *([ft.Text(sub, size=9, color=t.TEXT_DIMMER)] if sub else []),
            ], spacing=1, expand=True),
            right or ft.Container(),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=t.pad_sym(horizontal=18, vertical=10),
        border=t.border_bottom(),
        on_click=on_click,
        ink=bool(on_click),
    )
