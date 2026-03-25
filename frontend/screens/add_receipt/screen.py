# -*- coding: utf-8 -*-
"""
frontend/screens/add_receipt/screen.py
Screen 04 — Add/Edit receipt with items, AI photo, and save logic.
"""

import datetime
from typing import Callable, List, Optional
import flet as ft

import backend
from backend.models import Receipt, InvoiceItem, AppSettings
from backend.config import DEFAULT_CURRENCY, get_symbol
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.screens.add_receipt.receipt_form import ReceiptForm
from frontend.screens.add_receipt.items_table import (
    build_column_headers, build_add_row, build_item_row, update_total_text,
)
from frontend.screens.add_receipt.item_editor import open_item_editor
from frontend.screens.add_receipt.ai_handler import get_ai_click_handler
from frontend.sizes import (
    FONT_XS, FONT_TITLE, LETTER_SPACING,
    PAD_PAGE_H, PAD_HEADER_TOP, PAD_HEADER_BOTTOM,
    FIELD_RADIUS, GAP_XS,
)
from frontend.screens.add_receipt.sizes import (
    TOTAL_FONT, HEADER_SPACER_W, HEADER_PAD_LEFT,
    SAVE_BTN_PAD_H, FORM_FIELD_PAD_V,
)


class AddReceiptScreen(ft.Column):
    def __init__(self, app_state, on_save: Callable, on_cancel: Callable,
                 receipt: Optional[Receipt] = None):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.editing_receipt = receipt
        self._page_ref: Optional[ft.Page] = None
        self._init_state()

    def did_mount(self):
        self._page_ref = self.page
        self._build()
        self.update()

    def _init_state(self):
        r = self.editing_receipt
        now = datetime.datetime.now()
        self._date = r.created_date if r else now
        self._business = (r.business_name or "") if r else ""
        self._currency = r.currency if r else self.app_state.settings.default_currency
        self._type = r.transaction_type if r else "expense"
        self._items: List[InvoiceItem] = list(r.items) if r else []
        self._ai_running = False
        self._ai_status_text = ""

    def _build(self):
        self.controls.clear()
        settings: AppSettings = self.app_state.settings

        header = ft.Container(
            content=ft.Row([
                ft.TextButton(tr("add_receipt.back"),
                              style=ft.ButtonStyle(color=t.TEXT_DIM),
                              on_click=lambda e: self.on_cancel()),
                ft.Text(tr("add_receipt.new_receipt") if not self.editing_receipt else tr("add_receipt.editing"),
                        size=scaled(FONT_TITLE), color=t.TEXT, weight=ft.FontWeight.W_600),
                ft.Container(width=scaled(HEADER_SPACER_W)),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=scaled(HEADER_PAD_LEFT), right=scaled(PAD_PAGE_H),
                               top=scaled(PAD_HEADER_TOP), bottom=scaled(PAD_HEADER_BOTTOM)),
        )

        self._form = ReceiptForm(
            date=self._date,
            business=self._business,
            currency=self._currency,
            tx_type=self._type,
            has_api_key=bool(settings.gemini_api_key),
            ai_running=self._ai_running,
            ai_status_text=self._ai_status_text,
            on_currency_change=self._on_currency_change,
            on_type_change=self._set_type,
            on_pick_ai_image=get_ai_click_handler(self, self._page_ref),
            page=self._page_ref,
        )
        form_container = self._form.build()

        self._items_col = ft.Column(spacing=0)
        self._rebuild_items()

        col_heads = build_column_headers()
        add_row = build_add_row(lambda e: self._open_item_dialog(None, None))

        self._total_text = ft.Text(
            "", size=scaled(TOTAL_FONT), font_family="monospace", weight=ft.FontWeight.W_600)
        self._update_total()

        save_bar = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(tr("add_receipt.total"), size=scaled(FONT_XS), color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
                    self._total_text,
                ], spacing=scaled(GAP_XS)),
                ft.ElevatedButton(
                    tr("add_receipt.save"), bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=scaled(FIELD_RADIUS)),
                        padding=t.pad_sym(horizontal=scaled(SAVE_BTN_PAD_H), vertical=scaled(FORM_FIELD_PAD_V)),
                    ),
                    on_click=self._save,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(FORM_FIELD_PAD_V)),
            border=t.border_top(),
        )

        self.controls += [
            header,
            ft.Column([form_container, col_heads, self._items_col, add_row],
                      expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
            save_bar,
        ]

    def _rebuild_items(self):
        self._items_col.controls.clear()
        settings: AppSettings = self.app_state.settings
        for i, item in enumerate(self._items):
            self._items_col.controls.append(
                build_item_row(item, i, settings, self._currency,
                               on_edit=lambda idx: self._open_item_dialog(self._items[idx], idx),
                               on_remove=self._remove_item))
        try:
            self._items_col.update()
        except Exception:
            pass

    def _update_total(self):
        update_total_text(self._total_text, self._items, self._type, self._currency)

    # ── Handlers ─────────────────────────────────────────────

    def _on_currency_change(self, code: str):
        self._currency = code
        self._rebuild_items()
        self._update_total()

    def _set_type(self, mode: str):
        self._type = mode
        self._build()
        self.update()

    def _remove_item(self, idx: int):
        self._items.pop(idx)
        self._rebuild_items()
        self._update_total()

    def _open_item_dialog(self, item: Optional[InvoiceItem], idx: Optional[int]):
        open_item_editor(
            page=self._page_ref,
            app_state=self.app_state,
            items=self._items,
            item=item,
            idx=idx,
            on_done=lambda: (self._rebuild_items(), self._update_total()),
        )

    def _save(self, e):
        try:
            d = datetime.datetime.strptime(
                f"{self._form.date_field.value} {self._form.time_field.value}",
                "%d.%m.%Y %H:%M",
            )
        except ValueError:
            d = datetime.datetime.now()

        settings: AppSettings = self.app_state.settings
        base_currency = settings.default_currency
        receipt_currency = self._form.currency_field.value or DEFAULT_CURRENCY

        rate = None
        if receipt_currency != base_currency:
            if (
                self.editing_receipt
                and self.editing_receipt.exchange_rate is not None
                and self.editing_receipt.currency == receipt_currency
                and (self.editing_receipt.base_currency or base_currency) == base_currency
                and self.editing_receipt.created_date.date() == d.date()
            ):
                rate = self.editing_receipt.exchange_rate
            else:
                rate = backend.get_rate_for_receipt(receipt_currency, base_currency, d)

        receipt_kwargs = dict(
            created_date=d,
            business_name=self._form.shop_field.value.strip() or None,
            currency=receipt_currency,
            transaction_type=self._type,
            items=self._items,
            exchange_rate=rate,
            base_currency=base_currency,
        )
        if self.editing_receipt:
            receipt_kwargs["id"] = self.editing_receipt.id
        receipt = Receipt(**receipt_kwargs)

        if rate is not None:
            receipt.base_total = backend.convert_amount(receipt.total, rate)

        if self.editing_receipt:
            self.app_state.receipts = backend.update_receipt(receipt)
        else:
            self.app_state.receipts = backend.add_receipt(receipt)

        self.on_save()
