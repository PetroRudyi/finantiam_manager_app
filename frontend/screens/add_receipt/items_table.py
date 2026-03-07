# -*- coding: utf-8 -*-
"""Items table: column headers, item rows, add button, total display."""

from typing import Callable, List
import flet as ft

from backend.models import InvoiceItem, AppSettings
from backend.config import get_symbol
from frontend import theme as t


def build_column_headers() -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Text("Назва", size=8, color=t.TEXT_DIMMER,
                    font_family="monospace", expand=True),
            ft.Text("К-ть", size=8, color=t.TEXT_DIMMER,
                    font_family="monospace", width=30,
                    text_align=ft.TextAlign.CENTER),
            ft.Text("Ціна", size=8, color=t.TEXT_DIMMER,
                    font_family="monospace", width=58,
                    text_align=ft.TextAlign.RIGHT),
            ft.Text("Кат.", size=8, color=t.TEXT_DIMMER,
                    font_family="monospace", width=44,
                    text_align=ft.TextAlign.RIGHT),
            ft.Container(width=40),
        ], spacing=4),
        padding=t.pad_only(left=18, right=18, bottom=4),
    )


def build_add_row(on_click: Callable) -> ft.Container:
    return ft.Container(
        content=ft.Text("+ Додати позицію", size=11, color=t.ACCENT,
                        font_family="monospace"),
        padding=t.pad_only(left=18, top=8, bottom=4),
        on_click=on_click,
        ink=True,
    )


def build_item_row(item: InvoiceItem, idx: int, settings: AppSettings,
                   currency: str, on_edit: Callable, on_remove: Callable) -> ft.Container:
    cat_label = settings.get_category_name(item.category)[:6]
    return ft.Container(
        content=ft.Row([
            ft.Text(item.name, size=12, color=t.TEXT, expand=True,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    weight=ft.FontWeight.W_500),
            ft.Text(f"{item.quantity:g}", size=10, color=t.TEXT_DIM,
                    font_family="monospace", width=30,
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"{get_symbol(currency)}{item.price:.2f}", size=11, color=t.TEXT,
                    font_family="monospace", width=58,
                    text_align=ft.TextAlign.RIGHT),
            ft.Container(
                content=ft.Text(cat_label, size=8, color=t.TEXT_DIM,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER),
                bgcolor=t.SURFACE2, border_radius=4,
                padding=t.pad_sym(horizontal=5, vertical=2),
                width=44,
            ),
            ft.Row([
                ft.Container(
                    content=ft.Text("✎", size=9, color=t.ACCENT,
                                    font_family="monospace"),
                    width=18, height=18, border_radius=4,
                    bgcolor=t.alpha(t.ACCENT, "18"),
                    border=t.border_all(1, t.alpha(t.ACCENT, "44")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_edit(i),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("×", size=9, color=t.RED,
                                    font_family="monospace"),
                    width=18, height=18, border_radius=4,
                    bgcolor=t.alpha(t.RED, "18"),
                    border=t.border_all(1, t.alpha(t.RED, "33")),
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda e, i=idx: on_remove(i),
                    ink=True,
                ),
            ], spacing=2, width=40),
        ], spacing=4),
        padding=t.pad_only(left=18, right=18, top=7, bottom=7),
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
