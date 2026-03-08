# -*- coding: utf-8 -*-
"""Summary bar showing income, expenses, and balance."""

import flet as ft
from frontend import theme as t
from frontend.localisation import t as tr


def build_summary_row(summary: dict, base_currency: str) -> ft.Container:
    def stat(lbl, val, color):
        return ft.Column([
            ft.Text(lbl.upper(), size=9, color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=1.2)),
            ft.Text(t.format_amount(val, currency=base_currency), size=14, color=color,
                    weight=ft.FontWeight.W_600, font_family="monospace"),
        ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Row([
            stat(tr("summary.income"),   summary["income"],   t.BLUE),
            ft.VerticalDivider(width=1, color=t.BORDER),
            stat(tr("summary.expenses"), summary["expenses"], t.RED),
            ft.VerticalDivider(width=1, color=t.BORDER),
            stat(tr("summary.balance"), summary["balance"],  t.TEXT),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=t.pad_only(left=18, right=18, bottom=10, top=4),
        border=t.border_bottom(),
    )
