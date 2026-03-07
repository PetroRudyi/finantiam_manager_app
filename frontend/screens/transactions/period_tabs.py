# -*- coding: utf-8 -*-
"""Daily / Weekly / Total period tabs."""

from typing import Callable
import flet as ft
from frontend import theme as t


def build_period_tabs(current_mode: str, on_change: Callable[[str], None]) -> ft.Container:
    def tab(label, mode):
        active = current_mode == mode
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=11,
                        color=t.TEXT if active else t.TEXT_DIMMER,
                        font_family="monospace",
                        text_align=ft.TextAlign.CENTER),
                ft.Container(
                    height=2,
                    bgcolor=t.ACCENT if active else "transparent",
                    border_radius=2,
                    margin=t.mar_only(top=6),
                ),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=t.pad_sym(vertical=9),
            on_click=lambda e, m=mode: on_change(m),
            ink=True,
        )

    return ft.Container(
        content=ft.Row(
            [tab("Daily", "daily"), tab("Weekly", "weekly"), tab("Total", "total")],
            spacing=0,
        ),
        border=t.border_bottom(),
    )
