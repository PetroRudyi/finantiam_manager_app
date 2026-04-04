# -*- coding: utf-8 -*-
"""Main settings list view."""

import flet as ft

from backend.models import AppSettings
from backend.config import CURRENCY_CODES, SUPPORTED_LANGUAGES
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr, current_language
from frontend.helpers import show_snack
from frontend.components.settings_row import settings_section, settings_row
from frontend.sizes import (
    FONT_SM, FONT_BODY, PAD_PAGE_H, BTN_RADIUS, BTN_PAD_V, BORDER_WIDTH,
)
from frontend.screens.settings.sizes import (
    LANG_DD_W, CURRENCY_DD_W, DD_RADIUS, DD_PAD_H, DD_PAD_V,
    MARKUP_DD_W, EXPORT_BTN_PAD_H, VERSION_PAD_V,
)


def build_main_settings(settings: AppSettings,
                        on_set, on_open_categories, on_reset_categories,
                        on_open_api_key, on_export_csv) -> ft.Column:
    # Language dropdown
    lang_dd = ft.Dropdown(
        value=current_language(),
        bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=scaled(DD_RADIUS),
        text_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT, font_family="monospace"),
        content_padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(DD_PAD_V)),
        width=scaled(LANG_DD_W),
        options=[ft.dropdown.Option(key=code, text=name)
                 for code, name in SUPPORTED_LANGUAGES.items()],
    )
    lang_dd.on_select = lambda e: on_set("language", e.control.value)

    # Currency dropdown
    currency_dd = ft.Dropdown(
        value=settings.default_currency,
        bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=scaled(DD_RADIUS),
        text_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT, font_family="monospace"),
        content_padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(DD_PAD_V)),
        width=scaled(CURRENCY_DD_W),
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

    # Exchange markup percentage dropdown
    markup_options = [1, 2, 3, 5, 7, 10, 15, 20]
    current_pct = settings.exchange_markup_percent
    current_pct_str = (str(int(current_pct))
                       if current_pct == int(current_pct) and int(current_pct) in markup_options
                       else str(markup_options[3]))  # default to 5%
    markup_dd = ft.Dropdown(
        value=current_pct_str,
        bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=scaled(DD_RADIUS),
        text_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT, font_family="monospace"),
        content_padding=t.pad_sym(horizontal=scaled(DD_PAD_H), vertical=scaled(DD_PAD_V)),
        width=scaled(MARKUP_DD_W),
        options=[ft.dropdown.Option(key=str(v), text=f"+{v}%") for v in markup_options],
        disabled=not settings.exchange_markup_enabled,
    )
    markup_dd.on_select = lambda e: on_set("exchange_markup_percent", float(e.control.value))

    # Exchange markup switch
    def _on_markup_toggle(e):
        enabled = e.control.value
        markup_dd.disabled = not enabled
        if enabled and settings.exchange_markup_percent == 0.0:
            settings.exchange_markup_percent = 5.0
            markup_dd.value = "5"
        try:
            markup_dd.update()
        except Exception:
            pass
        on_set("exchange_markup_enabled", enabled)

    markup_sw = ft.Switch(value=settings.exchange_markup_enabled, active_color=t.ACCENT)
    markup_sw.on_change = _on_markup_toggle

    active_count = len([c for c in settings.categories if not c.deleted])

    return ft.Column([
        settings_section(tr("settings.general"), first=True),
        settings_row(tr("settings.language"), right=lang_dd),
        settings_row(tr("settings.default_currency"), right=currency_dd),
        settings_row(tr("settings.dark_theme"), right=dark_sw),
        settings_row(tr("settings.date_format"),
                     right=ft.Text(settings.date_format, size=scaled(FONT_BODY),
                                   color=t.TEXT_DIM, font_family="monospace"),
                     on_click=lambda e: None),

        settings_section(tr("settings.exchange")),
        settings_row(tr("settings.exchange_markup"),
                     sub=tr("settings.exchange_markup_sub"),
                     right=markup_sw),
        settings_row(tr("settings.exchange_markup_percent"),
                     sub=(tr("settings.exchange_markup_example")
                          .replace("{multiplier}",
                                   f"{1 + current_pct / 100:.2f}")
                          if settings.exchange_markup_enabled else ""),
                     right=markup_dd),

        settings_section(tr("settings.categories")),
        settings_row(tr("settings.edit_categories"),
                     sub=tr("settings.categories_count").replace("{count}", str(active_count)),
                     right=ft.Text("›", size=scaled(FONT_BODY), color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: on_open_categories()),
        settings_row(tr("settings.reset_defaults"),
                     sub=tr("settings.reset_sub"),
                     right=ft.Text("›", size=scaled(FONT_BODY), color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: on_reset_categories()),

        settings_section(tr("settings.ai_gemini")),
        settings_row(
            tr("settings.api_key"),
            sub=tr("settings.for_receipts"),
            right=ft.Text(
                masked if masked else "—",
                size=scaled(FONT_BODY), color=t.TEXT_DIM, font_family="monospace",
            ),
            on_click=lambda e: on_open_api_key(),
        ),
        settings_row(tr("settings.auto_fill"), right=ai_sw),

        settings_section(tr("settings.data")),
        settings_row(tr("settings.backup"),
                     sub=tr("settings.backup_sub"),
                     right=ft.Text("›", size=scaled(FONT_BODY), color=t.TEXT_DIMMER,
                                   font_family="monospace"),
                     on_click=lambda e: None),
        ft.Container(
            content=ft.ElevatedButton(
                tr("settings.export_csv"),
                bgcolor=t.SURFACE2, color=t.BLUE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=scaled(BTN_RADIUS)),
                    side=ft.BorderSide(scaled(BORDER_WIDTH), t.BORDER),
                    padding=t.pad_sym(horizontal=scaled(EXPORT_BTN_PAD_H), vertical=scaled(BTN_PAD_V)),
                ),
                on_click=lambda e: on_export_csv(),
                expand=True,
            ),
            padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(BTN_PAD_V)),
        ),
        ft.Container(
            content=ft.Text("v1.0.0", size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                            font_family="monospace",
                            text_align=ft.TextAlign.CENTER),
            padding=t.pad_sym(vertical=scaled(VERSION_PAD_V)),
            alignment=ft.Alignment(0, 0),
        ),
    ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
