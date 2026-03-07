# -*- coding: utf-8 -*-
"""app/shell.py — Application shell: tab bar, FAB, navigation, content area."""

import threading
import flet as ft

from app.state import AppState
from app.migration import run_background_migration
from frontend import theme as t
from frontend.screens.transactions import TransactionsScreen
from frontend.screens.dashboard import DashboardScreen
from frontend.screens.add_receipt import AddReceiptScreen
from frontend.screens.settings import SettingsScreen


TAB_LABELS = ["ВИТРАТИ", "ДАШБОРД", "НАЛАШТ."]


class AppShell:
    """Manages page setup, tab navigation, FAB, and content routing."""

    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state
        self._in_add_screen = False
        self._setup_page()
        self._content_area = ft.Container(expand=True)
        self._tab_row = ft.Row(
            [self._make_tab(label, idx) for idx, label in enumerate(TAB_LABELS)],
            spacing=0,
        )
        self._fab_button = ft.Container(
            content=ft.Icon(ft.Icons.ADD_ROUNDED, size=28, color=t.WHITE),
            width=52, height=52, border_radius=13,
            bgcolor=t.ACCENT,
            alignment=ft.Alignment(0, 0),
            on_click=lambda e: self.open_add_receipt(),
            ink=True,
        )
        self._tab_bar = ft.Container(
            content=self._tab_row,
            bgcolor=t.SURFACE,
            border=ft.Border(top=ft.BorderSide(1, t.BORDER)),
        )

    def _setup_page(self):
        self.page.title = "Expense Tracker"
        self.page.bgcolor = t.BG
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(color_scheme_seed=t.ACCENT)
        self.page.window.width = 390
        self.page.window.height = 720
        self.page.window.resizable = False

    def start(self):
        """Add controls to page and kick off initial rendering + migration."""
        safe_top = ft.Container(height=28, bgcolor=t.BG)
        safe_bottom = ft.Container(height=16, bgcolor=t.SURFACE)
        self.page.add(ft.Column(
            [safe_top, self._content_area, self._tab_bar, safe_bottom],
            spacing=0, expand=True,
        ))
        self.page.on_back = self._on_back
        self.page.on_keyboard_event = self._on_keyboard
        self.rebuild_nav()
        self.page.update()

        threading.Thread(
            target=run_background_migration,
            args=(self.state, self.rebuild_nav),
            daemon=True,
        ).start()

    # ── Navigation ───────────────────────────────────────────

    def rebuild_nav(self):
        self.state.reload()
        tab = self.state.current_tab

        self._tab_bar.visible = True
        self._tab_bar.update()

        if tab == 0:
            s = TransactionsScreen(
                app_state=self.state,
                on_add=self.open_add_receipt,
                on_refresh=self.rebuild_nav,
            )
            self._content_area.content = ft.Stack(
                controls=[
                    s,
                    ft.Container(content=self._fab_button, right=16, bottom=12),
                ],
                expand=True,
            )
        elif tab == 1:
            self._content_area.content = DashboardScreen(app_state=self.state)
        else:
            self._content_area.content = SettingsScreen(
                app_state=self.state, on_refresh=self.rebuild_nav,
            )

        self._content_area.update()

    def open_add_receipt(self, receipt=None):
        self._in_add_screen = True
        self._tab_bar.visible = False
        self._tab_bar.update()
        s = AddReceiptScreen(
            app_state=self.state,
            on_save=lambda: self._close_add_screen(),
            on_cancel=self._close_add_screen,
            receipt=receipt,
        )
        self._content_area.content = s
        self._content_area.update()

    def _close_add_screen(self):
        self._in_add_screen = False
        self.rebuild_nav()

    def _on_back(self, e):
        if self._in_add_screen:
            self._close_add_screen()
        # On main screens — do nothing (prevent app from closing)

    def _on_keyboard(self, e: ft.KeyboardEvent):
        if e.key == "Escape":
            self._on_back(e)

    # ── Tab bar ──────────────────────────────────────────────

    def _make_tab(self, label: str, idx: int) -> ft.Container:
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
            on_click=lambda e, i=idx: self._set_tab(i),
            ink=True,
        )

    def _set_tab(self, idx: int):
        self.state.current_tab = idx
        self.rebuild_nav()
        for i, c in enumerate(self._tab_row.controls):
            c.content.controls[1].color = t.ACCENT if i == idx else t.TEXT_DIMMER
            c.content.controls[0].bgcolor = t.ACCENT if i == idx else "transparent"
        self._tab_row.update()
