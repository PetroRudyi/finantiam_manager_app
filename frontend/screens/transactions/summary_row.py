# -*- coding: utf-8 -*-
"""Summary bar showing income, expenses, and balance."""

import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr


def build_summary_row(summary: dict, base_currency: str) -> ft.Container:
    def stat(lbl, val, color):
        return ft.Column([
            ft.Text(lbl.upper(), size=scaled(9), color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=scaled(1.2))),
            ft.Text(t.format_amount(val, currency=base_currency), size=scaled(14), color=color,
                    weight=ft.FontWeight.W_600, font_family="monospace"),
        ], spacing=scaled(3), horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Row([
            stat(tr("summary.income"),   summary["income"],   t.BLUE),
            ft.VerticalDivider(width=scaled(1), color=t.BORDER),
            stat(tr("summary.expenses"), summary["expenses"], t.RED),
            ft.VerticalDivider(width=scaled(1), color=t.BORDER),
            stat(tr("summary.balance"), summary["balance"],  t.TEXT),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=t.pad_only(left=scaled(18), right=scaled(18), bottom=scaled(10), top=scaled(4)),
        border=t.border_bottom(),
    )
