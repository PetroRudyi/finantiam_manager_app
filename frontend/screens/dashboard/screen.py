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
from frontend.screens.dashboard.category_detail import CategoryDetailScreen
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_SM
from frontend.screens.dashboard.sizes import (
    CUSTOM_BTN_RADIUS, CUSTOM_BTN_PAD_H, CUSTOM_BTN_PAD_V,
)


class DashboardScreen(ft.Column):
    def __init__(self, app_state, on_edit_receipt=None):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self._on_edit_receipt = on_edit_receipt
        self._mode = "expense"
        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        self._in_category_detail = False
        self._build()

    def refresh(self):
        self._build()
        self.update()

    @property
    def in_category_detail(self) -> bool:
        return self._in_category_detail

    def close_category_detail(self):
        """Return from category detail to main dashboard."""
        if self._in_category_detail:
            self._in_category_detail = False
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
            content=ft.Text(tr("dashboard.custom"), size=scaled(FONT_SM), color=t.TEXT_DIM,
                            font_family="monospace"),
            bgcolor=t.SURFACE2, border_radius=scaled(CUSTOM_BTN_RADIUS),
            padding=t.pad_sym(horizontal=scaled(CUSTOM_BTN_PAD_H), vertical=scaled(CUSTOM_BTN_PAD_V)),
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
                build_top_categories(month_receipts, self._mode, settings,
                                     on_category_click=self._open_category_detail),
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

    def _open_category_detail(self, category_id: str):
        self._in_category_detail = True
        self.controls.clear()
        detail = CategoryDetailScreen(
            app_state=self.app_state,
            category_id=category_id,
            mode=self._mode,
            year=self._year,
            month=self._month,
            on_back=self._close_category_detail,
            on_edit_receipt=self._on_edit_receipt or (lambda **kw: None),
        )
        self.controls.append(detail)
        self.update()

    def _close_category_detail(self):
        self._in_category_detail = False
        self._build()
        self.update()
