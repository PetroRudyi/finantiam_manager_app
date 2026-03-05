# -*- coding: utf-8 -*-
"""
frontend/screen_add_receipt.py  —  Compatible with Flet >= 0.80.0

Flet 0.80+ dialog API:
  Open:   page.dialog = dlg; dlg.open = True; page.update()
  Close:  dlg.open = False; page.update()
  Snack:  page.snack_bar = sb; sb.open = True; page.update()

Event handlers assigned as attributes AFTER construction (not as kwargs).
"""

import datetime
import threading
import difflib
import flet as ft
from typing import Callable, List, Optional

import backend
from backend.models import Receipt, InvoiceItem, AppSettings
from backend.config import CURRENCY_CODES, DEFAULT_CURRENCY, DEFAULT_CATEGORY, get_symbol
from frontend import theme as t


def _open_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Open an AlertDialog in Flet 0.80+."""
    page.dialog = dlg
    dlg.open = True
    page.update()


def _close_dialog(page: ft.Page, dlg: ft.AlertDialog):
    """Close an AlertDialog in Flet 0.80+."""
    dlg.open = False
    page.update()


def _show_snack(page: ft.Page, msg: str, color: str = t.TEXT_DIM):
    """Show a SnackBar in Flet 0.80+."""
    sb = ft.SnackBar(
        content=ft.Text(msg, color=t.TEXT),
        bgcolor=t.SURFACE2,
    )
    page.snack_bar = sb
    sb.open = True
    page.update()


class AddReceiptScreen(ft.Column):
    def __init__(self, app_state: dict, on_save: Callable, on_cancel: Callable,
                 receipt: Optional[Receipt] = None):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_save = on_save
        self.on_cancel = on_cancel
        self.editing_receipt = receipt
        self._init_state()
        self._build()

    # ── State ────────────────────────────────────────────────

    def _init_state(self):
        r = self.editing_receipt
        now = datetime.datetime.now()
        self._date = r.created_date if r else now
        self._business = (r.business_name or "") if r else ""
        self._currency = r.currency if r else self.app_state["settings"].default_currency
        self._type = r.transaction_type if r else "expense"
        self._items: List[InvoiceItem] = list(r.items) if r else []
        self._ai_running = False
        self._ai_status_text = ""

    def _set_ai_status(self, text: str):
        self._ai_status_text = text
        try:
            self._ai_status.value = text
            self._ai_status.update()
        except Exception:
            try:
                self.page.update()
            except Exception:
                pass

    # ── Build ─────────────────────────────────────────────────

    def _on_date_picked(self, ev):
        """Callback for DatePicker on_change."""
        # ev.data — datetime.datetime з UTC; ev.control.value може бути None

        raw = ev.data if ev.data is not None else getattr(ev.control, "value", None)
        if raw is None:
            return

        # Витягуємо лише дату (рік/місяць/день)
        # DatePicker повертає UTC — конвертуємо в локальний час, щоб не втратити день
        if isinstance(raw, datetime.datetime):
            if raw.tzinfo is not None:
                raw = raw.astimezone(tz=None)  # UTC → локальний час
            picked_date = raw.date()
        elif isinstance(raw, datetime.date):
            picked_date = raw
        else:
            # fallback для рядка
            s = str(raw).replace(" ", "T").split("T", 1)[0]
            try:
                picked_date = datetime.date.fromisoformat(s)
            except ValueError:
                return

        self._date = datetime.datetime(
            year=picked_date.year,
            month=picked_date.month,
            day=picked_date.day,
            hour=self._date.hour,
            minute=self._date.minute,
            second=self._date.second,
            microsecond=self._date.microsecond,
        )
        try:
            self._date_field.value = self._date.strftime("%d.%m.%Y")
            self._date_field.update()
        except Exception:
            try:
                self.page.update()
            except Exception:
                pass

    def _open_date_picker(self, e=None):
        dp = ft.DatePicker(
            value=self._date.date(),
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=self._on_date_picked,
        )
        self.page.show_dialog(dp)

    def _build(self):
        self.controls.clear()

        settings: AppSettings = self.app_state["settings"]

        header = ft.Container(
            content=ft.Row([
                ft.TextButton("← Назад",
                              style=ft.ButtonStyle(color=t.TEXT_DIM),
                              on_click=lambda e: self.on_cancel()),
                ft.Text("Новий чек" if not self.editing_receipt else "Редагування",
                        size=15, color=t.TEXT, weight=ft.FontWeight.W_600),
                ft.Container(width=80),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=8, right=18, top=4, bottom=10),
        )

        self._date_field = ft.TextField(
            value=self._date.strftime("%d.%m.%Y"), label="Дата",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True, read_only=True,
            label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace"),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )
        self._date_field.on_click = self._open_date_picker
        date_block = ft.Row([self._date_field], spacing=7, expand=True)
        self._time_field = ft.TextField(
            value=self._date.strftime("%H:%M"), label="Час",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace"),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )
        self._shop_field = ft.TextField(
            value=self._business, hint_text="необов'язково", label="Магазин / джерело",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace"),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            hint_style=ft.TextStyle(size=12, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=11, vertical=8),
        )
        self._currency_field = ft.Dropdown(
            value=self._currency, label="Валюта",
            bgcolor=t.SURFACE2, border_color=t.BORDER, border_radius=9,
            width=100,
            label_style=ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace"),
            text_style=ft.TextStyle(size=12, color=t.TEXT),
            content_padding=t.pad_sym(horizontal=11, vertical=4),
            options=[ft.dropdown.Option(c) for c in CURRENCY_CODES],
        )
        self._currency_field.on_select = lambda e: self._on_currency_change(e.control.value)

        type_row = self._make_type_row()

        has_api_key = bool(settings.gemini_api_key)
        status_text = self._ai_status_text
        if not has_api_key:
            status_text = "API ключ не налаштований"
        elif self._ai_running and not status_text:
            status_text = "AI: обробка…"
        self._ai_status = ft.Text(
            status_text,
            size=10,
            color=t.TEXT_DIMMER,
            font_family="monospace",
        )
        ai_btn = ft.Container(
            content=ft.Row([
                ft.Text(
                    "Завантажити фото чеку (AI)",
                    size=11,
                    color=t.ACCENT if has_api_key else t.TEXT_DIMMER,
                    font_family="monospace",
                ),
                self._ai_status,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            bgcolor=t.alpha(t.ACCENT, "0f") if has_api_key else t.SURFACE2,
            border=t.border_all(
                1,
                t.alpha(t.ACCENT, "66") if has_api_key else t.BORDER,
            ),
            border_radius=9,
            padding=10,
            on_click=(None if self._ai_running else (self._pick_ai_image if has_api_key else None)),
            ink=(has_api_key and not self._ai_running),
        )
        self._ai_btn = ai_btn

        self._items_col = ft.Column(spacing=0)
        self._rebuild_items()

        col_heads = ft.Container(
            content=ft.Row([
                ft.Text("Назва", size=8, color=t.TEXT_DIMMER,
                        font_family="monospace", expand=True),
                ft.Text("К-ть", size=8, color=t.TEXT_DIMMER,
                        font_family="monospace", width=30,
                        text_align=ft.TextAlign.CENTER),
                ft.Text("Ціна", size=8, color=t.TEXT_DIMMER,
                        font_family="monospace", width=58,
                        text_align=ft.TextAlign.RIGHT),
                ft.Text("Кат.", size=8, color=t.TEXT_DIMMER,
                        font_family="monospace", width=44,
                        text_align=ft.TextAlign.RIGHT),
                ft.Container(width=40),
            ], spacing=4),
            padding=t.pad_only(left=18, right=18, bottom=4),
        )

        add_row = ft.Container(
            content=ft.Text("+ Додати позицію", size=11, color=t.ACCENT,
                            font_family="monospace"),
            padding=t.pad_only(left=18, top=8, bottom=4),
            on_click=lambda e: self._open_item_dialog(None, None),
            ink=True,
        )

        self._total_text = ft.Text(
            "", size=17, font_family="monospace", weight=ft.FontWeight.W_600)
        self._update_total()

        save_bar = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text("РАЗОМ", size=8, color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=1.2)),
                    self._total_text,
                ], spacing=2),
                ft.ElevatedButton(
                    "Зберегти", bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=t.pad_sym(horizontal=22, vertical=9),
                    ),
                    on_click=self._save,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_sym(horizontal=18, vertical=9),
            border=t.border_top(),
        )

        form = ft.Container(
            content=ft.Column([
                ft.Row([date_block, self._time_field], spacing=7),
                ft.Row([self._shop_field, self._currency_field], spacing=7),
                type_row,
                ai_btn,
            ], spacing=7),
            padding=t.pad_sym(horizontal=18, vertical=6),
        )

        self.controls += [
            header,
            ft.Column([form, col_heads, self._items_col, add_row],
                      expand=True, scroll=ft.ScrollMode.AUTO, spacing=0),
            save_bar,
        ]

    def _make_type_row(self) -> ft.Row:
        def btn(label, mode):
            active = self._type == mode
            color = t.RED if mode == "expense" else t.BLUE
            return ft.Container(
                content=ft.Text(label, size=11, font_family="monospace",
                                color=color if active else t.TEXT_DIMMER,
                                text_align=ft.TextAlign.CENTER),
                expand=True,
                bgcolor=t.alpha(color, "18") if active else t.SURFACE2,
                border=t.border_all(1, t.alpha(color, "88") if active else t.BORDER),
                border_radius=9,
                padding=t.pad_sym(vertical=7),
                on_click=lambda e, m=mode: self._set_type(m),
                ink=True,
            )
        return ft.Row([btn("Витрата", "expense"), btn("Дохід", "income")], spacing=7)

    # ── Items ─────────────────────────────────────────────────

    def _rebuild_items(self):
        self._items_col.controls.clear()
        for i, item in enumerate(self._items):
            self._items_col.controls.append(self._item_row(item, i))
        try:
            self._items_col.update()
        except Exception:
            pass

    def _item_row(self, item: InvoiceItem, idx: int) -> ft.Container:
        settings: AppSettings = self.app_state["settings"]
        cat_label = settings.get_category_name(item.category)[:6]
        return ft.Container(
            content=ft.Row([
                ft.Text(item.name, size=12, color=t.TEXT, expand=True,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        weight=ft.FontWeight.W_500),
                ft.Text(f"{item.quantity:g}", size=10, color=t.TEXT_DIM,
                        font_family="monospace", width=30,
                        text_align=ft.TextAlign.CENTER),
                ft.Text(f"{get_symbol(self._currency)}{item.price:.2f}", size=11, color=t.TEXT,
                        font_family="monospace", width=58,
                        text_align=ft.TextAlign.RIGHT),
                ft.Container(
                    content=ft.Text(cat_label, size=8, color=t.TEXT_DIM,
                                    font_family="monospace",
                                    text_align=ft.TextAlign.CENTER),
                    bgcolor=t.SURFACE2, border_radius=4,
                    padding=t.pad_sym(horizontal=5, vertical=2),
                    width=44,
                ),
                ft.Row([
                    ft.Container(
                        content=ft.Text("✎", size=9, color=t.ACCENT,
                                        font_family="monospace"),
                        width=18, height=18, border_radius=4,
                        bgcolor=t.alpha(t.ACCENT, "18"),
                        border=t.border_all(1, t.alpha(t.ACCENT, "44")),
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e, i=idx: self._open_item_dialog(self._items[i], i),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("×", size=9, color=t.RED,
                                        font_family="monospace"),
                        width=18, height=18, border_radius=4,
                        bgcolor=t.alpha(t.RED, "18"),
                        border=t.border_all(1, t.alpha(t.RED, "33")),
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e, i=idx: self._remove_item(i),
                        ink=True,
                    ),
                ], spacing=2, width=40),
            ], spacing=4),
            padding=t.pad_only(left=18, right=18, top=7, bottom=7),
            border=t.border_bottom(),
        )

    def _update_total(self):
        total = sum(i.price for i in self._items)
        sign  = "−" if self._type == "expense" else "+"
        color = t.RED if self._type == "expense" else t.BLUE
        symbol = get_symbol(self._currency)
        self._total_text.value = f"{sign}{symbol}{total:,.2f}"
        self._total_text.color = color
        try:
            self._total_text.update()
        except Exception:
            pass

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
        settings: AppSettings = self.app_state["settings"]
        is_new = item is None

        # ── Fields ────────────────────────────────────────────
        _lbl = ft.TextStyle(size=9, color=t.TEXT_DIMMER, font_family="monospace",
                            letter_spacing=1.2)
        _txt = ft.TextStyle(size=13, color=t.TEXT)

        name_f = ft.TextField(
            value=item.name if item else "",
            label="НАЗВА", hint_text="М'ясо куряче",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, autofocus=True,
            label_style=_lbl, text_style=_txt,
            hint_style=ft.TextStyle(size=13, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=12, vertical=12),
        )

        # ── PRICE FIELD (UPDATED LOGIC ONLY) ───────────────────
        # Old logic
        # qty_f = ft.TextField(
        #     value=str(item.quantity) if item else "1",
        #     label="КІЛЬКІСТЬ", keyboard_type=ft.KeyboardType.NUMBER,
        #     bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        #     border_radius=9, expand=True,
        #     label_style=_lbl, text_style=_txt,
        #     content_padding=t.pad_sym(horizontal=12, vertical=12),
        # )

        default_quantity = "1"

        qty_f = ft.TextField(
            value=str(item.quantity) if item else default_quantity,
            hint_text="",
            label="КІЛЬКІСТЬ", keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^(\d+(\.\d{0,2})?)?$",
                replacement_string=""
            ),
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=_lbl, text_style=_txt,
            content_padding=t.pad_sym(horizontal=12, vertical=12),
        )

        def _price_on_focus(e: ft.ControlEvent):
            tf: ft.TextField = e.control
            if (tf.value or "").strip() == default_quantity:
                tf.value = ""
                tf.update()

        def _price_on_blur(e: ft.ControlEvent):
            tf: ft.TextField = e.control
            if (tf.value or "").strip() == "":
                tf.value = default_quantity
                tf.update()

        # assign handlers after construction
        qty_f.on_focus = _price_on_focus
        qty_f.on_blur = _price_on_blur

        # ──────────────────────────────────────────────────────
        price_f = ft.TextField(
            value=str(item.price) if item else "",
            hint_text = "",
            label="ЦІНА", keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(
                allow=True,
                regex_string=r"^(\d+(\.\d{0,2})?)?$",
                replacement_string=""
            ),
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            label_style=_lbl, text_style=_txt,
            content_padding=t.pad_sym(horizontal=12, vertical=12),
        )

        error_text = ft.Text("", size=10, color=t.RED)

        # ── Category selector ─────────────────────────────────
        # усередині item.category тепер зберігається ID категорії
        active_cats = [c for c in settings.categories if not c.deleted]
        default_cat_id = active_cats[0].id if active_cats else ""
        current_cat = [item.category if item else default_cat_id]
        adding_new_cat = [False]
        new_cat_field = ft.TextField(
            hint_text="Назва категорії",
            bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
            border_radius=9, expand=True,
            text_style=ft.TextStyle(size=13, color=t.TEXT),
            hint_style=ft.TextStyle(size=12, color=t.TEXT_DIMMER),
            content_padding=t.pad_sym(horizontal=12, vertical=8),
        )
        cat_col = ft.Column(spacing=0)

        def _build_cats():
            cat_col.controls.clear()
            for cat in settings.categories:
                if cat.deleted:
                    continue
                sel = cat.id == current_cat[0]
                cat_col.controls.append(ft.Container(
                    content=ft.Row([
                        ft.Text(cat.name, size=13,
                                color=t.ACCENT if sel else t.TEXT),
                        ft.Text("✓", size=13, color=t.ACCENT,
                                font_family="monospace") if sel else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=t.alpha(t.ACCENT, "18") if sel else "transparent",
                    padding=t.pad_sym(horizontal=14, vertical=10),
                    border_radius=8 if sel else 0,
                    on_click=lambda e, c=cat: _sel_cat(c.id),
                    ink=True,
                ))
            # "+ Нова категорія" — toggle inline input
            if adding_new_cat[0]:
                cat_col.controls.append(ft.Container(
                    content=ft.Row([
                        new_cat_field,
                        ft.Container(
                            content=ft.Text("OK", size=11, color=t.WHITE,
                                            font_family="monospace",
                                            text_align=ft.TextAlign.CENTER),
                            width=36, height=36, border_radius=9,
                            bgcolor=t.ACCENT,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda e: _confirm_new_cat(),
                            ink=True,
                        ),
                        ft.Container(
                            content=ft.Text("✕", size=11, color=t.TEXT_DIM,
                                            font_family="monospace",
                                            text_align=ft.TextAlign.CENTER),
                            width=36, height=36, border_radius=9,
                            bgcolor=t.SURFACE2,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda e: _cancel_new_cat(),
                            ink=True,
                        ),
                    ], spacing=6),
                    padding=t.pad_sym(horizontal=10, vertical=6),
                ))
            else:
                cat_col.controls.append(ft.Container(
                    content=ft.Text("+ Нова категорія", size=12, color=t.ACCENT),
                    padding=t.pad_sym(horizontal=14, vertical=10),
                    on_click=lambda e: _start_new_cat(),
                    ink=True,
                ))
            try:
                cat_col.update()
            except Exception:
                pass

        def _sel_cat(c):
            current_cat[0] = c
            adding_new_cat[0] = False
            _build_cats()

        def _start_new_cat():
            adding_new_cat[0] = True
            new_cat_field.value = ""
            _build_cats()

        def _cancel_new_cat():
            adding_new_cat[0] = False
            _build_cats()

        def _confirm_new_cat():
            name = new_cat_field.value.strip()
            if not name:
                return
            # якщо така назва вже існує — не створюємо нову, показуємо помилку
            existing_id = settings.get_category_id_by_name(name)
            if existing_id is not None:
                current_cat[0] = existing_id
                error_text.value = "Така категорія вже існує"
                try:
                    error_text.update()
                except Exception:
                    pass
                adding_new_cat[0] = False
                _build_cats()
                return
            # створюємо нову категорію з ID = max(id) + 1
            cid = settings.ensure_category(name)
            backend.save_settings(settings)
            self.app_state["settings"] = settings
            current_cat[0] = cid
            error_text.value = ""
            try:
                error_text.update()
            except Exception:
                pass
            adding_new_cat[0] = False
            _build_cats()

        _build_cats()

        # ── Bottom sheet ref ──────────────────────────────────
        bs_ref: list = [None]

        def _close_bs():
            bs_ref[0].open = False
            self.page.update()

        def _confirm(e):
            name = name_f.value.strip()
            if not name:
                error_text.value = "Введіть назву"
                error_text.update()
                return
            try:
                qty = float(qty_f.value or "1")
                price = float(price_f.value or "0")
            except ValueError:
                error_text.value = "Невірне число"
                error_text.update()
                return

            item_kwargs = dict(
                name=name,
                quantity=qty,
                price=price,
                # тут category = ID категорії
                category=current_cat[0],
            )
            if item:
                item_kwargs["id"] = item.id
            new_item = InvoiceItem(**item_kwargs)
            if is_new:
                self._items.append(new_item)
            else:
                self._items[idx] = new_item

            self._rebuild_items()
            self._update_total()
            _close_bs()

        # ── Sheet content ─────────────────────────────────────
        # Dynamic height: 90% of actual window height
        sheet_height = int((self.page.window.height or 720) * 0.7)

        # Scrollable body: fields + category list
        scrollable_body = ft.Column([
            name_f,
            ft.Row([qty_f, price_f], spacing=7),
            # Category header
            ft.Container(
                content=ft.Text("КАТЕГОРІЯ", size=9, color=t.TEXT_DIMMER,
                                font_family="monospace",
                                style=ft.TextStyle(letter_spacing=1.2)),
                padding=t.pad_only(top=4, bottom=2),
            ),
            # Category list — expands to fill available space
            ft.Container(
                content=ft.Column([cat_col], scroll=ft.ScrollMode.AUTO,
                                   spacing=0),
                expand=True,
                border=t.border_all(1, t.BORDER),
                border_radius=9,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            ),
            error_text,
        ], spacing=10, expand=True)

        # Fixed bottom buttons
        buttons_row = ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    "Скасувати",
                    style=ft.ButtonStyle(
                        color=t.TEXT_DIM,
                        side=ft.BorderSide(1, t.BORDER),
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=t.pad_sym(horizontal=18, vertical=10),
                    ),
                    on_click=lambda e: _close_bs(),
                ),
                ft.ElevatedButton(
                    "Додати позицію" if is_new else "Зберегти",
                    bgcolor=t.ACCENT, color=t.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=t.pad_sym(horizontal=18, vertical=10),
                    ),
                    on_click=_confirm,
                ),
            ], alignment=ft.MainAxisAlignment.END, spacing=10),
            padding=t.pad_only(top=8, bottom=8),
            border=t.border_top(),
        )

        sheet_content = ft.Container(
            content=ft.Column([
                # Drag handle
                ft.Container(
                    content=ft.Container(
                        width=36, height=4, border_radius=2,
                        bgcolor=t.TEXT_DIMMER,
                    ),
                    alignment=ft.Alignment(0, 0),
                    padding=t.pad_only(top=10, bottom=4),
                ),
                # Title
                ft.Text("Нова позиція" if is_new else "Редагування",
                        size=15, color=t.TEXT, weight=ft.FontWeight.W_600),
                # Scrollable form body
                scrollable_body,
                # Fixed buttons at bottom
                buttons_row,
            ], spacing=6),
            padding=t.pad_sym(horizontal=18, vertical=0),
            bgcolor=t.SURFACE,
            height=sheet_height,
            border_radius=ft.BorderRadius(top_left=16, top_right=16,
                                           bottom_left=0, bottom_right=0),
        )

        bs = ft.BottomSheet(
            content=sheet_content,
            bgcolor=t.SURFACE,
            open=False,
            scrollable=True,
            size_constraints=ft.BoxConstraints(max_height=sheet_height),
            on_dismiss=lambda e: None,
        )
        bs_ref[0] = bs
        self.page.overlay.append(bs)
        self.page.update()
        bs.open = True
        self.page.update()

    # ── AI photo ──────────────────────────────────────────────

    async def _pick_ai_image(self, e):
        settings = self.app_state["settings"]
        if not settings.gemini_api_key:
            _show_snack(
                self.page,
                "Gemini API ключ не налаштований. Перевірте Налаштування.",
            )
            return
        if self._ai_running:
            return

        # Flet 0.80+: FilePicker — це сервіс, використовуємо його напряму
        files = await ft.FilePicker().pick_files(
            dialog_title="Оберіть фото чеку",
            allowed_extensions=["jpg", "jpeg", "png", "gif"],
            allow_multiple=False,
        )
        if not files:
            return

        path = files[0].path
        if not path:
            _show_snack(self.page, "Не вдалося отримати шлях до файлу.")
            return

        self._ai_running = True
        try:
            self._ai_btn.on_click = None
            self._ai_btn.ink = False
            self._ai_btn.update()
        except Exception:
            pass
        self._set_ai_status("AI: підготовка фото…")

        def run():
            try:
                self._set_ai_status("AI: запит до Gemini…")
                data = backend.extract_receipt_from_image(
                    image_path=path,
                    api_key=settings.gemini_api_key,
                    default_currency=settings.default_currency,
                    categories=settings.categories,
                )
                self._set_ai_status("AI: обробка відповіді…")
                merged = backend.merge_duplicate_items(data.invoice_items)
                self._business = data.business_name or ""
                self._currency = data.currency
                if data.created_date:
                    self._date = data.created_date

                # Мапимо назву категорії з AI у внутрішній ID (створюємо нову при потребі)
                def _map_category(name: str) -> str:
                    raw = (name or "").strip()
                    if not raw:
                        return settings.ensure_category(DEFAULT_CATEGORY)

                    # 1) Exact match (case-sensitive, as stored)
                    cid = settings.get_category_id_by_name(raw)
                    if cid is None:
                        # 2) Case-insensitive match
                        for c in settings.categories:
                            if not c.deleted and c.name.strip().lower() == raw.lower():
                                cid = c.id
                                break

                    if cid is None:
                        # 3) Fuzzy match against existing categories (avoid creating junk categories)
                        active_names = [c.name for c in settings.categories if not c.deleted and c.name.strip()]
                        match = difflib.get_close_matches(raw, active_names, n=1, cutoff=0.82)
                        if match:
                            cid = settings.get_category_id_by_name(match[0])

                    if cid is None:
                        # 4) Fallback: create new category (keeps your current behavior)
                        cid = settings.ensure_category(raw)
                        backend.save_settings(settings)
                        self.app_state["settings"] = settings
                    return cid

                self._set_ai_status("AI: категорії та позиції…")
                self._items = [
                    InvoiceItem(
                        name=i.name,
                        quantity=i.quantity,
                        price=i.price,
                        category=_map_category(i.category),
                    )
                    for i in merged
                ]
                self._set_ai_status("AI: оновлення форми…")

                self._ai_running = False
                self._ai_status_text = f"Готово: {len(self._items)} позицій"
                self._build()
                try:
                    self.update()
                except Exception:
                    pass
                try:
                    self.page.update()
                except Exception:
                    pass
            except Exception:
                # Показуємо коротке повідомлення без деталей помилки
                self._ai_running = False
                self._set_ai_status("AI: помилка (перевірте API ключ)")
                try:
                    self._ai_btn.on_click = self._pick_ai_image if bool(settings.gemini_api_key) else None
                    self._ai_btn.ink = bool(settings.gemini_api_key)
                    self._ai_btn.update()
                except Exception:
                    pass

        # safer than manual threading.Thread for Flet
        try:
            self.page.run_thread(run)
        except Exception:
            threading.Thread(target=run, daemon=True).start()

    # ── Save ──────────────────────────────────────────────────

    def _save(self, e):
        try:
            d = datetime.datetime.strptime(
                f"{self._date_field.value} {self._time_field.value}",
                "%d.%m.%Y %H:%M",
            )
        except ValueError:
            d = datetime.datetime.now()

        settings: AppSettings = self.app_state["settings"]
        base_currency = settings.default_currency
        receipt_currency = self._currency_field.value or DEFAULT_CURRENCY

        # Курс валют
        rate = None
        if receipt_currency != base_currency:
            # Якщо редагуємо чек і дата (по дню), валюта чеку та базова валюта
            # не змінилися — пере використовуємо вже збережений курс, щоб не
            # робити зайвий запит до API.
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
            business_name=self._shop_field.value.strip() or None,
            currency=receipt_currency,
            transaction_type=self._type,
            items=self._items,
            exchange_rate=rate,
            base_currency=base_currency,
        )
        if self.editing_receipt:
            receipt_kwargs["id"] = self.editing_receipt.id
        receipt = Receipt(**receipt_kwargs)

        # base_total обчислюється після створення (потрібен .total)
        if rate is not None:
            receipt.base_total = backend.convert_amount(receipt.total, rate)

        if self.editing_receipt:
            self.app_state["receipts"] = backend.update_receipt(receipt)
        else:
            self.app_state["receipts"] = backend.add_receipt(receipt)

        self.on_save()
