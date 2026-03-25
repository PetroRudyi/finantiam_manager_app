# -*- coding: utf-8 -*-
"""Summary bar showing income, expenses, and balance."""

import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import FONT_SM, LETTER_SPACING, PAD_PAGE_H, BORDER_WIDTH
from frontend.screens.transactions.sizes import (
    SUMMARY_AMOUNT_FONT, SUMMARY_LABEL_GAP, SUMMARY_PAD_BOTTOM,
)


def build_summary_row(summary: dict, base_currency: str) -> ft.Container:
    def stat(lbl, val, color):
        return ft.Column([
            ft.Text(lbl.upper(), size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                    font_family="monospace",
                    style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
            ft.Text(t.format_amount(val, currency=base_currency), size=scaled(SUMMARY_AMOUNT_FONT), color=color,
                    weight=ft.FontWeight.W_600, font_family="monospace"),
        ], spacing=scaled(SUMMARY_LABEL_GAP), horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=ft.Row([
            stat(tr("summary.income"),   summary["income"],   t.BLUE),
            ft.VerticalDivider(width=scaled(BORDER_WIDTH), color=t.BORDER),
            stat(tr("summary.expenses"), summary["expenses"], t.RED),
            ft.VerticalDivider(width=scaled(BORDER_WIDTH), color=t.BORDER),
            stat(tr("summary.balance"), summary["balance"],  t.TEXT),
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           bottom=scaled(SUMMARY_PAD_BOTTOM), top=scaled(4)),
        border=t.border_bottom(),
    )
