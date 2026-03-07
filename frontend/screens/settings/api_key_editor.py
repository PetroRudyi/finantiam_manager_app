# -*- coding: utf-8 -*-
"""Gemini API key editor sub-screen."""

import flet as ft
from frontend import theme as t


def build_api_key_editor(settings, on_save, on_cancel) -> ft.Column:
    """Build the API key editor view.

    Parameters:
        settings: AppSettings with current gemini_api_key
        on_save: callback(new_key: str) when user saves
        on_cancel: callback() when user cancels
    """
    api_key_field = ft.TextField(
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
        label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace"),
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

    def _save(e):
        on_save(api_key_field.value.strip())

    return ft.Column([
        ft.Container(
            content=api_key_field,
            padding=t.pad_sym(horizontal=18, vertical=10),
        ),
        ft.Container(
            content=info_text,
            padding=t.pad_only(left=18, right=18, bottom=12),
        ),
        ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    "Скасувати",
                    style=ft.ButtonStyle(
                        color=t.TEXT_DIM,
                        side=ft.BorderSide(1, t.BORDER),
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=t.pad_sym(horizontal=16, vertical=10),
                    ),
                    on_click=lambda e: on_cancel(),
                ),
                ft.ElevatedButton(
                    "Зберегти",
                    bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=t.pad_sym(horizontal=20, vertical=10),
                    ),
                    on_click=_save,
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
            padding=t.pad_sym(horizontal=18, vertical=10),
        ),
    ], spacing=4, expand=True)
