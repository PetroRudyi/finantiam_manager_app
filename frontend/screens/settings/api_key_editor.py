# -*- coding: utf-8 -*-
"""Gemini API key editor sub-screen."""

import flet as ft
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import (
    FONT_SM, FONT_BODY, PAD_PAGE_H, FIELD_RADIUS, FIELD_PAD_H, FIELD_PAD_V,
    BTN_RADIUS, BTN_PAD_V, BORDER_WIDTH, GAP_SM, GAP_XL,
)
from frontend.screens.settings.sizes import (
    API_CANCEL_PAD_H, API_SAVE_PAD_H, API_INFO_PAD_BOTTOM,
)


def build_api_key_editor(settings, on_save, on_cancel) -> ft.Column:
    """Build the API key editor view.

    Parameters:
        settings: AppSettings with current gemini_api_key
        on_save: callback(new_key: str) when user saves
        on_cancel: callback() when user cancels
    """
    api_key_field = ft.TextField(
        value=settings.gemini_api_key,
        label=tr("api_key_editor.label"),
        hint_text=tr("api_key_editor.hint"),
        password=True,
        can_reveal_password=True,
        bgcolor=t.SURFACE2,
        border_color=t.BORDER,
        focused_border_color=t.ACCENT,
        border_radius=scaled(FIELD_RADIUS),
        expand=True,
        label_style=ft.TextStyle(size=scaled(FONT_SM), color=t.TEXT_DIMMER, font_family="monospace"),
        text_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT),
        content_padding=t.pad_sym(horizontal=scaled(FIELD_PAD_H), vertical=scaled(FIELD_PAD_V)),
    )

    info_text = ft.Text(
        tr("api_key_editor.info"),
        size=scaled(FONT_SM),
        color=t.TEXT_DIMMER,
    )

    def _save(e):
        on_save(api_key_field.value.strip())

    return ft.Column([
        ft.Container(
            content=api_key_field,
            padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(BTN_PAD_V)),
        ),
        ft.Container(
            content=info_text,
            padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                               bottom=scaled(API_INFO_PAD_BOTTOM)),
        ),
        ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    tr("api_key_editor.cancel"),
                    style=ft.ButtonStyle(
                        color=t.TEXT_DIM,
                        side=ft.BorderSide(scaled(BORDER_WIDTH), t.BORDER),
                        shape=ft.RoundedRectangleBorder(radius=scaled(BTN_RADIUS)),
                        padding=t.pad_sym(horizontal=scaled(API_CANCEL_PAD_H), vertical=scaled(BTN_PAD_V)),
                    ),
                    on_click=lambda e: on_cancel(),
                ),
                ft.ElevatedButton(
                    tr("api_key_editor.save"),
                    bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=scaled(BTN_RADIUS)),
                        padding=t.pad_sym(horizontal=scaled(API_SAVE_PAD_H), vertical=scaled(BTN_PAD_V)),
                    ),
                    on_click=_save,
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=scaled(GAP_XL)),
            padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(BTN_PAD_V)),
        ),
    ], spacing=scaled(GAP_SM), expand=True)
