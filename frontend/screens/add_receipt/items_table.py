# -*- coding: utf-8 -*-
"""Items table: column headers, item rows, add button, total display."""

from typing import Callable, List
import flet as ft

from backend.models import InvoiceItem, AppSettings
from backend.config import get_symbol
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import (
    FONT_XS, FONT_SM, FONT_SM_MD, FONT_MD, FONT_BODY,
    PAD_PAGE_H, GAP_XS, GAP_SM, BORDER_WIDTH,
    ICON_BTN_SM, ICON_BTN_RADIUS,
)
from frontend.screens.add_receipt.sizes import (
    COL_QTY_W, COL_PRICE_W, COL_CAT_W, COL_ACTIONS_W,
    TABLE_GAP, TABLE_ROW_PAD_V,
)


def build_column_headers() -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Text(tr("items_table.name"), size=scaled(FONT_XS), color=t.TEXT_DIMMER,
                    font_family="monospace", expand=True),
            ft.Text(tr("items_table.qty"), size=scaled(FONT_XS), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(COL_QTY_W),
                    text_align=ft.TextAlign.LEFT),
            ft.Text(tr("items_table.price"), size=scaled(FONT_XS), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(COL_PRICE_W),
                    text_align=ft.TextAlign.LEFT),
            ft.Text(tr("items_table.cat"), size=scaled(FONT_XS), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(COL_CAT_W),
                    text_align=ft.TextAlign.LEFT),
            ft.Container(width=scaled(COL_ACTIONS_W)),
        ], spacing=scaled(TABLE_GAP)),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H), bottom=scaled(TABLE_GAP)),
    )


def build_add_row(on_click: Callable) -> ft.Container:
    return ft.Container(
        content=ft.Text(tr("items_table.add_item"), size=scaled(FONT_MD), color=t.ACCENT,
                        font_family="monospace", text_align=ft.TextAlign.CENTER,
                        width=float("inf")),
        padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(8)),
        on_click=on_click,
        ink=True,
        border=t.border_bottom(),
    )


def build_item_row(item: InvoiceItem, idx: int, settings: AppSettings,
                   currency: str, on_edit: Callable, on_remove: Callable) -> ft.Container:
    cat_label = settings.get_category_name(item.category)
    return ft.Container(
        content=ft.Row([
            ft.Text(item.name, size=scaled(FONT_BODY), color=t.TEXT, expand=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    weight=ft.FontWeight.W_500),
            ft.Text(f"{item.quantity:g}", size=scaled(FONT_SM_MD), color=t.TEXT_DIM,
                    font_family="monospace", width=scaled(COL_QTY_W),
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"{item.price:.2f}", size=scaled(FONT_SM_MD), color=t.TEXT,
                    font_family="monospace", width=scaled(COL_PRICE_W),
                    text_align=ft.TextAlign.RIGHT),
            ft.Container(
                content=ft.Text(cat_label, size=scaled(FONT_SM_MD), color=t.TEXT_DIM,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1),
                bgcolor=t.SURFACE2, border_radius=scaled(ICON_BTN_RADIUS),
                padding=t.pad_sym(horizontal=scaled(3), vertical=scaled(2)),
                width=scaled(COL_CAT_W),
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            ),
            ft.Row([
                ft.Container(
                    content=ft.Text("✎", size=scaled(FONT_SM), color=t.ACCENT,
                                    font_family="monospace"),
                    width=scaled(ICON_BTN_SM), height=scaled(ICON_BTN_SM), border_radius=scaled(ICON_BTN_RADIUS),
                    bgcolor=t.alpha(t.ACCENT, "18"),
                    border=t.border_all(scaled(BORDER_WIDTH), t.alpha(t.ACCENT, "44")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_edit(i),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("×", size=scaled(FONT_SM), color=t.RED,
                                    font_family="monospace"),
                    width=scaled(ICON_BTN_SM), height=scaled(ICON_BTN_SM), border_radius=scaled(ICON_BTN_RADIUS),
                    bgcolor=t.alpha(t.RED, "18"),
                    border=t.border_all(scaled(BORDER_WIDTH), t.alpha(t.RED, "33")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_remove(i),
                    ink=True,
                ),
            ], spacing=scaled(GAP_XS), width=scaled(COL_ACTIONS_W)),
        ], spacing=scaled(TABLE_GAP)),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           top=scaled(TABLE_ROW_PAD_V), bottom=scaled(TABLE_ROW_PAD_V)),
        border=t.border_bottom(),
    )


def update_total_text(total_text: ft.Text, items: List[InvoiceItem],
                      tx_type: str, currency: str):
    total = sum(i.price for i in items)
    sign = "−" if tx_type == "expense" else "+"
    color = t.RED if tx_type == "expense" else t.BLUE
    symbol = get_symbol(currency)
    total_text.value = f"{sign}{symbol}{total:,.2f}"
    total_text.color = color
    try:
        total_text.update()
    except Exception:
        pass
