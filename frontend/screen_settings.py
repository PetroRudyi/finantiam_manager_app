# -*- coding: utf-8 -*-
"""
frontend/screen_settings.py  —  Compatible with Flet >= 0.80.0

Flet 0.80+ dialog API:
  Open:   page.dialog = dlg; dlg.open = True; page.update()
  Close:  dlg.open = False; page.update()
  Snack:  page.snack_bar = sb; sb.open = True; page.update()

Event handlers assigned as attributes AFTER construction (not as kwargs).
"""

import threading
import flet as ft
from typing import Callable

import backend
from backend.models import AppSettings, Category
from backend.config import CURRENCY_CODES, DEFAULT_CATEGORY_DEFS
from frontend import theme as t


def _show_snack(page: ft.Page, msg: str):
    sb = ft.SnackBar(content=ft.Text(msg, color=t.TEXT), bgcolor=t.SURFACE2)
    page.snack_bar = sb
    sb.open = True
    page.update()


class SettingsScreen(ft.Column):
    def __init__(self, app_state: dict, on_refresh: Callable):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_refresh = on_refresh
        self._show_categories = False
        self._show_api_key_editor = False  # окрема вкладка для API ключа
        self._editing_cat_idx = None
        self._build()

    def refresh(self):
        self._build()
        self.update()

    def _build(self):
        self.controls.clear()
        settings: AppSettings = self.app_state["settings"]

        if self._show_categories:
            self.controls += [
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text("←", size=14, color=t.TEXT_DIM),
                            on_click=lambda e: self._go_back(),
                            ink=True, padding=t.pad_sym(horizontal=6, vertical=4),
                        ),
                        ft.Text("Категорії", size=15, color=t.TEXT,
                                weight=ft.FontWeight.W_600),
                        ft.Container(width=40),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=t.pad_only(left=12, right=18, top=4, bottom=10),
                ),
                self._build_cat_editor(settings),
            ]
        elif self._show_api_key_editor:
            # Окрема вкладка для редагування API ключа
            self.controls += [
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Text("←", size=14, color=t.TEXT_DIM),
                                on_click=lambda e: self._go_back(),
                                ink=True,
                                padding=t.pad_sym(horizontal=6, vertical=4),
                            ),
                            ft.Text(
                                "API ключ Gemini",
                                size=15,
                                color=t.TEXT,
                                weight=ft.FontWeight.W_600,
                            ),
                            ft.Container(width=40),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=t.pad_only(left=12, right=18, top=4, bottom=10),
                ),
                self._build_api_key_editor(settings),
            ]
        else:
            self.controls += [
                ft.Container(
                    content=ft.Text("Налаштування", size=15, color=t.TEXT,
                                    weight=ft.FontWeight.W_600),
                    padding=t.pad_only(left=18, right=18, top=4, bottom=10),
                ),
                self._build_main(settings),
            ]

    # ── Main settings ─────────────────────────────────────────

    def _build_main(self, settings: AppSettings) -> ft.Column:
        # Dropdowns — on_change assigned AFTER construction
        currency_dd = ft.Dropdown(
            value=settings.default_currency,
            bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=8,
            text_style=ft.TextStyle(size=12, color=t.TEXT, font_family="monospace"),
            content_padding=t.pad_sym(horizontal=10, vertical=4),
            width=100,
            options=[ft.dropdown.Option(c) for c in CURRENCY_CODES],
        )
        currency_dd.on_select = lambda e: self._set("default_currency", e.control.value)

        date_dd = ft.Dropdown(
            value=settings.date_format,
            bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=8,
            text_style=ft.TextStyle(size=12, color=t.TEXT, font_family="monospace"),
            content_padding=t.pad_sym(horizontal=10, vertical=4),
            width=120,
            options=[ft.dropdown.Option(f) for f in
                     ["DD.MM.YY", "MM/DD/YY", "YY-MM-DD"]],
        )
        date_dd.on_select = lambda e: self._set("date_format", e.control.value)

        # Switches — on_change assigned AFTER construction
        dark_sw = ft.Switch(value=settings.dark_theme, active_color=t.ACCENT)
        dark_sw.on_change = lambda e: self._set("dark_theme", e.control.value)

        ai_sw = ft.Switch(value=settings.ai_auto_fill, active_color=t.ACCENT)
        ai_sw.on_change = lambda e: self._set("ai_auto_fill", e.control.value)

        # API key masked preview
        api_key = settings.gemini_api_key
        if api_key and len(api_key) > 3:
            masked = "●●●●" + api_key[-3:]
        elif api_key:
            masked = "●●●●"
        else:
            masked = ""

        return ft.Column([
            self._sec("ЗАГАЛЬНЕ"),
            self._row("Валюта за замовч.", right=currency_dd),
            self._row("Темна тема",        right=dark_sw),
            self._row("Формат дати",
                      right=ft.Text(settings.date_format, size=12,
                                    color=t.TEXT_DIM, font_family="monospace"),
                      on_click=lambda e: None),

            self._sec("КАТЕГОРІЇ"),
            self._row("Редагувати категорії",
                      sub=f"{len([c for c in settings.categories if not c.deleted])} категорій у списку",
                      right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                    font_family="monospace"),
                      on_click=lambda e: self._open_categories()),
            self._row("Відновити початкові",
                      sub="Скинути до дефолтних",
                      right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                    font_family="monospace"),
                      on_click=lambda e: self._reset_categories()),

            self._sec("AI · GEMINI"),
            self._row(
                "API ключ Gemini",
                sub="Для розпізнавання чеків",
                right=ft.Text(
                    masked if masked else "—",
                    size=12,
                    color=t.TEXT_DIM,
                    font_family="monospace",
                ),
                on_click=lambda e: self._open_api_key_row(e),
            ),
            self._row("Авто-заповнення", right=ai_sw),

            self._sec("ДАНІ"),
            self._row("Резервна копія",
                      sub="Останнє: дані в data/",
                      right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                    font_family="monospace"),
                      on_click=lambda e: _show_snack(
                          self.page,
                          "Дані вже зберігаються локально в папці data/")),
            ft.Container(
                content=ft.ElevatedButton(
                    "Вигрузити всі дані у CSV",
                    bgcolor=t.SURFACE2, color=t.BLUE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=9),
                        side=ft.BorderSide(1, t.BORDER),
                        padding=t.pad_sym(horizontal=12, vertical=10),
                    ),
                    on_click=lambda e: self._export_csv(),
                    expand=True,
                ),
                padding=t.pad_sym(horizontal=18, vertical=10),
            ),
            ft.Container(
                content=ft.Text("v1.0.0", size=9, color=t.TEXT_DIMMER,
                                font_family="monospace",
                                text_align=ft.TextAlign.CENTER),
                padding=t.pad_sym(vertical=12),
                alignment=ft.Alignment(0, 0),
            ),
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    # ── Category editor ───────────────────────────────────────

    def _build_cat_editor(self, settings: AppSettings) -> ft.Column:
        self._new_cat_field = ft.TextField(
            hint_text="Нова категорія...",
            bgcolor=t.SURFACE2, border_color=t.BORDER,
            focused_border_color=t.ACCENT, border_radius=8, expand=True,
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            hint_style=ft.TextStyle(size=12, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=10, vertical=7),
        )
        self._cat_list = ft.Column(spacing=0)
        self._cat_error = ft.Text("", size=10, color=t.RED)
        self._refresh_cat_list(settings)

        editing_label = ""
        active_cats = [c for c in settings.categories if not c.deleted]
        if (
            self._editing_cat_idx is not None
            and 0 <= self._editing_cat_idx < len(active_cats)
        ):
            editing_label = (
                f" · Редагується: {active_cats[self._editing_cat_idx].name}"
            )

        return ft.Column([
            ft.Container(
                content=ft.Text(
                    "Перетягніть для зміни порядку",
                    size=9, color=t.TEXT_DIMMER, font_family="monospace"),
                padding=t.pad_only(left=18, right=18, bottom=8),
            ),
            self._cat_list,
            ft.Container(
                content=ft.Row([
                    self._new_cat_field,
                    ft.ElevatedButton(
                        "+ Додати", bgcolor=t.ACCENT, color=t.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=t.pad_sym(horizontal=14, vertical=7),
                        ),
                        on_click=self._add_category,
                    ),
                ], spacing=8),
                padding=t.pad_sym(horizontal=18, vertical=10),
            ),
            ft.Container(
                content=self._cat_error,
                padding=t.pad_only(left=18, right=18, bottom=4),
            ),
            ft.Container(
                content=ft.Text(
                    f"{len(active_cats)} категорій{editing_label}",
                    size=9, color=t.TEXT_DIMMER, font_family="monospace"),
                padding=t.pad_only(left=18, right=18, bottom=8),
                alignment=ft.Alignment(0, 0),
            ),
        ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    def _refresh_cat_list(self, settings: AppSettings):
        self._cat_list.controls.clear()
        active_cats = [c for c in settings.categories if not c.deleted]
        for i, cat in enumerate(active_cats):
            if i == self._editing_cat_idx:
                self._cat_list.controls.append(self._cat_row_editing(cat, i, settings))
            else:
                self._cat_list.controls.append(self._cat_row(cat, i, settings))
        try:
            self._cat_list.update()
        except Exception:
            pass

    def _cat_row(self, cat: Category, idx: int, settings: AppSettings) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Text("⠿", size=14, color=t.TEXT_DIMMER, font_family="monospace"),
                ft.Text(cat.name, size=13, color=t.TEXT,
                        weight=ft.FontWeight.W_500, expand=True),
                ft.Container(
                    content=ft.Text("✎", size=10, color=t.ACCENT,
                                    font_family="monospace"),
                    bgcolor=t.alpha(t.ACCENT, "18"), border_radius=5,
                    border=t.border_all(1, t.alpha(t.ACCENT, "44")),
                    padding=t.pad_sym(horizontal=8, vertical=3),
                    on_click=lambda e, i=idx: self._start_edit_category(i),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Text("×", size=10, color=t.RED,
                                    font_family="monospace"),
                    bgcolor=t.alpha(t.RED, "18"), border_radius=5,
                    border=t.border_all(1, t.alpha(t.RED, "33")),
                    padding=t.pad_sym(horizontal=8, vertical=3),
                    on_click=lambda e, c=cat: self._delete_category(c, settings),
                    ink=True,
                ),
            ], spacing=8),
            padding=t.pad_only(left=18, right=18, top=9, bottom=9),
            border=t.border_bottom(),
        )

    def _cat_row_editing(self, cat: Category, idx: int, settings: AppSettings) -> ft.Container:
        self._edit_cat_field = ft.TextField(
            value=cat.name, autofocus=True, expand=True,
            bgcolor=t.SURFACE2, border_color=t.ACCENT, border_radius=7,
            text_style=ft.TextStyle(size=13, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=10, vertical=5),
        )
        return ft.Container(
            content=ft.Row([
                ft.Text("⠿", size=14, color=t.TEXT_DIMMER, font_family="monospace"),
                self._edit_cat_field,
                ft.ElevatedButton(
                    "OK", bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=7),
                        padding=t.pad_sym(horizontal=10, vertical=3),
                    ),
                    on_click=lambda e, i=idx: self._confirm_edit_category(i, settings),
                ),
            ], spacing=8),
            padding=t.pad_only(left=18, right=18, top=6, bottom=6),
            border=t.border_bottom(),
            bgcolor=t.alpha(t.ACCENT, "0a"),
        )

    def _build_api_key_editor(self, settings: AppSettings) -> ft.Column:
        """Окрема вкладка для введення API ключа Gemini."""
        self._api_key_field = ft.TextField(
            value=settings.gemini_api_key,
            label="API ключ Gemini",
            hint_text="AIza...",
            password=True,
            can_reveal_password=True,
            bgcolor=t.SURFACE2,
            border_color=t.BORDER,
            focused_border_color=t.ACCENT,
            border_radius=9,
            expand=True,
            label_style=ft.TextStyle(
                size=9,
                color=t.TEXT_DIMMER,
                font_family="monospace",
            ),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=12, vertical=9),
        )

        info_text = ft.Text(
            "Ключ використовується лише для запитів до сервісу Gemini "
            "для розпізнавання чеків.\n"
            "Розробник програми не має доступу до вашого API ключа "
            "і не може списувати кошти з вашого акаунта.",
            size=9,
            color=t.TEXT_DIMMER,
        )

        def save_and_back(e):
            self._set("gemini_api_key", self._api_key_field.value.strip())
            self._show_api_key_editor = False
            self._build()
            self.update()

        def cancel_and_back(e):
            self._show_api_key_editor = False
            self._build()
            self.update()

        return ft.Column(
            [
                ft.Container(
                    content=self._api_key_field,
                    padding=t.pad_sym(horizontal=18, vertical=10),
                ),
                ft.Container(
                    content=info_text,
                    padding=t.pad_only(left=18, right=18, bottom=12),
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.OutlinedButton(
                                "Скасувати",
                                style=ft.ButtonStyle(
                                    color=t.TEXT_DIM,
                                    side=ft.BorderSide(1, t.BORDER),
                                    shape=ft.RoundedRectangleBorder(radius=9),
                                    padding=t.pad_sym(horizontal=16, vertical=10),
                                ),
                                on_click=cancel_and_back,
                            ),
                            ft.ElevatedButton(
                                "Зберегти",
                                bgcolor=t.ACCENT,
                                color=t.WHITE,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=9),
                                    padding=t.pad_sym(horizontal=20, vertical=10),
                                ),
                                on_click=save_and_back,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10,
                    ),
                    padding=t.pad_sym(horizontal=18, vertical=10),
                ),
            ],
            spacing=4,
            expand=True,
        )

    # ── Helpers ──────────────────────────────────────────────

    def _open_api_key_row(self, e):
        """Відкрити окрему вкладку введення API ключа."""
        self._show_categories = False
        self._show_api_key_editor = True
        self._build()
        self.update()

    def _sec(self, label: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=9, color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=1.2)),
            padding=t.pad_only(left=18, right=18, top=12, bottom=5),
        )

    def _row(self, label: str, sub: str = "",
             right=None, on_click=None) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(label, size=13, color=t.TEXT,
                            weight=ft.FontWeight.W_500),
                    *([ft.Text(sub, size=9, color=t.TEXT_DIMMER)] if sub else []),
                ], spacing=1, expand=True),
                right or ft.Container(),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_sym(horizontal=18, vertical=10),
            border=t.border_bottom(),
            on_click=on_click,
            ink=bool(on_click),
        )

    def _set(self, key: str, value):
        settings: AppSettings = self.app_state["settings"]
        old_value = getattr(settings, key, None)
        setattr(settings, key, value)
        backend.save_settings(settings)

        if key == "default_currency" and value != old_value:
            self._recalculate_base_currency(value)

    def _recalculate_base_currency(self, new_currency: str):
        progress = ft.ProgressBar(width=250, color=t.ACCENT, bgcolor=t.SURFACE2)
        status = ft.Text("Перерахунок валют... 0%", size=11, color=t.TEXT_DIM)
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Зміна базової валюти", size=13, color=t.TEXT),
            bgcolor=t.SURFACE,
            content=ft.Column([status, progress], spacing=10, tight=True, width=280),
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

        def on_progress(current, total):
            progress.value = current / total
            status.value = f"Перерахунок валют... {int(current / total * 100)}%"
            try:
                progress.update()
                status.update()
            except Exception:
                pass

        def run():
            try:
                self.app_state["receipts"] = backend.recalculate_all_receipts(
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

    def _open_categories(self):
        self._show_categories = True
        self._show_api_key_editor = False
        self._editing_cat_idx = None
        self._build()
        self.update()

    def _go_back(self):
        self._show_categories = False
        self._show_api_key_editor = False
        self._editing_cat_idx = None
        self._build()
        self.update()

    def _reset_categories(self):
        settings: AppSettings = self.app_state["settings"]
        settings.categories = [Category(id=c.id, name=c.name) for c in DEFAULT_CATEGORY_DEFS]
        backend.save_settings(settings)
        self._build()
        self.update()

    def _add_category(self, e):
        settings: AppSettings = self.app_state["settings"]
        name = self._new_cat_field.value.strip()
        if not name:
            return
        # Перевірка на дубль за назвою серед активних категорій
        for c in settings.categories:
            if not c.deleted and c.name == name:
                self._cat_error.value = "Така категорія вже існує"
                try:
                    self._cat_error.update()
                except Exception:
                    pass
                return
        # Створюємо нову категорію з ID = max(id) + 1
        cid = settings.ensure_category(name)
        backend.save_settings(settings)
        self._new_cat_field.value = ""
        self._cat_error.value = ""
        self._refresh_cat_list(settings)
        try:
            self._new_cat_field.update()
            self._cat_error.update()
        except Exception:
            pass

    def _delete_category(self, cat: Category, settings: AppSettings):
        if cat in settings.categories:
            # М'яке видалення: залишаємо запис, але позначаємо як видалений
            cat.deleted = True
            cat.name = "..."
            backend.save_settings(settings)
            if self._editing_cat_idx is not None:
                self._editing_cat_idx = None
            self._refresh_cat_list(settings)

    def _start_edit_category(self, idx: int):
        self._editing_cat_idx = idx
        settings: AppSettings = self.app_state["settings"]
        self._build()
        self.update()

    def _confirm_edit_category(self, idx: int, settings: AppSettings):
        new_name = self._edit_cat_field.value.strip()
        if new_name and new_name != settings.categories[idx].name:
            # Міняємо лише name, ID залишається сталим,
            # щоб чеки по ID автоматично підхоплювали нову назву.
            settings.categories[idx].name = new_name
            backend.save_settings(settings)
        self._editing_cat_idx = None
        self._build()
        self.update()

    def _edit_api_key(self, settings: AppSettings):
        field = ft.TextField(
            value=settings.gemini_api_key, autofocus=True,
            label="API ключ", hint_text="AIza...",
            password=True, can_reveal_password=True,
            bgcolor=t.SURFACE2, border_color=t.BORDER,
            focused_border_color=t.ACCENT, border_radius=9, expand=True,
            label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER,
                                     font_family="monospace"),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=12, vertical=9),
        )

        dlg_ref: list = [None]

        def confirm(e):
            new_key = field.value.strip()
            settings.gemini_api_key = new_key
            backend.save_settings(settings)
            dlg_ref[0].open = False
            self.page.update()
            self._build()
            self.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("API ключ Gemini", size=13, color=t.TEXT,
                          weight=ft.FontWeight.W_600),
            bgcolor=t.SURFACE,
            content=ft.Column([
                field,
                ft.Text(
                    "Для розпізнавання фото чеків.",
                    size=9,
                    color=t.TEXT_DIMMER,
                ),
                ft.Text(
                    "Ми не зберігаємо ваш API ключ і не несемо "
                    "відповідальності за витрати на вашому акаунті.",
                    size=9,
                    color=t.TEXT_DIMMER,
                ),
            ], spacing=6, tight=True, width=300),
            actions=[
                ft.OutlinedButton(
                    "Скасувати",
                    style=ft.ButtonStyle(
                        color=t.TEXT_DIM,
                        side=ft.BorderSide(1, t.BORDER),
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                    on_click=lambda e: (
                        setattr(dlg_ref[0], 'open', False),
                        self.page.update(),
                    ),
                ),
                ft.ElevatedButton(
                    "Зберегти", bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=9)),
                    on_click=confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        dlg_ref[0] = dlg
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def _export_csv(self):
        receipts = self.app_state.get("receipts", [])
        settings: AppSettings = self.app_state["settings"]
        path = backend.export_to_csv(receipts, settings)
        _show_snack(self.page, f"Збережено: {path}")
