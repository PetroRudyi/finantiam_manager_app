# -*- coding: utf-8 -*-
"""
frontend/screen_dashboard.py
Screen 03 — Analytics: bar chart + donut chart + category breakdown.
Compatible with Flet >= 0.80.0
"""

import datetime
import math
import flet as ft
import flet.canvas as cv
from typing import List

import backend
from backend.models import Receipt, AppSettings
from frontend import theme as t

# English-to-Ukrainian short month labels for chart axis
_ENG_TO_UA = {
    "Jan": "Сі", "Feb": "Лю", "Mar": "Бе", "Apr": "Кв",
    "May": "Тр", "Jun": "Чр", "Jul": "Лп", "Aug": "Сп",
    "Sep": "Ве", "Oct": "Жо", "Nov": "Лс", "Dec": "Гр",
}

CATEGORY_COLORS = ["#ff4d5a", "#ffb240", "#7c6aff", "#3d9bff",
                   "#3dcc8e", "#e5a35a", "#a8d5a2"]

class DashboardScreen(ft.Column):
    def __init__(self, app_state: dict):
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
        receipts: List[Receipt] = self.app_state.get("receipts", [])

        # Filter by selected month
        month_receipts = [
            r for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]

        self.controls += [
            self._period_nav(),
            self._type_toggle(),
            ft.Column([
                self._bar_chart(receipts),
                self._categories_card(month_receipts),
                self._top_categories(month_receipts),
            ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
        ]

    # ── Period nav ────────────────────────────────────────────

    def _period_nav(self) -> ft.Container:
        month_label = f"{t.UA_MONTHS_SHORT[self._month]} {self._year}"
        return ft.Container(
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
                ft.Container(
                    content=ft.Text("Кастом", size=9, color=t.TEXT_DIM,
                                    font_family="monospace"),
                    bgcolor=t.SURFACE2, border_radius=8,
                    padding=t.pad_sym(horizontal=10, vertical=5),
                    border=t.border_all(),
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=18, right=18, top=4, bottom=10),
        )

    # ── Type toggle ───────────────────────────────────────────

    def _type_toggle(self) -> ft.Container:
        def btn(label, mode):
            active = self._mode == mode
            return ft.Container(
                content=ft.Text(label, size=10,
                                color=t.TEXT if active else t.TEXT_DIMMER,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER),
                expand=True,
                bgcolor=t.SURFACE if active else "transparent",
                border_radius=7,
                padding=t.pad_sym(vertical=5),
                on_click=lambda e, m=mode: self._set_mode(m),
                ink=True,
            )
        return ft.Container(
            content=ft.Row([btn("Витрати", "expense"), btn("Дохід", "income")],
                           spacing=0),
            bgcolor=t.SURFACE2, border_radius=9, padding=3,
            margin=t.mar_only(left=18, right=18, bottom=8),
        )

    # ── Bar chart ─────────────────────────────────────────────

    def _bar_chart(self, receipts: List[Receipt]) -> ft.Container:
        totals = backend.get_monthly_totals(
            receipts, self._mode,
            target_year=self._year, target_month=self._month,
        )
        max_v = max(totals.values()) if any(totals.values()) else 1
        chart_color = t.RED if self._mode == "expense" else t.BLUE

        # Selected month is penultimate (index 4 of 6)
        selected_idx = 4
        items = list(totals.items())
        selected_total = items[selected_idx][1] if len(items) > selected_idx else 0

        bars = []
        for i, (month, val) in enumerate(items):
            is_selected = i == selected_idx
            height = max(4, int((val / max_v) * 55)) if max_v > 0 else 4
            ua_label = _ENG_TO_UA.get(month, month)
            bars.append(ft.Column([
                ft.Container(
                    height=height, bgcolor=chart_color,
                    border_radius=ft.BorderRadius(top_left=3, top_right=3,
                                                  bottom_left=0, bottom_right=0),
                    opacity=1.0 if is_selected else 0.5,
                ),
                ft.Text(ua_label, size=8,
                        color=t.ACCENT if is_selected else t.TEXT_DIMMER,
                        font_family="monospace"),
            ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               expand=True))

        return ft.Container(
            content=ft.Column([
                ft.Text("ТРЕНД ПО МІСЯЦЯХ", size=9, color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=1.2)),
                ft.Text(t.format_amount(selected_total,
                        currency=self.app_state["settings"].default_currency),
                        size=20, color=chart_color,
                        font_family="monospace", weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.Row(bars, spacing=4,
                                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    height=72,
                ),
            ], spacing=8),
            bgcolor=t.SURFACE2, border_radius=12, padding=12,
            margin=t.mar_only(left=18, right=18, bottom=10),
            border=t.border_all(),
        )

    # ── Categories card with donut chart ──────────────────────

    def _categories_card(self, receipts: List[Receipt]) -> ft.Container:
        settings: AppSettings = self.app_state["settings"]
        cat_totals_ids = backend.get_category_totals(receipts, self._mode)
        cat_totals = {
            settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
        }
        grand = sum(cat_totals.values()) or 1

        legend_items = []
        chart_size = 90
        stroke = 18
        gap_angle = 0.06  # small gap between segments in radians
        offset = stroke / 2
        rect_size = chart_size - stroke

        items = list(cat_totals.items())[:6]
        total_gap = gap_angle * len(items) if len(items) > 1 else 0
        available_angle = 2 * math.pi - total_gap

        shapes = []
        start = -math.pi / 2  # start from top

        for i, (cat, val) in enumerate(items):
            pct = int(val / grand * 100)
            color = CATEGORY_COLORS[i % len(CATEGORY_COLORS)]
            sweep = (val / grand) * available_angle if grand > 0 else 0

            shapes.append(cv.Arc(
                x=offset, y=offset,
                width=rect_size, height=rect_size,
                start_angle=start,
                sweep_angle=sweep,
                use_center=False,
                paint=ft.Paint(
                    color=color,
                    stroke_width=stroke,
                    style=ft.PaintingStyle.STROKE,
                    stroke_cap=ft.StrokeCap.BUTT,
                ),
            ))
            start += sweep + (gap_angle if len(items) > 1 else 0)

            legend_items.append(ft.Row([
                ft.Container(width=6, height=6, bgcolor=color, border_radius=2),
                ft.Text(cat, size=10, color=t.TEXT_DIM, expand=True),
                ft.Text(f"{pct}%", size=10, color=t.TEXT, font_family="monospace"),
            ], spacing=5))

        if not legend_items:
            legend_items.append(ft.Text("Немає даних", size=11, color=t.TEXT_DIMMER))

        if not shapes:
            # Empty state — gray ring
            shapes.append(cv.Arc(
                x=offset, y=offset,
                width=rect_size, height=rect_size,
                start_angle=0,
                sweep_angle=2 * math.pi,
                use_center=False,
                paint=ft.Paint(
                    color=t.TEXT_DIMMER,
                    stroke_width=stroke,
                    style=ft.PaintingStyle.STROKE,
                ),
            ))

        chart = cv.Canvas(shapes, width=chart_size, height=chart_size)

        return ft.Container(
            content=ft.Column([
                ft.Text("КАТЕГОРІЇ", size=9, color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=1.2)),
                ft.Row([
                    chart,
                    ft.Column(legend_items, spacing=4, expand=True),
                ], spacing=14, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], spacing=8),
            bgcolor=t.SURFACE2, border_radius=12, padding=12,
            margin=t.mar_only(left=18, right=18, bottom=10),
            border=t.border_all(),
        )

    # ── Top categories list ───────────────────────────────────

    def _top_categories(self, receipts: List[Receipt]) -> ft.Column:
        settings: AppSettings = self.app_state["settings"]
        cat_totals_ids = backend.get_category_totals(receipts, self._mode)
        cat_totals = {
            settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
        }
        max_val = max(cat_totals.values()) if cat_totals else 1
        grand = sum(cat_totals.values()) or 1

        header = ft.Container(
            content=ft.Text("ТОП КАТЕГОРІЙ", size=9, color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=1.2)),
            padding=t.pad_only(left=18, right=18, top=6, bottom=4),
        )

        rows = [header]
        for i, (cat, val) in enumerate(list(cat_totals.items())[:8]):
            bar_fraction = val / max_val if max_val > 0 else 0
            bar_width = max(4, int(bar_fraction * 160))
            color = CATEGORY_COLORS[i % len(CATEGORY_COLORS)]
            pct = int(val / grand * 100)

            rows.append(ft.Container(
                content=ft.Row([
                    ft.Text(str(i + 1), size=9, color=t.TEXT_DIMMER,
                            font_family="monospace", width=14),
                    ft.Column([
                        ft.Text(cat, size=12, color=t.TEXT,
                                weight=ft.FontWeight.W_500),
                        ft.Container(
                            width=bar_width, height=3,
                            bgcolor=color, border_radius=2,
                        ),
                    ], spacing=4, expand=True),
                    ft.Text(f"{t.format_amount(val, currency=settings.default_currency)}, {pct}%",
                            size=12, color=color, font_family="monospace",
                            weight=ft.FontWeight.W_500),
                ], spacing=8),
                padding=t.pad_only(left=18, right=18, top=7, bottom=7),
                border=t.border_bottom(),
            ))

        if not cat_totals:
            rows.append(ft.Container(
                content=ft.Text("Немає даних", size=12, color=t.TEXT_DIMMER,
                                text_align=ft.TextAlign.CENTER),
                padding=30, alignment=ft.Alignment(0, 0),
            ))

        return ft.Column(rows, spacing=0)

    # ── Handlers ──────────────────────────────────────────────

    def _prev_month(self):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self._build()
        self.update()

    def _next_month(self):
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self._build()
        self.update()

    def _set_mode(self, mode: str):
        self._mode = mode
        self._build()
        self.update()
