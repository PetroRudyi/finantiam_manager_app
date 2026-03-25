# -*- coding: utf-8 -*-
"""Main settings list view."""

import flet as ft

from backend.models import AppSettings
from backend.config import CURRENCY_CODES, SUPPORTED_LANGUAGES
from frontend import theme as t
from frontend.localisation import t as tr, current_language
from frontend.helpers import show_snack
from frontend.components.settings_row import settings_section, settings_row


def build_main_settings(settings: AppSettings,
                        on_set, on_open_categories, on_reset_categories,
                        on_open_api_key, on_export_csv) -> ft.Column:
    # Language dropdown
    lang_dd = ft.Dropdown(
        value=current_language(),
        bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=8,
        text_style=ft.TextStyle(size=12, color=t.TEXT, font_family="monospace"),
        content_padding=t.pad_sym(horizontal=10, vertical=4),
        width=140,
        options=[ft.dropdown.Option(key=code, text=name)
                 for code, name in SUPPORTED_LANGUAGES.items()],
    )
    lang_dd.on_select = lambda e: on_set("language", e.control.value)

    # Currency dropdown
    currency_dd = ft.Dropdown(
        value=settings.default_currency,
        bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=8,
        text_style=ft.TextStyle(size=12, color=t.TEXT, font_family="monospace"),
        content_padding=t.pad_sym(horizontal=10, vertical=4),
        width=100,
        options=[ft.dropdown.Option(c) for c in CURRENCY_CODES],
    )
    currency_dd.on_select = lambda e: on_set("default_currency", e.control.value)

    # Dark theme switch
    dark_sw = ft.Switch(value=settings.dark_theme, active_color=t.ACCENT)
    dark_sw.on_change = lambda e: on_set("dark_theme", e.control.value)

    # AI auto-fill switch
    ai_sw = ft.Switch(value=settings.ai_auto_fill, active_color=t.ACCENT)
    ai_sw.on_change = lambda e: on_set("ai_auto_fill", e.control.value)

    # API key masked preview
    api_key = settings.gemini_api_key
    if api_key and len(api_key) > 3:
        masked = "●●●●" + api_key[-3:]
    elif api_key:
        masked = "●●●●"
    else:
        masked = ""

    active_count = len([c for c in settings.categories if not c.deleted])

    return ft.Column([
        settings_section(tr("settings.general")),
        settings_row(tr("settings.language"), right=lang_dd),
        settings_row(tr("settings.default_currency"), right=currency_dd),
        settings_row(tr("settings.dark_theme"), right=dark_sw),
        settings_row(tr("settings.date_format"),
                     right=ft.Text(settings.date_format, size=12,
                                   color=t.TEXT_DIM, font_family="monospace"),
                     on_click=lambda e: None),

        settings_section(tr("settings.categories")),
        settings_row(tr("settings.edit_categories"),
                     sub=tr("settings.categories_count").replace("{count}", str(active_count)),
                     right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: on_open_categories()),
        settings_row(tr("settings.reset_defaults"),
                     sub=tr("settings.reset_sub"),
                     right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: on_reset_categories()),

        settings_section(tr("settings.ai_gemini")),
        settings_row(
            tr("settings.api_key"),
            sub=tr("settings.for_receipts"),
            right=ft.Text(
                masked if masked else "—",
                size=12, color=t.TEXT_DIM, font_family="monospace",
            ),
            on_click=lambda e: on_open_api_key(),
        ),
        settings_row(tr("settings.auto_fill"), right=ai_sw),

        settings_section(tr("settings.data")),
        settings_row(tr("settings.backup"),
                     sub=tr("settings.backup_sub"),
                     right=ft.Text("›", size=12, color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: None),
        ft.Container(
            content=ft.ElevatedButton(
                tr("settings.export_csv"),
                bgcolor=t.SURFACE2, color=t.BLUE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=9),
                    side=ft.BorderSide(1, t.BORDER),
                    padding=t.pad_sym(horizontal=12, vertical=10),
                ),
                on_click=lambda e: on_export_csv(),
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
