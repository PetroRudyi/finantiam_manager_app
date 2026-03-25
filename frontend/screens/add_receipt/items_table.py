# -*- coding: utf-8 -*-
"""Items table: column headers, item rows, add button, total display."""

from typing import Callable, List
import flet as ft

from backend.models import InvoiceItem, AppSettings
from backend.config import get_symbol
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr


def build_column_headers() -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Text(tr("items_table.name"), size=scaled(8), color=t.TEXT_DIMMER,
                    font_family="monospace", expand=True),
            ft.Text(tr("items_table.qty"), size=scaled(8), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(30),
                    text_align=ft.TextAlign.CENTER),
            ft.Text(tr("items_table.price"), size=scaled(8), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(58),
                    text_align=ft.TextAlign.RIGHT),
            ft.Text(tr("items_table.cat"), size=scaled(8), color=t.TEXT_DIMMER,
                    font_family="monospace", width=scaled(44),
                    text_align=ft.TextAlign.RIGHT),
            ft.Container(width=scaled(40)),
        ], spacing=scaled(4)),
        padding=t.pad_only(left=scaled(18), right=scaled(18), bottom=scaled(4)),
    )


def build_add_row(on_click: Callable) -> ft.Container:
    return ft.Container(
        content=ft.Text(tr("items_table.add_item"), size=scaled(11), color=t.ACCENT,
                        font_family="monospace"),
        padding=t.pad_only(left=scaled(18), top=scaled(8), bottom=scaled(4)),
        on_click=on_click,
        ink=True,
    )


def build_item_row(item: InvoiceItem, idx: int, settings: AppSettings,
                   currency: str, on_edit: Callable, on_remove: Callable) -> ft.Container:
    cat_label = settings.get_category_name(item.category)[:6]
    return ft.Container(
        content=ft.Row([
            ft.Text(item.name, size=scaled(12), color=t.TEXT, expand=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    weight=ft.FontWeight.W_500),
            ft.Text(f"{item.quantity:g}", size=scaled(10), color=t.TEXT_DIM,
                    font_family="monospace", width=scaled(30),
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"{get_symbol(currency)}{item.price:.2f}", size=scaled(11), color=t.TEXT,
                    font_family="monospace", width=scaled(58),
                    text_align=ft.TextAlign.RIGHT),
            ft.Container(
                content=ft.Text(cat_label, size=scaled(8), color=t.TEXT_DIM,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER),
                bgcolor=t.SURFACE2, border_radius=scaled(4),
                padding=t.pad_sym(horizontal=scaled(5), vertical=scaled(2)),
                width=scaled(44),
            ),
            ft.Row([
                ft.Container(
                    content=ft.Text("✎", size=scaled(9), color=t.ACCENT,
                                    font_family="monospace"),
                    width=scaled(18), height=scaled(18), border_radius=scaled(4),
                    bgcolor=t.alpha(t.ACCENT, "18"),
                    border=t.border_all(scaled(1), t.alpha(t.ACCENT, "44")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_edit(i),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("×", size=scaled(9), color=t.RED,
                                    font_family="monospace"),
                    width=scaled(18), height=scaled(18), border_radius=scaled(4),
                    bgcolor=t.alpha(t.RED, "18"),
                    border=t.border_all(scaled(1), t.alpha(t.RED, "33")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_remove(i),
                    ink=True,
                ),
            ], spacing=scaled(2), width=scaled(40)),
        ], spacing=scaled(4)),
        padding=t.pad_only(left=scaled(18), right=scaled(18), top=scaled(7), bottom=scaled(7)),
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
