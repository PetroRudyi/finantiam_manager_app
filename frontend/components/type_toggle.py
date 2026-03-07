# -*- coding: utf-8 -*-
"""frontend/components/type_toggle.py — Expense/Income segmented toggle."""

from typing import Callable
import flet as ft
from frontend import theme as t


class TypeToggle(ft.Container):
    """Segmented control to switch between expense and income.

    Parameters:
        current_mode: "expense" or "income"
        on_change: callback(new_mode)
        style: "filled" for dashboard look, "outlined" for receipt form look
    """

    def __init__(self, current_mode: str, on_change: Callable[[str], None],
                 style: str = "filled"):
        self._on_change = on_change

        if style == "filled":
            content = self._filled(current_mode)
            super().__init__(
                content=content,
                bgcolor=t.SURFACE2, border_radius=9, padding=3,
                margin=t.mar_only(left=18, right=18, bottom=8),
            )
        else:
            content = self._outlined(current_mode)
            super().__init__(content=content)

    def _filled(self, current_mode: str) -> ft.Row:
        def btn(label, mode):
            active = current_mode == mode
            return ft.Container(
                content=ft.Text(label, size=10,
                                color=t.TEXT if active else t.TEXT_DIMMER,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER),
                expand=True,
                bgcolor=t.SURFACE if active else "transparent",
                border_radius=7,
                padding=t.pad_sym(vertical=5),
                on_click=lambda e, m=mode: self._on_change(m),
                ink=True,
            )
        return ft.Row([btn("Витрати", "expense"), btn("Дохід", "income")],
                      spacing=0)

    def _outlined(self, current_mode: str) -> ft.Row:
        def btn(label, mode):
            active = current_mode == mode
            color = t.RED if mode == "expense" else t.BLUE
            return ft.Container(
                content=ft.Text(label, size=11, font_family="monospace",
                                color=color if active else t.TEXT_DIMMER,
                                text_align=ft.TextAlign.CENTER),
                expand=True,
                bgcolor=t.alpha(color, "18") if active else t.SURFACE2,
                border=t.border_all(1, t.alpha(color, "88") if active else t.BORDER),
                border_radius=9,
                padding=t.pad_sym(vertical=7),
                on_click=lambda e, m=mode: self._on_change(m),
                ink=True,
            )
        return ft.Row([btn("Витрата", "expense"), btn("Дохід", "income")], spacing=7)
