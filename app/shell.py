# -*- coding: utf-8 -*-
"""app/shell.py — Application shell: tab bar, FAB, navigation, content area."""

import threading
import flet as ft

from app.state import AppState
from app.migration import run_background_migration
from backend.config import WINDOW_RESIZABLE
from backend.update_service import check_for_update, get_apk_url
from frontend import theme as t
from frontend.theme import scaled
from frontend.sizes import FONT_TAB
from frontend.localisation import t as tr
from frontend.screens.transactions import TransactionsScreen
from frontend.screens.dashboard import DashboardScreen
from frontend.screens.add_receipt import AddReceiptScreen
from frontend.screens.settings import SettingsScreen


def _get_tab_labels():
    return [tr("shell.tab_expenses"), tr("shell.tab_dashboard"), tr("shell.tab_settings")]


class AppShell:
    """Manages page setup, tab navigation, FAB, and content routing."""

    def __init__(self, page: ft.Page, state: AppState):
        self.page = page
        self.state = state
        self._in_add_screen = False
        self._setup_page(width=450, height=1000)

    # ── Page setup ───────────────────────────────────────────

    def _setup_page(self, width=390, height=720):
        self.page.title = "Expense Tracker"
        self.page.bgcolor = t.BG
        self.page.padding = 0
        self.page.spacing = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.theme = ft.Theme(color_scheme_seed=t.ACCENT)
        self.page.window.width = width
        self.page.window.height = height
        self.page.window.resizable = WINDOW_RESIZABLE

    def _build_ui(self):
        """Create all UI controls. Called AFTER init_scale so scaled() works."""
        self._content_area = ft.Container(expand=True)
        self._tab_row = ft.Row(
            [self._make_tab(label, idx) for idx, label in enumerate(_get_tab_labels())],
            spacing=0,
        )
        self._fab_button = ft.Container(
            content=ft.Icon(ft.Icons.ADD_ROUNDED, size=scaled(28), color=t.WHITE),
            width=scaled(52), height=scaled(52), border_radius=scaled(13),
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

    def start(self):
        """Add controls to page and kick off initial rendering + migration."""
        # Flush page so that window dimensions are applied
        self.page.update()

        # Calculate scale based on window dimensions (not viewport — it may be 0 this early)
        t.init_scale(self.page.window.width, self.page.window.height)

        # Build all UI with correct scale
        self._build_ui()

        safe_top = ft.Container(height=scaled(28), bgcolor=t.BG)
        safe_bottom = ft.Container(height=scaled(16), bgcolor=t.SURFACE)
        self.page.add(ft.Column(
            [safe_top, self._content_area, self._tab_bar, safe_bottom],
            spacing=0, expand=True,
        ))
        self.page.on_back = self._on_back
        self.page.on_keyboard_event = self._on_keyboard
        self.page.on_resized = self._on_resized
        self.rebuild_nav()
        self.page.update()

        threading.Thread(
            target=run_background_migration,
            args=(self.state, self.rebuild_nav),
            daemon=True,
        ).start()

        threading.Thread(target=self._check_update, daemon=True).start()

    # ── Update check ────────────────────────────────────────

    def _check_update(self):
        new_version = check_for_update()
        if not new_version:
            return
        apk_url = get_apk_url()
        if not apk_url:
            return

        dlg = ft.AlertDialog(
            title=ft.Text(tr("update.title")),
            content=ft.Text(tr("update.new_version").replace("{new_version}", new_version)),
            actions=[
                ft.TextButton(
                    tr("update.update"),
                    on_click=lambda _: self.page.launch_url(apk_url),
                ),
                ft.TextButton(
                    tr("update.later"),
                    on_click=lambda _: self.page.close(dlg),
                ),
            ],
        )
        self.page.open(dlg)
        self.page.update()

    # ── Navigation ───────────────────────────────────────────

    def rebuild_nav(self):
        self.state.reload()
        tab = self.state.current_tab

        # Rebuild tab labels (language may have changed)
        tab_labels = _get_tab_labels()
        for i, c in enumerate(self._tab_row.controls):
            c.content.controls[1].value = tab_labels[i]

        self._tab_bar.visible = True
        self._tab_bar.update()

        if tab == 0:
            screen = TransactionsScreen(
                app_state=self.state,
                on_add=self.open_add_receipt,
                on_refresh=self.rebuild_nav,
            )
            self._content_area.content = ft.Stack(
                controls=[
                    screen,
                    ft.Container(content=self._fab_button, right=scaled(16), bottom=scaled(12)),
                ],
                expand=True,
            )
        elif tab == 1:
            self._content_area.content = DashboardScreen(
                app_state=self.state,
                on_edit_receipt=self.open_add_receipt,
            )
        else:
            self._content_area.content = SettingsScreen(
                app_state=self.state, on_refresh=self.rebuild_nav,
            )

        self._content_area.update()

    def open_add_receipt(self, receipt=None):
        self._in_add_screen = True
        self._tab_bar.visible = False
        self._tab_bar.update()
        screen = AddReceiptScreen(
            app_state=self.state,
            on_save=lambda: self._close_add_screen(),
            on_cancel=self._close_add_screen,
            receipt=receipt,
        )
        self._content_area.content = screen
        self._content_area.update()

    def _close_add_screen(self):
        self._in_add_screen = False
        self.rebuild_nav()

    def _on_resized(self, e):
        """Recalculate scale factor and rebuild the entire UI on window resize."""
        t.init_scale(self.page.window.width, self.page.window.height)
        # Rebuild all UI controls with new scale
        self._build_ui()
        safe_top = ft.Container(height=scaled(28), bgcolor=t.BG)
        safe_bottom = ft.Container(height=scaled(16), bgcolor=t.SURFACE)
        self.page.controls.clear()
        self.page.add(ft.Column(
            [safe_top, self._content_area, self._tab_bar, safe_bottom],
            spacing=0, expand=True,
        ))
        self.rebuild_nav()
        self.page.update()

    def _on_back(self, e):
        if self._in_add_screen:
            self._close_add_screen()
            return
        # Check if dashboard is showing category detail
        if self.state.current_tab == 1:
            content = self._content_area.content
            if isinstance(content, DashboardScreen) and content.in_category_detail:
                content.close_category_detail()
                return
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
                    ft.Container(height=scaled(2), width=scaled(24),
                                 bgcolor=t.ACCENT if active else "transparent",
                                 border_radius=scaled(1)),
                    ft.Text(label, size=scaled(FONT_TAB),
                            color=t.ACCENT if active else t.TEXT_DIMMER,
                            font_family="monospace",
                            text_align=ft.TextAlign.CENTER,
                            style=ft.TextStyle(letter_spacing=scaled(1.0))),
                ],
                spacing=scaled(3),
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            padding=ft.Padding(left=0, right=0, top=scaled(9), bottom=scaled(14)),
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
