# -*- coding: utf-8 -*-
"""Bottom sheet item editor with category selector."""

from typing import Callable, List, Optional
import flet as ft

import backend
from backend.models import InvoiceItem, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr


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

    _lbl = ft.TextStyle(size=scaled(9), color=t.TEXT_DIMMER, font_family="monospace",
                        letter_spacing=scaled(1.2))
    _txt = ft.TextStyle(size=scaled(13), color=t.TEXT)

    name_f = ft.TextField(
        value=item.name if item else "",
        label=tr("item_editor.name"), hint_text=tr("item_editor.name_hint"),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(9), autofocus=True,
        label_style=_lbl, text_style=_txt,
        hint_style=ft.TextStyle(size=scaled(13), color=t.TEXT_DIMMER),
        content_padding=t.pad_sym(horizontal=scaled(12), vertical=scaled(12)),
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
        border_radius=scaled(9), expand=True,
        label_style=_lbl, text_style=_txt,
        content_padding=t.pad_sym(horizontal=scaled(12), vertical=scaled(12)),
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
        border_radius=scaled(9), expand=True,
        label_style=_lbl, text_style=_txt,
        content_padding=t.pad_sym(horizontal=scaled(12), vertical=scaled(12)),
    )

    error_text = ft.Text("", size=scaled(10), color=t.RED)

    # ── Category selector ─────────────────────────────────
    active_cats = [c for c in settings.categories if not c.deleted]
    default_cat_id = active_cats[0].id if active_cats else ""
    current_cat = [item.category if item else default_cat_id]
    adding_new_cat = [False]
    new_cat_field = ft.TextField(
        hint_text=tr("item_editor.category_hint"),
        bgcolor=t.SURFACE2, border_color=t.BORDER, focused_border_color=t.ACCENT,
        border_radius=scaled(9), expand=True,
        text_style=ft.TextStyle(size=scaled(13), color=t.TEXT),
        hint_style=ft.TextStyle(size=scaled(12), color=t.TEXT_DIMMER),
        content_padding=t.pad_sym(horizontal=scaled(12), vertical=scaled(8)),
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
                    ft.Text(cat.name, size=scaled(13),
                            color=t.ACCENT if sel else t.TEXT),
                    ft.Text("✓", size=scaled(13), color=t.ACCENT,
                            font_family="monospace") if sel else ft.Container(),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=t.alpha(t.ACCENT, "18") if sel else "transparent",
                padding=t.pad_sym(horizontal=scaled(14), vertical=scaled(10)),
                border_radius=scaled(8) if sel else 0,
                on_click=lambda e, c=cat: _sel_cat(c.id),
                ink=True,
            ))
        if adding_new_cat[0]:
            cat_col.controls.append(ft.Container(
                content=ft.Row([
                    new_cat_field,
                    ft.Container(
                        content=ft.Text("OK", size=scaled(11), color=t.WHITE,
                                        font_family="monospace",
                                        text_align=ft.TextAlign.CENTER),
                        width=scaled(36), height=scaled(36), border_radius=scaled(9),
                        bgcolor=t.ACCENT,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: _confirm_new_cat(),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("✕", size=scaled(11), color=t.TEXT_DIM,
                                        font_family="monospace",
                                        text_align=ft.TextAlign.CENTER),
                        width=scaled(36), height=scaled(36), border_radius=scaled(9),
                        bgcolor=t.SURFACE2,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: _cancel_new_cat(),
                        ink=True,
                    ),
                ], spacing=scaled(6)),
                padding=t.pad_sym(horizontal=scaled(10), vertical=scaled(6)),
            ))
        else:
            cat_col.controls.append(ft.Container(
                content=ft.Text(tr("item_editor.new_category"), size=scaled(12), color=t.ACCENT),
                padding=t.pad_sym(horizontal=scaled(14), vertical=scaled(10)),
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

    sheet_height = int((page.window.height or 720) * 0.7) #todo double check this one, does it need scaled()

    scrollable_body = ft.Column([
        name_f,
        ft.Row([qty_f, price_f], spacing=scaled(7)),
        ft.Container(
            content=ft.Text(tr("item_editor.category"), size=scaled(9), color=t.TEXT_DIMMER,
                            font_family="monospace",
                            style=ft.TextStyle(letter_spacing=scaled(1.2))),
            padding=t.pad_only(top=scaled(4), bottom=scaled(2)),
        ),
        ft.Container(
            content=ft.Column([cat_col], scroll=ft.ScrollMode.AUTO, spacing=0),
            expand=True,
            border=t.border_all(scaled(1), t.BORDER),
            border_radius=scaled(9),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        ),
        error_text,
    ], spacing=scaled(10), expand=True)

    buttons_row = ft.Container(
        content=ft.Row([
            ft.OutlinedButton(
                tr("item_editor.cancel"),
                style=ft.ButtonStyle(
                    color=t.TEXT_DIM,
                    side=ft.BorderSide(1, t.BORDER),
                    shape=ft.RoundedRectangleBorder(radius=scaled(9)),
                    padding=t.pad_sym(horizontal=scaled(18), vertical=scaled(10)),
                ),
                on_click=lambda e: _close_bs(),
            ),
            ft.ElevatedButton(
                tr("item_editor.add_item") if is_new else tr("item_editor.save"),
                bgcolor=t.ACCENT, color=t.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=scaled(9)),
                    padding=t.pad_sym(horizontal=scaled(18), vertical=scaled(10)),
                ),
                on_click=_confirm,
            ),
        ], alignment=ft.MainAxisAlignment.END, spacing=scaled(10)),
        padding=t.pad_only(top=scaled(8), bottom=scaled(8)),
        border=t.border_top(),
    )

    sheet_content = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Container(width=scaled(36), height=scaled(4), border_radius=scaled(2),
                                     bgcolor=t.TEXT_DIMMER),
                alignment=ft.Alignment(0, 0),
                padding=t.pad_only(top=scaled(10), bottom=scaled(4)),
            ),
            ft.Text(tr("item_editor.new_item") if is_new else tr("item_editor.editing"),
                    size=scaled(15), color=t.TEXT, weight=ft.FontWeight.W_600),
            scrollable_body,
            buttons_row,
        ], spacing=scaled(6)),
        padding=t.pad_sym(horizontal=scaled(18), vertical=0),
        bgcolor=t.SURFACE,
        height=sheet_height,
        border_radius=ft.BorderRadius(top_left=scaled(16), top_right=scaled(16),
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
