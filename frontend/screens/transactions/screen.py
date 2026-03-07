# -*- coding: utf-8 -*-
"""
frontend/screens/transactions/screen.py
Screen 01 — Transactions list (Daily / Weekly / Total tabs, multi-select).
"""

import datetime
import flet as ft
from typing import Callable, Set

import backend
from frontend.components.month_navigator import MonthNavigator
from frontend.screens.transactions.summary_row import build_summary_row
from frontend.screens.transactions.period_tabs import build_period_tabs
from frontend.screens.transactions.selection_bar import build_selection_bar
from frontend.screens.transactions.receipt_list import build_receipt_list
from frontend import theme as t


TAB_MODES = ["daily", "weekly", "total"]


class TransactionsScreen(ft.Column):
    def __init__(self, app_state, on_add: Callable, on_refresh: Callable):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_add = on_add
        self.on_refresh = on_refresh
        self.tab_mode = "daily"
        self.selected_ids: Set[str] = set()
        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        self._build()

    def refresh(self):
        self._build()
        self.update()

    def _build(self):
        self.controls.clear()
        receipts = self.app_state.receipts

        month_receipts = [
            r for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]

        summary = backend.get_summary(month_receipts)

        if self.tab_mode in ("daily", "total"):
            filtered = month_receipts
        elif self.tab_mode == "weekly":
            month_start = datetime.date(self._year, self._month, 1)
            if self._month == 12:
                next_month = datetime.date(self._year + 1, 1, 1)
            else:
                next_month = datetime.date(self._year, self._month + 1, 1)
            month_end = next_month - datetime.timedelta(days=1)
            start_week = month_start - datetime.timedelta(days=month_start.weekday())
            end_week = month_end + datetime.timedelta(days=(6 - month_end.weekday()))
            filtered = [
                r for r in receipts
                if start_week <= r.created_date.date() <= end_week
            ]
        else:
            filtered = receipts

        extra_right = ft.Row([
            ft.Container(
                content=ft.Text("✓", size=12, color=t.TEXT_DIM, font_family="monospace"),
                width=30, height=30, border_radius=8,
                bgcolor=t.SURFACE2, border=t.border_all(),
                alignment=ft.Alignment(0, 0),
                on_click=lambda e: self._toggle_select_all(),
                ink=True,
            ),
            ft.Container(
                content=ft.Text("···", size=12, color=t.TEXT_DIM, font_family="monospace"),
                width=30, height=30, border_radius=8,
                bgcolor=t.SURFACE2, border=t.border_all(),
                alignment=ft.Alignment(0, 0),
                ink=True,
            ),
        ], spacing=6)

        self.controls += [
            MonthNavigator(self._year, self._month,
                           on_change=self._on_month_change,
                           extra_right=extra_right),
            build_summary_row(summary, self.app_state.settings.default_currency),
            build_period_tabs(self.tab_mode, self._set_tab),
        ]
        if self.selected_ids:
            self.controls.append(
                build_selection_bar(self.selected_ids,
                                    self._delete_selected,
                                    self._change_date_selected))

        receipt_col = build_receipt_list(
            filtered, self.tab_mode, self.selected_ids,
            self.app_state, self._toggle_select, self.on_add)

        swipeable = ft.GestureDetector(
            content=receipt_col,
            on_horizontal_drag_end=self._on_swipe,
            expand=True,
        )
        self.controls.append(swipeable)

    # ── Handlers ─────────────────────────────────────────────

    def _on_month_change(self, year: int, month: int):
        self._year = year
        self._month = month
        self.selected_ids.clear()
        self._build()
        self.update()

    def _toggle_select_all(self):
        receipts = self.app_state.receipts
        month_receipts = [
            r for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]
        all_ids = {r.id for r in month_receipts}
        if self.selected_ids == all_ids:
            self.selected_ids.clear()
        else:
            self.selected_ids = all_ids
        self._build()
        self.update()

    def _on_swipe(self, e: ft.DragEndEvent):
        vx = e.velocity.x if e.velocity else 0
        if abs(vx) < 100:
            return
        idx = TAB_MODES.index(self.tab_mode)
        if vx < 0 and idx < len(TAB_MODES) - 1:
            self._set_tab(TAB_MODES[idx + 1])
        elif vx > 0 and idx > 0:
            self._set_tab(TAB_MODES[idx - 1])

    def _set_tab(self, mode: str):
        self.tab_mode = mode
        self.selected_ids.clear()
        self._build()
        self.update()

    def _toggle_select(self, rid: str):
        if rid in self.selected_ids:
            self.selected_ids.discard(rid)
        else:
            self.selected_ids.add(rid)
        self._build()
        self.update()

    def _delete_selected(self, e):
        if not self.selected_ids:
            return
        self.app_state.receipts = backend.delete_receipts(list(self.selected_ids))
        self.selected_ids.clear()
        self._build()
        self.update()

    def _change_date_selected(self, e):
        def on_picked(ev):
            picked = ev.control.value
            if picked:
                new_dt = datetime.datetime.combine(picked, datetime.time(12, 0))
                self.app_state.receipts = backend.update_receipts_date(
                    list(self.selected_ids), new_dt)
                self.selected_ids.clear()
                self._build()
                self.update()

        dp = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=on_picked,
        )
        self.page.show_dialog(dp)
