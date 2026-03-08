# -*- coding: utf-8 -*-
"""Multi-select action bar."""

from typing import Set
import flet as ft
from frontend import theme as t
from frontend.localisation import t as tr


def build_selection_bar(selected_ids: Set[str],
                        on_delete, on_change_date) -> ft.Container:
    count = len(selected_ids)
    return ft.Container(
        content=ft.Row([
            ft.Text(tr("transactions.selected").replace("{count}", str(count)), size=10, color=t.ACCENT,
                    font_family="monospace"),
            ft.Row([
                ft.TextButton(tr("transactions.delete"),
                              style=ft.ButtonStyle(color=t.RED),
                              on_click=on_delete),
                ft.Text("·", size=10, color=t.TEXT_DIMMER),
                ft.TextButton(tr("transactions.change_date"),
                              style=ft.ButtonStyle(color=t.TEXT_DIM),
                              on_click=on_change_date),
            ], spacing=0),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        bgcolor=t.alpha(t.ACCENT, "18"),
        padding=t.pad_sym(horizontal=18, vertical=5),
        border=t.border_bottom(color=t.alpha(t.ACCENT, "28")),
    )
