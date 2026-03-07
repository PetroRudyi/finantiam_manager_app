# -*- coding: utf-8 -*-
"""
frontend/screens/dashboard/screen.py
Screen 02 — Analytics: bar chart + donut chart + category breakdown.
"""

import datetime
from typing import List
import flet as ft

from backend.models import Receipt
from frontend.components.month_navigator import MonthNavigator
from frontend.components.type_toggle import TypeToggle
from frontend.screens.dashboard.bar_chart import build_bar_chart
from frontend.screens.dashboard.donut_chart import build_donut_chart
from frontend.screens.dashboard.top_categories import build_top_categories
from frontend import theme as t


class DashboardScreen(ft.Column):
    def __init__(self, app_state):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self._mode = "expense"
        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        self._build()

    def refresh(self):
        self._build()
        self.update()

    def _build(self):
        self.controls.clear()
        receipts: List[Receipt] = self.app_state.receipts
        settings = self.app_state.settings

        month_receipts = [
            r for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]

        extra_right = ft.Container(
            content=ft.Text("Кастом", size=9, color=t.TEXT_DIM,
                            font_family="monospace"),
            bgcolor=t.SURFACE2, border_radius=8,
            padding=t.pad_sym(horizontal=10, vertical=5),
            border=t.border_all(),
        )

        self.controls += [
            MonthNavigator(self._year, self._month,
                           on_change=self._on_month_change,
                           extra_right=extra_right),
            TypeToggle(self._mode, on_change=self._set_mode, style="filled"),
            ft.Column([
                build_bar_chart(receipts, self._mode, self._year, self._month,
                                settings.default_currency),
                build_donut_chart(month_receipts, self._mode, settings),
                build_top_categories(month_receipts, self._mode, settings),
            ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
        ]

    # ── Handlers ──────────────────────────────────────────────

    def _on_month_change(self, year: int, month: int):
        self._year = year
        self._month = month
        self._build()
        self.update()

    def _set_mode(self, mode: str):
        self._mode = mode
        self._build()
        self.update()
