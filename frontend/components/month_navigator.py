# -*- coding: utf-8 -*-
"""frontend/components/month_navigator.py — Shared month/year navigation bar."""

from typing import Callable, Optional
import flet as ft
from frontend import theme as t


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

        month_label = f"{t.UA_MONTHS_SHORT[month]} {year}"

        right_controls = extra_right or ft.Container()

        super().__init__(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Text("‹", size=14, color=t.TEXT_DIM),
                        on_click=lambda e: self._prev_month(),
                        ink=True, padding=t.pad_sym(horizontal=4, vertical=2),
                    ),
                    ft.Text(month_label, size=14, color=t.TEXT,
                            weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text("›", size=14, color=t.TEXT_DIM),
                        on_click=lambda e: self._next_month(),
                        ink=True, padding=t.pad_sym(horizontal=4, vertical=2),
                    ),
                ], spacing=5),
                right_controls,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=18, right=18, top=8, bottom=6),
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
