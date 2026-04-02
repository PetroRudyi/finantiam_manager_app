# -*- coding: utf-8 -*-
"""Top categories ranked list with progress bars."""

from typing import List
import flet as ft

import backend
from backend.models import Receipt, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_SM, FONT_BODY, LETTER_SPACING, PAD_PAGE_H, GAP_SM, GAP_LG
from frontend.screens.dashboard.sizes import (
    TOP_CAT_BAR_MAX_W, TOP_CAT_BAR_H, TOP_CAT_BAR_MIN_W,
    RANK_NUM_W, ROW_PAD_V, HEADER_PAD_TOP, HEADER_PAD_BOTTOM,
    LEGEND_DOT_RADIUS, EMPTY_PAD,
)


def build_top_categories(receipts: List[Receipt], mode: str,
                         settings: AppSettings,
                         on_category_click=None) -> ft.Column:
    cat_totals_ids = backend.get_category_totals(receipts, mode)
    cat_totals = {
        settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
    }
    # Keep ID mapping for click handler
    cat_id_by_name = {
        settings.get_category_name(cid): cid for cid in cat_totals_ids.keys()
    }
    max_val = max(cat_totals.values()) if cat_totals else 1
    grand = sum(cat_totals.values()) or 1

    header = ft.Container(
        content=ft.Text(tr("dashboard.top_categories"), size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           top=scaled(HEADER_PAD_TOP), bottom=scaled(HEADER_PAD_BOTTOM)),
    )

    category_rows = []
    for i, (cat, val) in enumerate(cat_totals.items()):
        bar_fraction = val / max_val if max_val > 0 else 0
        bar_width = max(scaled(TOP_CAT_BAR_MIN_W), int(bar_fraction * scaled(TOP_CAT_BAR_MAX_W)))
        color = t.CATEGORY_COLORS[i % len(t.CATEGORY_COLORS)]
        pct = int(val / grand * 100)

        cid = cat_id_by_name.get(cat, cat)
        category_rows.append(ft.Container(
            content=ft.Row([
                ft.Text(str(i + 1), size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                        font_family="monospace", width=scaled(RANK_NUM_W)),
                ft.Column([
                    ft.Text(cat, size=scaled(FONT_BODY), color=t.TEXT,
                            weight=ft.FontWeight.W_500),
                    ft.Container(
                        width=bar_width, height=scaled(TOP_CAT_BAR_H),
                        bgcolor=color, border_radius=scaled(LEGEND_DOT_RADIUS),
                    ),
                ], spacing=scaled(GAP_SM), expand=True),
                ft.Text(f"{t.format_amount(val, currency=settings.default_currency)}, {pct}%",
                        size=scaled(FONT_BODY), color=color, font_family="monospace",
                        weight=ft.FontWeight.W_500),
            ], spacing=scaled(GAP_LG)),
            padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                               top=scaled(ROW_PAD_V), bottom=scaled(ROW_PAD_V)),
            border=t.border_bottom(),
            on_click=(lambda e, c=cid: on_category_click(c)) if on_category_click else None,
            ink=True if on_category_click else False,
        ))

    if not cat_totals:
        category_rows.append(ft.Container(
            content=ft.Text(tr("dashboard.no_data"), size=scaled(FONT_BODY), color=t.TEXT_DIMMER,
                            text_align=ft.TextAlign.CENTER),
            padding=scaled(EMPTY_PAD), alignment=ft.Alignment(0, 0),
        ))

    return ft.Column([
        header,
        ft.Column(category_rows, spacing=0, scroll=ft.ScrollMode.AUTO),
    ], spacing=0)
