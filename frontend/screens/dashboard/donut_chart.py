# -*- coding: utf-8 -*-
"""Categories pie chart with on-chart labels and leader lines."""

import math
from typing import List
import flet as ft
import flet.canvas as cv

import backend
from backend.models import Receipt, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_XS, FONT_SM, FONT_SM_MD, LETTER_SPACING, PAD_PAGE_H, GAP_LG
from frontend.screens.dashboard.sizes import (
    CARD_RADIUS, CARD_PAD, CARD_MARGIN_BOTTOM,
    LEGEND_DOT_RADIUS,
)

# Layout constants (design px at base 390px screen)
_SCREEN_BASE = 390
_LINE_EXT = 12   # radial line length past pie edge
_HORIZ    = 14   # horizontal leader line extension
_TEXT_W   = 50   # max label text width
_LINE_W   = 0.9  # leader line stroke width

# Font sizes for on-chart labels
_FONT_NAME = 11  # category name label
_FONT_PCT  = 9   # percentage label
_COLOR_PCT = "#c0c0ce"  # light gray for percentage text


def build_donut_chart(receipts: List[Receipt], mode: str,
                      settings: AppSettings) -> ft.Container:
    cat_totals_ids = backend.get_category_totals(receipts, mode)
    cat_totals = {
        settings.get_category_name(cid): val for cid, val in cat_totals_ids.items()
    }
    grand = sum(cat_totals.values()) or 1

    # Top-6 + "others" grouping (same as before)
    all_items = list(cat_totals.items())
    top_items = all_items[:6]
    rest = all_items[6:]
    if rest:
        other_val = sum(v for _, v in rest)
        top_items = top_items + [(tr("dashboard.other_categories"), other_val)]
    items = top_items

    # Compute canvas width from available card space
    card_inner = _SCREEN_BASE - 2 * PAD_PAGE_H - 2 * CARD_PAD
    cw = scaled(card_inner)
    # Pie radius fills available width after subtracting label margins on both sides
    line_ext = scaled(_LINE_EXT)
    horiz = scaled(_HORIZ)
    text_w = scaled(_TEXT_W)
    line_w = scaled(_LINE_W)
    label_margin = line_ext + horiz + text_w
    pie_r = (cw / 2) - label_margin
    # Asymmetric vertical padding: top needs less space than bottom
    font_name_sz = scaled(_FONT_NAME)
    font_pct_sz = scaled(_FONT_PCT)
    max_label_h = 2 * font_name_sz * 1.25 + font_pct_sz * 1.25
    v_pad_top = line_ext + font_name_sz * 1.25  # top labels: only ~1 line of name
    v_pad_bot = line_ext + max_label_h           # bottom labels: 2-line name + pct
    ch = pie_r * 2 + v_pad_top + v_pad_bot
    cx = cw / 2
    cy = v_pad_top + pie_r  # pie center shifted up

    gap_angle = 0
    available_angle = 2 * math.pi

    shapes = []
    start = -math.pi / 2

    if not items:
        shapes.append(cv.Arc(
            x=cx - pie_r, y=cy - pie_r,
            width=pie_r * 2, height=pie_r * 2,
            start_angle=0, sweep_angle=2 * math.pi,
            use_center=False,
            paint=ft.Paint(color=t.TEXT_DIMMER, stroke_width=pie_r * 0.6,
                           style=ft.PaintingStyle.STROKE),
        ))
    else:
        for i, (cat, val) in enumerate(items):
            pct = val / grand * 100
            color = t.CATEGORY_COLORS[i % len(t.CATEGORY_COLORS)]
            sweep = (val / grand) * available_angle if grand > 0 else 0

            # Filled pie segment
            shapes.append(cv.Arc(
                x=cx - pie_r, y=cy - pie_r,
                width=pie_r * 2, height=pie_r * 2,
                start_angle=start,
                sweep_angle=sweep,
                use_center=True,
                paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL),
            ))


            # Leader line
            mid_angle = start + sweep / 2
            # Start point: on the pie edge
            lx1 = cx + pie_r * math.cos(mid_angle)
            ly1 = cy + pie_r * math.sin(mid_angle)
            # End point: outside pie
            lx2 = cx + (pie_r + line_ext) * math.cos(mid_angle)
            ly2 = cy + (pie_r + line_ext) * math.sin(mid_angle)
            # Horizontal elbow
            is_right = math.cos(mid_angle) >= 0
            lx3 = lx2 + (horiz if is_right else -horiz)

            line_paint = ft.Paint(
                color=color, stroke_width=line_w,
                style=ft.PaintingStyle.STROKE,
            )
            shapes.append(cv.Line(lx1, ly1, lx2, ly2, paint=line_paint))
            shapes.append(cv.Line(lx2, ly2, lx3, ly2, paint=line_paint))

            # Text starts at lx3+gap (right side) or lx3-text_w-gap (left side)
            # so it never overlaps the pie
            if is_right:
                tx = lx3 + scaled(2)
            else:
                tx = lx3 - text_w - scaled(2)
            # Estimate how many lines the category name will occupy
            char_w = font_name_sz * 0.55  # approximate average char width
            text_pixel_w = len(cat) * char_w
            name_lines = max(1, math.ceil(text_pixel_w / text_w))
            name_block_h = name_lines * font_name_sz * 1.25  # line height

            shapes.append(cv.Text(
                x=tx, y=ly2 - scaled(7),
                value=cat,
                style=ft.TextStyle(
                    size=font_name_sz,
                    color=color,
                    weight=ft.FontWeight.W_600,
                ),
                text_align=ft.TextAlign.LEFT,
                max_width=text_w,
            ))
            pct_y = ly2 - scaled(7) + name_block_h + scaled(1)
            shapes.append(cv.Text(
                x=tx, y=pct_y,
                value=f"{pct:.1f} %",
                style=ft.TextStyle(
                    size=scaled(_FONT_PCT),
                    color=_COLOR_PCT,
                ),
                text_align=ft.TextAlign.LEFT,
                max_width=text_w,
            ))

            start += sweep

    chart = cv.Canvas(shapes, width=cw, height=ch)

    return ft.Container(
        content=ft.Column([
            ft.Text(tr("dashboard.categories_title"),
                    size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
            ft.Row([chart], alignment=ft.MainAxisAlignment.CENTER),
        ], spacing=scaled(2)),
        bgcolor=t.SURFACE2, border_radius=scaled(CARD_RADIUS), padding=scaled(CARD_PAD),
        margin=t.mar_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                          bottom=scaled(CARD_MARGIN_BOTTOM)),
        border=t.border_all(),
    )
