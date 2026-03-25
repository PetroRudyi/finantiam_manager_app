# -*- coding: utf-8 -*-
"""Top categories ranked list with progress bars."""

from typing import List
import flet as ft

import backend
from backend.models import Receipt, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr


def build_top_categories(receipts: List[Receipt], mode: str,
                         settings: AppSettings) -> ft.Column:
    cat_totals_ids = backend.get_category_totals(receipts, mode)
    cat_totals = {
        settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
    }
    max_val = max(cat_totals.values()) if cat_totals else 1
    grand = sum(cat_totals.values()) or 1

    header = ft.Container(
        content=ft.Text(tr("dashboard.top_categories"), size=scaled(9), color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=scaled(1.2))),
        padding=t.pad_only(left=scaled(18), right=scaled(18), top=scaled(6), bottom=scaled(4)),
    )

    rows = [header]
    for i, (cat, val) in enumerate(list(cat_totals.items())[:8]):
        bar_fraction = val / max_val if max_val > 0 else 0
        bar_width = max(scaled(4), int(bar_fraction * scaled(160)))
        color = t.CATEGORY_COLORS[i % len(t.CATEGORY_COLORS)]
        pct = int(val / grand * 100)

        rows.append(ft.Container(
            content=ft.Row([
                ft.Text(str(i + 1), size=scaled(9), color=t.TEXT_DIMMER,
                        font_family="monospace", width=scaled(14)),
                ft.Column([
                    ft.Text(cat, size=scaled(12), color=t.TEXT,
                            weight=ft.FontWeight.W_500),
                    ft.Container(
                        width=bar_width, height=scaled(3),
                        bgcolor=color, border_radius=scaled(2),
                    ),
                ], spacing=scaled(4), expand=True),
                ft.Text(f"{t.format_amount(val, currency=settings.default_currency)}, {pct}%",
                        size=scaled(12), color=color, font_family="monospace",
                        weight=ft.FontWeight.W_500),
            ], spacing=scaled(8)),
            padding=t.pad_only(left=scaled(18), right=scaled(18), top=scaled(7), bottom=scaled(7)),
            border=t.border_bottom(),
        ))

    if not cat_totals:
        rows.append(ft.Container(
            content=ft.Text(tr("dashboard.no_data"), size=scaled(12), color=t.TEXT_DIMMER,
                            text_align=ft.TextAlign.CENTER),
            padding=scaled(30), alignment=ft.Alignment(0, 0),
        ))

    return ft.Column(rows, spacing=0)
