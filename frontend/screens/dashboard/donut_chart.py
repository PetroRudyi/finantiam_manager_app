# -*- coding: utf-8 -*-
"""Categories donut chart with legend."""

import math
from typing import List
import flet as ft
import flet.canvas as cv

import backend
from backend.models import Receipt, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_SM, FONT_SM_MD, FONT_MD, LETTER_SPACING, PAD_PAGE_H, GAP_SM, GAP_LG
from frontend.screens.dashboard.sizes import (
    CARD_RADIUS, CARD_PAD, CARD_MARGIN_BOTTOM,
    DONUT_SIZE, DONUT_STROKE, LEGEND_DOT, LEGEND_DOT_RADIUS,
    LEGEND_GAP, LEGEND_CHART_GAP,
)


def build_donut_chart(receipts: List[Receipt], mode: str,
                      settings: AppSettings) -> ft.Container:
    cat_totals_ids = backend.get_category_totals(receipts, mode)
    cat_totals = {
        settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
    }
    grand = sum(cat_totals.values()) or 1

    legend_items = []
    chart_size = scaled(DONUT_SIZE)
    stroke = scaled(DONUT_STROKE)
    gap_angle = 0.06
    offset = stroke / 2
    rect_size = chart_size - stroke

    items = list(cat_totals.items())[:6]
    total_gap = gap_angle * len(items) if len(items) > 1 else 0
    available_angle = 2 * math.pi - total_gap

    shapes = []
    start = -math.pi / 2

    for i, (cat, val) in enumerate(items):
        pct = int(val / grand * 100)
        color = t.CATEGORY_COLORS[i % len(t.CATEGORY_COLORS)]
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
            ft.Container(width=scaled(LEGEND_DOT), height=scaled(LEGEND_DOT),
                         bgcolor=color, border_radius=scaled(LEGEND_DOT_RADIUS)),
            ft.Text(cat, size=scaled(FONT_SM_MD), color=t.TEXT_DIM, expand=True),
            ft.Text(f"{pct}%", size=scaled(FONT_SM_MD), color=t.TEXT, font_family="monospace"),
        ], spacing=scaled(LEGEND_GAP)))

    if not legend_items:
        legend_items.append(ft.Text(tr("dashboard.no_data"), size=scaled(FONT_MD), color=t.TEXT_DIMMER))

    if not shapes:
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
            ft.Text(tr("dashboard.categories_title"), size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
            ft.Row([
                chart,
                ft.Column(legend_items, spacing=scaled(GAP_SM), expand=True),
            ], spacing=scaled(LEGEND_CHART_GAP), vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ], spacing=scaled(GAP_LG)),
        bgcolor=t.SURFACE2, border_radius=scaled(CARD_RADIUS), padding=scaled(CARD_PAD),
        margin=t.mar_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H), bottom=scaled(CARD_MARGIN_BOTTOM)),
        border=t.border_all(),
    )
