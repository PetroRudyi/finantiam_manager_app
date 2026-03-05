# -*- coding: utf-8 -*-
"""
main.py  —  Expense Tracker entry point
Compatible with Flet >= 0.80.0

Run:  python main.py
"""

import threading
import flet as ft

import backend
from frontend import theme as t
from frontend.screen_transactions import TransactionsScreen
from frontend.screen_add_receipt import AddReceiptScreen
from frontend.screen_dashboard import DashboardScreen
from frontend.screen_settings import SettingsScreen


def main(page: ft.Page):
    page.title = "Expense Tracker"
    page.bgcolor = t.BG
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=t.ACCENT)
    page.window.width = 390
    page.window.height = 720
    page.window.resizable = False

    # Shared mutable state
    app_state = {
        "settings": backend.load_settings(),
        "receipts": backend.load_receipts(),
        "current_tab": 0,
    }

    content_area = ft.Container(expand=True)

    # fab_button буде оголошений нижче, після визначення open_add_receipt

    # ── Navigation ───────────────────────────────────────────

    def rebuild_nav():
        app_state["receipts"] = backend.load_receipts()
        app_state["settings"] = backend.load_settings()
        tab = app_state["current_tab"]

        # При поверненні на основні екрани показуємо нижнє меню
        tab_bar.visible = True
        tab_bar.update()

        if tab == 0:
            s = TransactionsScreen(app_state=app_state, on_add=open_add_receipt,
                                   on_refresh=rebuild_nav)
            # Wrap in Stack with FAB positioned bottom-right, above tab bar
            content_area.content = ft.Stack(
                controls=[
                    s,
                    ft.Container(
                        content=fab_button,
                        right=16, bottom=12,
                    ),
                ],
                expand=True,
            )
        elif tab == 1:
            content_area.content = DashboardScreen(app_state=app_state)
        else:
            content_area.content = SettingsScreen(app_state=app_state,
                                                   on_refresh=rebuild_nav)

        content_area.update()

    def open_add_receipt(receipt=None):
        # На екрані створення / редагування чеку ховаємо нижнє меню,
        # щоб вийти можна було лише через "Назад" або "Зберегти".
        tab_bar.visible = False
        tab_bar.update()
        s = AddReceiptScreen(app_state=app_state,
                             on_save=lambda: rebuild_nav(),
                             on_cancel=rebuild_nav,
                             receipt=receipt)
        content_area.content = s
        content_area.update()

    # ── Tab bar ──────────────────────────────────────────────

    TAB_LABELS = ["ВИТРАТИ", "ДАШБОРД", "НАЛАШТ."]

    def make_tab(label: str, idx: int) -> ft.Container:
        active = idx == 0
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(height=2, width=24,
                                 bgcolor=t.ACCENT if active else "transparent",
                                 border_radius=1),
                    ft.Text(label, size=9,
                            color=t.ACCENT if active else t.TEXT_DIMMER,
                            font_family="monospace",
                            text_align=ft.TextAlign.CENTER,
                            style=ft.TextStyle(letter_spacing=1.0)),
                ],
                spacing=3,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            padding=ft.Padding(left=0, right=0, top=9, bottom=14),
            on_click=lambda e, i=idx: set_tab(i),
            ink=True,
        )

    tab_row = ft.Row([make_tab(l, i) for i, l in enumerate(TAB_LABELS)], spacing=0)

    def set_tab(idx: int):
        app_state["current_tab"] = idx
        rebuild_nav()
        for i, c in enumerate(tab_row.controls):
            c.content.controls[1].color = t.ACCENT if i == idx else t.TEXT_DIMMER
            c.content.controls[0].bgcolor = t.ACCENT if i == idx else "transparent"
        tab_row.update()

    tab_bar = ft.Container(
        content=tab_row,
        bgcolor=t.SURFACE,
        border=ft.Border(top=ft.BorderSide(1, t.BORDER)),
    )

    # ── Custom FAB (no page-level FAB — no animations) ──────
    fab_button = ft.Container(
        content=ft.Icon(ft.Icons.ADD_ROUNDED, size=28, color=t.WHITE),
        width=52, height=52, border_radius=13,
        bgcolor=t.ACCENT,
        alignment=ft.Alignment(0, 0),
        on_click=lambda e: open_add_receipt(),
        ink=True,
    )

    page.add(ft.Column([content_area, tab_bar],
                       spacing=0, expand=True))
    rebuild_nav()
    page.update()

    # ── Background migration: exchange rates for existing receipts ──
    def _migrate_rates():
        s = app_state["settings"]
        rs = app_state["receipts"]
        needs = any(
            # base_currency not set yet
            r.base_currency is None and r.currency != s.default_currency
            for r in rs
        ) or any(
            # base_currency changed
            r.base_currency is not None and r.base_currency != s.default_currency
            for r in rs
        ) or any(
            # rate missing (previous API call failed)
            r.currency != s.default_currency and r.exchange_rate is None
            for r in rs
        )
        if needs:
            print(f"[migration] Recalculating exchange rates → {s.default_currency}")
            app_state["receipts"] = backend.recalculate_all_receipts(s.default_currency)
            try:
                rebuild_nav()
            except Exception:
                pass
            print("[migration] Done")

    threading.Thread(target=_migrate_rates, daemon=True).start()


if __name__ == "__main__":
    ft.run(main)
