# -*- coding: utf-8 -*-
"""Monthly trend bar chart."""

from typing import List
import flet as ft

import backend
from backend.models import Receipt
from frontend import theme as t
from frontend.localisation import t as tr

_ENG_MONTH_TO_NUM = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def build_bar_chart(receipts: List[Receipt], mode: str,
                    year: int, month: int, base_currency: str) -> ft.Container:
    totals = backend.get_monthly_totals(
        receipts, mode, target_year=year, target_month=month,
    )
    max_v = max(totals.values()) if any(totals.values()) else 1
    chart_color = t.RED if mode == "expense" else t.BLUE

    selected_idx = 4
    items = list(totals.items())
    selected_total = items[selected_idx][1] if len(items) > selected_idx else 0

    bars = []
    months_chart = t.get_months_chart()
    for i, (month_label, val) in enumerate(items):
        is_selected = i == selected_idx
        height = max(4, int((val / max_v) * 55)) if max_v > 0 else 4
        month_num = _ENG_MONTH_TO_NUM.get(month_label, 0)
        chart_label = months_chart.get(month_num, month_label)
        bars.append(ft.Column([
            ft.Container(
                height=height, bgcolor=chart_color,
                border_radius=ft.BorderRadius(top_left=3, top_right=3,
                                              bottom_left=0, bottom_right=0),
                opacity=1.0 if is_selected else 0.5,
            ),
            ft.Text(chart_label, size=8,
                    color=t.ACCENT if is_selected else t.TEXT_DIMMER,
                    font_family="monospace"),
        ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
           expand=True))

    return ft.Container(
        content=ft.Column([
            ft.Text(tr("dashboard.trend_title"), size=9, color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=1.2)),
            ft.Text(t.format_amount(selected_total, currency=base_currency),
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
