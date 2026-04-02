# -*- coding: utf-8 -*-
"""Monthly trend line chart (replaces former bar chart)."""

from typing import List
import flet as ft

import backend
from backend.models import Receipt
from frontend import theme as t
from frontend.localisation import t as tr
from frontend.screens.dashboard.line_chart import build_line_chart


def build_bar_chart(receipts: List[Receipt], mode: str,
                    year: int, month: int, base_currency: str) -> ft.Container:
    totals = backend.get_monthly_totals(
        receipts, mode, target_year=year, target_month=month,
    )
    chart_color = t.RED if mode == "expense" else t.BLUE

    return build_line_chart(
        totals=totals,
        chart_color=chart_color,
        base_currency=base_currency,
        title=tr("dashboard.trend_title"),
        selected_idx=4,
    )
