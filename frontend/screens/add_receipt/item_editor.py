# -*- coding: utf-8 -*-
"""Bottom sheet item editor with category selector."""

from typing import Callable, List, Optional
import flet as ft

import backend
from backend.models import InvoiceItem, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import (
    FONT_SM, FONT_SM_MD, FONT_MD, FONT_BODY, FONT_LG, FONT_TITLE,
    LETTER_SPACING, PAD_PAGE_H, FIELD_RADIUS, BORDER_WIDTH,
    BTN_RADIUS, BTN_PAD_H, BTN_PAD_V, GAP_MD, GAP_LG, GAP_XL,
)
from frontend.screens.add_receipt.sizes import (
    ACTION_BTN_SIZE, SHEET_HANDLE_W, SHEET_HANDLE_H, SHEET_RADIUS,
    SHEET_HANDLE_PAD_TOP, SHEET_HANDLE_PAD_BOTTOM,
    CAT_ITEM_PAD_H, CAT_ITEM_PAD_V, CAT_SELECTOR_RADIUS,
    EDITOR_FIELD_PAD, NEW_CAT_ROW_PAD_H, NEW_CAT_ROW_PAD_V, CAT_BTN_GAP,
    FORM_GAP,
)


def open_item_editor(page: ft.Page, app_state, items: List[InvoiceItem],
                     item: Optional[InvoiceItem], idx: Optional[int],
                     on_done: Callable):
    """Open a bottom sheet to add/edit an item.

    Parameters:
        page: Flet page reference
        app_state: AppState instance
        items: mutable items list (will be modified in-place)
        item: existing item to edit, or None for new
        idx: index of item in list, or None for new
        on_done: callback() after item is added/edited
    """
    settings: AppSettings = app_state.settings
    is_new = item is None

    _lbl = ft.TextStyle(size=scaled(FONT_SM), color=t.TEXT_DIMMER, font_family="monospace",
                        letter_spacing=scaled(LETTER_SPACING))
    _txt = ft.TextStyle(size=scaled(FONT_LG), color=t.TEXT)

    name_f = ft.TextField(
        value=item.name if item else "",
        label=tr("item_editor.name"), hint_text=tr("item_editor.name_hint"),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(FIELD_RADIUS), autofocus=True,
        label_style=_lbl, text_style=_txt,
        hint_style=ft.TextStyle(size=scaled(FONT_LG), color=t.TEXT_DIMMER),
        content_padding=t.pad_sym(horizontal=scaled(EDITOR_FIELD_PAD), vertical=scaled(EDITOR_FIELD_PAD)),
    )

    default_quantity = "1"

    qty_f = ft.TextField(
        value=str(item.quantity) if item else default_quantity,
        hint_text="",
        label=tr("item_editor.quantity"), keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^(\d+(\.\d{0,2})?)?$",
            replacement_string=""
        ),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(FIELD_RADIUS), expand=True,
        label_style=_lbl, text_style=_txt,
        content_padding=t.pad_sym(horizontal=scaled(EDITOR_FIELD_PAD), vertical=scaled(EDITOR_FIELD_PAD)),
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

    qty_f.on_focus = _price_on_focus
    qty_f.on_blur = _price_on_blur

    price_f = ft.TextField(
        value=str(item.price) if item else "",
        hint_text="",
        label=tr("item_editor.price"), keyboard_type=ft.KeyboardType.NUMBER,
        input_filter=ft.InputFilter(
            allow=True,
            regex_string=r"^(\d+(\.\d{0,2})?)?$",
            replacement_string=""
        ),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(FIELD_RADIUS), expand=True,
        label_style=_lbl, text_style=_txt,
        content_padding=t.pad_sym(horizontal=scaled(EDITOR_FIELD_PAD), vertical=scaled(EDITOR_FIELD_PAD)),
    )

    error_text = ft.Text("", size=scaled(FONT_SM_MD), color=t.RED)

    # ── Category selector ─────────────────────────────────
    active_cats = [c for c in settings.categories if not c.deleted]
    default_cat_id = active_cats[0].id if active_cats else ""
    current_cat = [item.category if item else default_cat_id]
    adding_new_cat = [False]
    new_cat_field = ft.TextField(
        hint_text=tr("item_editor.category_hint"),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(FIELD_RADIUS), expand=True,
        text_style=ft.TextStyle(size=scaled(FONT_LG), color=t.TEXT),
        hint_style=ft.TextStyle(size=scaled(FONT_BODY), color=t.TEXT_DIMMER),
        content_padding=t.pad_sym(horizontal=scaled(EDITOR_FIELD_PAD), vertical=scaled(8)),
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
                    ft.Text(cat.name, size=scaled(FONT_LG),
                            color=t.ACCENT if sel else t.TEXT),
                    ft.Text("✓", size=scaled(FONT_LG), color=t.ACCENT,
                            font_family="monospace") if sel else ft.Container(),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=t.alpha(t.ACCENT, "18") if sel else "transparent",
                padding=t.pad_sym(horizontal=scaled(CAT_ITEM_PAD_H), vertical=scaled(CAT_ITEM_PAD_V)),
                border_radius=scaled(CAT_SELECTOR_RADIUS) if sel else 0,
                on_click=lambda e, c=cat: _sel_cat(c.id),
                ink=True,
            ))
        if adding_new_cat[0]:
            cat_col.controls.append(ft.Container(
                content=ft.Row([
                    new_cat_field,
                    ft.Container(
                        content=ft.Text("OK", size=scaled(FONT_MD), color=t.WHITE,
                                        font_family="monospace",
                                        text_align=ft.TextAlign.CENTER),
                        width=scaled(ACTION_BTN_SIZE), height=scaled(ACTION_BTN_SIZE),
                        border_radius=scaled(FIELD_RADIUS),
                        bgcolor=t.ACCENT,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: _confirm_new_cat(),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("✕", size=scaled(FONT_MD), color=t.TEXT_DIM,
                                        font_family="monospace",
                                        text_align=ft.TextAlign.CENTER),
                        width=scaled(ACTION_BTN_SIZE), height=scaled(ACTION_BTN_SIZE),
                        border_radius=scaled(FIELD_RADIUS),
                        bgcolor=t.SURFACE2,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: _cancel_new_cat(),
                        ink=True,
                    ),
                ], spacing=scaled(CAT_BTN_GAP)),
                padding=t.pad_sym(horizontal=scaled(NEW_CAT_ROW_PAD_H), vertical=scaled(NEW_CAT_ROW_PAD_V)),
            ))
        else:
            cat_col.controls.append(ft.Container(
                content=ft.Text(tr("item_editor.new_category"), size=scaled(FONT_BODY), color=t.ACCENT),
                padding=t.pad_sym(horizontal=scaled(CAT_ITEM_PAD_H), vertical=scaled(CAT_ITEM_PAD_V)),
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
        existing_id = settings.get_category_id_by_name(name)
        if existing_id is not None:
            current_cat[0] = existing_id
            error_text.value = tr("item_editor.category_exists")
            try:
                error_text.update()
            except Exception:
                pass
            adding_new_cat[0] = False
            _build_cats()
            return
        cid = settings.ensure_category(name)
        backend.save_settings(settings)
        app_state.settings = settings
        current_cat[0] = cid
        error_text.value = ""
        try:
            error_text.update()
        except Exception:
            pass
        adding_new_cat[0] = False
        _build_cats()

    _build_cats()

    # ── Bottom sheet ──────────────────────────────────────
    bs_ref: list = [None]

    def _close_bs():
        bs_ref[0].open = False
        page.update()

    def _confirm(e):
        name = name_f.value.strip()
        if not name:
            error_text.value = tr("item_editor.enter_name")
            error_text.update()
            return
        try:
            qty = float(qty_f.value or "1")
            price = float(price_f.value or "0")
        except ValueError:
            error_text.value = tr("item_editor.invalid_number")
            error_text.update()
            return

        item_kwargs = dict(name=name, quantity=qty, price=price,
                           category=current_cat[0])
        if item:
            item_kwargs["id"] = item.id
        new_item = InvoiceItem(**item_kwargs)
        if is_new:
            items.append(new_item)
        else:
            items[idx] = new_item

        on_done()
        _close_bs()

    sheet_height = int((page.window.height or 720) * 0.7)

    scrollable_body = ft.Column([
        name_f,
        ft.Row([qty_f, price_f], spacing=scaled(FORM_GAP)),
        ft.Container(
            content=ft.Text(tr("item_editor.category"), size=scaled(FONT_SM), color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=scaled(LETTER_SPACING))),
            padding=t.pad_only(top=scaled(4), bottom=scaled(2)),
        ),
        ft.Container(
            content=ft.Column([cat_col], scroll=ft.ScrollMode.AUTO, spacing=0),
            expand=True,
            border=t.border_all(scaled(BORDER_WIDTH), t.BORDER),
            border_radius=scaled(FIELD_RADIUS),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ),
        error_text,
    ], spacing=scaled(GAP_XL), expand=True)

    buttons_row = ft.Container(
        content=ft.Row([
            ft.OutlinedButton(
                tr("item_editor.cancel"),
                style=ft.ButtonStyle(
                    color=t.TEXT_DIM,
                    side=ft.BorderSide(1, t.BORDER),
                    shape=ft.RoundedRectangleBorder(radius=scaled(BTN_RADIUS)),
                    padding=t.pad_sym(horizontal=scaled(BTN_PAD_H), vertical=scaled(BTN_PAD_V)),
                ),
                on_click=lambda e: _close_bs(),
            ),
            ft.ElevatedButton(
                tr("item_editor.add_item") if is_new else tr("item_editor.save"),
                bgcolor=t.ACCENT, color=t.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=scaled(BTN_RADIUS)),
                    padding=t.pad_sym(horizontal=scaled(BTN_PAD_H), vertical=scaled(BTN_PAD_V)),
                ),
                on_click=_confirm,
            ),
        ], alignment=ft.MainAxisAlignment.END, spacing=scaled(GAP_XL)),
        padding=t.pad_only(top=scaled(GAP_LG), bottom=scaled(GAP_LG)),
        border=t.border_top(),
    )

    sheet_content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Container(width=scaled(SHEET_HANDLE_W), height=scaled(SHEET_HANDLE_H),
                                     border_radius=scaled(2),
                                     bgcolor=t.TEXT_DIMMER),
                alignment=ft.Alignment(0, 0),
                padding=t.pad_only(top=scaled(SHEET_HANDLE_PAD_TOP), bottom=scaled(SHEET_HANDLE_PAD_BOTTOM)),
            ),
            ft.Text(tr("item_editor.new_item") if is_new else tr("item_editor.editing"),
                    size=scaled(FONT_TITLE), color=t.TEXT, weight=ft.FontWeight.W_600),
            scrollable_body,
            buttons_row,
        ], spacing=scaled(GAP_MD)),
        padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=0),
        bgcolor=t.SURFACE,
        height=sheet_height,
        border_radius=ft.BorderRadius(top_left=scaled(SHEET_RADIUS), top_right=scaled(SHEET_RADIUS),
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
    page.overlay.append(bs)
    page.update()
    bs.open = True
    page.update()
