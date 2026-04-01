# -*- coding: utf-8 -*-
"""frontend/components/month_navigator.py — Shared month/year navigation bar."""

from typing import Callable, Optional
import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.sizes import FONT_NAV, FONT_NAV_ARROW, PAD_PAGE_H


class MonthNavigator(ft.Container):
    """Month navigation bar with prev/next arrows and optional extra controls.

    Parameters:
        year: current year
        month: current month (1-12)
        on_change: callback(new_year, new_month) when user navigates
        extra_right: optional controls placed on the right side
    """

    def __init__(self, year: int, month: int,
                 on_change: Callable[[int, int], None],
                 extra_right: Optional[ft.Control] = None):
        self._year = year
        self._month = month
        self._on_change = on_change

        month_label = f"{t.get_months_short()[month]} {year}"

        right_controls = extra_right or ft.Container()

        def _arrow_btn(icon: ft.Icons, on_click):
            return ft.Container(
                content=ft.Icon(icon, size=scaled(FONT_NAV_ARROW), color=t.TEXT_DIM),
                on_click=on_click,
                ink=True, padding=t.pad_sym(horizontal=scaled(10), vertical=scaled(6)),
            )

        super().__init__(
            content=ft.Row([
                ft.Row([
                    _arrow_btn(ft.Icons.CHEVRON_LEFT, lambda e: self._prev_month()),
                    ft.Text(month_label, size=scaled(FONT_NAV), color=t.TEXT,
                            weight=ft.FontWeight.W_600),
                    _arrow_btn(ft.Icons.CHEVRON_RIGHT, lambda e: self._next_month()),
                ], spacing=scaled(5), alignment=ft.MainAxisAlignment.CENTER,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                right_controls,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                               top=scaled(8), bottom=scaled(6)),
        )

    def _prev_month(self):
        if self._month == 1:
            self._on_change(self._year - 1, 12)
        else:
            self._on_change(self._year, self._month - 1)

    def _next_month(self):
        if self._month == 12:
            self._on_change(self._year + 1, 1)
        else:
            self._on_change(self._year, self._month + 1)
