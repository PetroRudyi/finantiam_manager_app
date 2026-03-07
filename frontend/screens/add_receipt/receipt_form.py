# -*- coding: utf-8 -*-
"""Receipt header form: date, time, shop, currency, type toggle."""

import datetime
from typing import Callable, List
import flet as ft

from backend.config import CURRENCY_CODES
from frontend import theme as t
from frontend.components.type_toggle import TypeToggle


class ReceiptForm:
    """Builds the top form area of the add/edit receipt screen.

    After calling build(), access the field references via:
        .date_field, .time_field, .shop_field, .currency_field
    """

    def __init__(self, date: datetime.datetime, business: str, currency: str,
                 tx_type: str, has_api_key: bool, ai_running: bool,
                 ai_status_text: str,
                 on_currency_change: Callable[[str], None],
                 on_type_change: Callable[[str], None],
                 on_pick_ai_image,
                 page: ft.Page):
        self._date = date
        self._business = business
        self._currency = currency
        self._tx_type = tx_type
        self._has_api_key = has_api_key
        self._ai_running = ai_running
        self._ai_status_text = ai_status_text
        self._on_currency_change = on_currency_change
        self._on_type_change = on_type_change
        self._on_pick_ai_image = on_pick_ai_image
        self._page = page

    def build(self) -> ft.Container:
        _lbl = ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace")
        _txt = ft.TextStyle(size=12, color=t.TEXT)

        self.date_field = ft.TextField(
            value=self._date.strftime("%d.%m.%Y"), label="Дата",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True, read_only=True,
            label_style=_lbl, text_style=_txt,
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )
        self.date_field.on_click = self._open_date_picker

        self.time_field = ft.TextField(
            value=self._date.strftime("%H:%M"), label="Час",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=_lbl, text_style=_txt,
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )

        self.shop_field = ft.TextField(
            value=self._business, hint_text="необов'язково",
            label="Магазин / джерело",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=_lbl, text_style=_txt,
            hint_style=ft.TextStyle(size=12, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )

        self.currency_field = ft.Dropdown(
            value=self._currency, label="Валюта",
            bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=9,
            width=100,
            label_style=_lbl, text_style=_txt,
            content_padding=t.pad_sym(horizontal=11, vertical=4),
            options=[ft.dropdown.Option(c) for c in CURRENCY_CODES],
        )
        self.currency_field.on_select = lambda e: self._on_currency_change(e.control.value)

        type_row = TypeToggle(self._tx_type, on_change=self._on_type_change,
                              style="outlined")

        status_text = self._ai_status_text
        if not self._has_api_key:
            status_text = "API ключ не налаштований"
        elif self._ai_running and not status_text:
            status_text = "AI: обробка…"

        self.ai_status = ft.Text(status_text, size=10, color=t.TEXT_DIMMER,
                                 font_family="monospace")

        self.ai_btn = ft.Container(
            content=ft.Row([
                ft.Text("Завантажити фото чеку (AI)", size=11,
                        color=t.ACCENT if self._has_api_key else t.TEXT_DIMMER,
                        font_family="monospace"),
                self.ai_status,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=t.alpha(t.ACCENT, "0f") if self._has_api_key else t.SURFACE2,
            border=t.border_all(1, t.alpha(t.ACCENT, "66") if self._has_api_key else t.BORDER),
            border_radius=9, padding=10,
            on_click=(None if self._ai_running else
                      (self._on_pick_ai_image if self._has_api_key else None)),
            ink=(self._has_api_key and not self._ai_running),
        )

        date_block = ft.Row([self.date_field], spacing=7, expand=True)

        return ft.Container(
            content=ft.Column([
                ft.Row([date_block, self.time_field], spacing=7),
                ft.Row([self.shop_field, self.currency_field], spacing=7),
                type_row,
                self.ai_btn,
            ], spacing=7),
            padding=t.pad_sym(horizontal=18, vertical=6),
        )

    # ── Date picker ───────────────────────────────────────────

    def _open_date_picker(self, e=None):
        dp = ft.DatePicker(
            value=self._date.date(),
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=self._on_date_picked,
        )
        self._page.show_dialog(dp)

    def _on_date_picked(self, ev):
        raw = ev.data if ev.data is not None else getattr(ev.control, "value", None)
        if raw is None:
            return

        if isinstance(raw, datetime.datetime):
            if raw.tzinfo is not None:
                raw = raw.astimezone(tz=None)
            picked_date = raw.date()
        elif isinstance(raw, datetime.date):
            picked_date = raw
        else:
            s = str(raw).replace(" ", "T").split("T", 1)[0]
            try:
                picked_date = datetime.date.fromisoformat(s)
            except ValueError:
                return

        self._date = datetime.datetime(
            year=picked_date.year, month=picked_date.month, day=picked_date.day,
            hour=self._date.hour, minute=self._date.minute,
            second=self._date.second, microsecond=self._date.microsecond,
        )
        try:
            self.date_field.value = self._date.strftime("%d.%m.%Y")
            self.date_field.update()
        except Exception:
            try:
                self._page.update()
            except Exception:
                pass
