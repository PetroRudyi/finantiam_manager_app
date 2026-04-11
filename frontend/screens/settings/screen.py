# -*- coding: utf-8 -*-
"""
frontend/screens/settings/screen.py
Screen 03 — Settings with sub-view routing.
"""

import threading
import flet as ft
from typing import Callable

import backend
from backend.models import AppSettings, Category
from backend.config import DEFAULT_CATEGORY_DEFS
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.helpers import show_snack
from frontend.screens.settings.main_settings import build_main_settings
from frontend.screens.settings.category_editor import CategoryEditor
from frontend.screens.settings.api_key_editor import build_api_key_editor
from frontend.sizes import (
    FONT_LG, FONT_MD, FONT_NAV, FONT_HEADER,
    PAD_PAGE_H, PAD_HEADER_TOP, PAD_HEADER_BOTTOM,
    GAP_XL,
)
from frontend.screens.settings.sizes import (
    BACK_ARROW_PAD_H, BACK_ARROW_PAD_V,
    SUB_HEADER_PAD_LEFT, SPACER_W, PROGRESS_W, DIALOG_W,
)


class SettingsScreen(ft.Column):
    def __init__(self, app_state, on_refresh: Callable):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_refresh = on_refresh
        self._show_categories = False
        self._show_api_key_editor = False
        self._cat_editor = CategoryEditor(app_state, on_rebuild=self._rebuild, get_page=lambda: self.page)
        self._build()

    def refresh(self):
        self._build()
        self.update()

    def _rebuild(self):
        self._build()
        self.update()

    def _build(self):
        self.controls.clear()
        settings: AppSettings = self.app_state.settings

        if self._show_categories:
            self.controls += [
                self._sub_header(tr("settings.categories")),
                self._cat_editor.build(),
            ]
        elif self._show_api_key_editor:
            self.controls += [
                self._sub_header(tr("settings.api_key")),
                build_api_key_editor(settings,
                                     on_save=self._save_api_key,
                                     on_cancel=self._go_back),
            ]
        else:
            self.controls += [
                ft.Container(
                    content=ft.Text(tr("settings.title"), size=scaled(FONT_HEADER), color=t.TEXT,
                                    weight=ft.FontWeight.W_600),
                    padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                                       top=scaled(PAD_HEADER_TOP), bottom=scaled(PAD_HEADER_BOTTOM)),
                ),
                build_main_settings(
                    settings,
                    on_set=self._set,
                    on_open_categories=self._open_categories,
                    on_reset_categories=self._reset_categories,
                    on_open_api_key=self._open_api_key,
                    on_export_csv=self._export_csv,
                ),
            ]

    def _sub_header(self, title: str) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("←", size=scaled(FONT_NAV), color=t.TEXT_DIM),
                            ft.Text(tr("settings.back"), size=scaled(FONT_NAV), color=t.TEXT_DIM),
                        ],
                        spacing=scaled(4),
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    on_click=lambda e: self._go_back(),
                    ink=True, padding=t.pad_sym(horizontal=scaled(BACK_ARROW_PAD_H),
                                                vertical=scaled(BACK_ARROW_PAD_V)),
                ),
                ft.Text(title, size=scaled(FONT_HEADER), color=t.TEXT, weight=ft.FontWeight.W_600),
                ft.Container(width=scaled(SPACER_W)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=scaled(SUB_HEADER_PAD_LEFT), right=scaled(PAD_PAGE_H),
                               top=scaled(PAD_HEADER_TOP), bottom=scaled(PAD_HEADER_BOTTOM)),
        )

    # ── Navigation ─────────────────────────────────────────────

    def _open_categories(self):
        self._show_categories = True
        self._show_api_key_editor = False
        self._cat_editor.reset_editing()
        self._build()
        self.update()

    def _open_api_key(self):
        self._show_categories = False
        self._show_api_key_editor = True
        self._build()
        self.update()

    def _go_back(self):
        self._show_categories = False
        self._show_api_key_editor = False
        self._cat_editor.reset_editing()
        self._build()
        self.update()

    # ── Handlers ──────────────────────────────────────────────

    def _set(self, key: str, value):
        settings: AppSettings = self.app_state.settings
        old_value = getattr(settings, key, None)
        setattr(settings, key, value)
        backend.save_settings(settings)

        if key == "language" and value != old_value:
            from frontend.localisation import init as init_localisation
            init_localisation(value)
            self.on_refresh()
            return

        if key == "default_currency" and value != old_value:
            self._recalculate_base_currency(value)

        if key in ("exchange_markup_enabled", "exchange_markup_percent") and value != old_value:
            self._recalculate_base_currency(settings.default_currency)

    def _save_api_key(self, new_key: str, new_model: str = ""):
        self._set("gemini_api_key", new_key)
        if new_model:
            self._set("gemini_model", new_model)
        self._show_api_key_editor = False
        self._build()
        self.update()

    def _reset_categories(self):
        settings: AppSettings = self.app_state.settings
        settings.categories = [Category(id=c.id, name=c.name) for c in DEFAULT_CATEGORY_DEFS]
        backend.save_settings(settings)
        self._build()
        self.update()

    def _export_csv(self):
        receipts = self.app_state.receipts
        settings: AppSettings = self.app_state.settings
        path = backend.export_to_csv(receipts, settings)
        show_snack(self.page, tr("settings.saved").replace("{path}", str(path)))

    def _recalculate_base_currency(self, new_currency: str):
        progress = ft.ProgressBar(width=scaled(PROGRESS_W), color=t.ACCENT, bgcolor=t.SURFACE2)
        status = ft.Text(tr("settings.recalc_progress").replace("{percent}", "0"),
                         size=scaled(FONT_MD), color=t.TEXT_DIM)
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(tr("settings.currency_change_title"), size=scaled(FONT_LG), color=t.TEXT),
            bgcolor=t.SURFACE,
            content=ft.Column([status, progress], spacing=scaled(GAP_XL), tight=True, width=scaled(DIALOG_W)),
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

        def on_progress(current, total):
            progress.value = current / total
            status.value = tr("settings.recalc_progress").replace("{percent}", str(int(current / total * 100)))
            try:
                progress.update()
                status.update()
            except Exception:
                pass

        def run():
            try:
                self.app_state.receipts = backend.recalculate_all_receipts(
                    new_currency, progress_callback=on_progress
                )
            except Exception:
                pass
            dlg.open = False
            try:
                self.page.update()
            except Exception:
                pass
            self.on_refresh()

        try:
            self.page.run_thread(run)
        except Exception:
            threading.Thread(target=run, daemon=True).start()
