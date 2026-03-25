# -*- coding: utf-8 -*-
"""Daily / Weekly / Total period tabs."""

from typing import Callable
import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_MD
from frontend.screens.transactions.sizes import (
    TAB_INDICATOR_H, TAB_INDICATOR_RADIUS, TAB_INDICATOR_MARGIN, TAB_PAD_V,
)


def build_period_tabs(current_mode: str, on_change: Callable[[str], None]) -> ft.Container:
    def tab(label, mode):
        active = current_mode == mode
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=scaled(FONT_MD),
                        color=t.TEXT if active else t.TEXT_DIMMER,
                        font_family="monospace",
                        text_align=ft.TextAlign.CENTER),
                ft.Container(
                    height=scaled(TAB_INDICATOR_H),
                    bgcolor=t.ACCENT if active else "transparent",
                    border_radius=scaled(TAB_INDICATOR_RADIUS),
                    margin=t.mar_only(top=scaled(TAB_INDICATOR_MARGIN)),
                ),
            ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=t.pad_sym(vertical=scaled(TAB_PAD_V)),
            on_click=lambda e, m=mode: on_change(m),
            ink=True,
        )

    return ft.Container(
        content=ft.Row(
            [tab(tr("period_tabs.daily"), "daily"), tab(tr("period_tabs.weekly"), "weekly"), tab(tr("period_tabs.total"), "total")],
            spacing=0,
        ),
        border=t.border_bottom(),
    )
