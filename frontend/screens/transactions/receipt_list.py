# -*- coding: utf-8 -*-
"""Receipt list with grouping (daily/weekly/total) and receipt row rendering."""

import datetime
from collections import defaultdict
from typing import Callable, List, Set

import flet as ft

from backend.models import Receipt, AppSettings
from frontend import theme as t
from frontend.theme import scaled
from frontend.localisation import t as tr
from frontend.sizes import (
    FONT_SM, FONT_MD, FONT_BODY, FONT_LG,
    PAD_PAGE_H, GAP_XS, GAP_MD, ICON_BTN_SM, ICON_BTN_RADIUS,
)
from frontend.screens.transactions.sizes import (
    DATE_DAY_FONT, HEADER_AMOUNT_FONT, ROW_PAD_V, ROW_HEADER_PAD_BOTTOM,
    ROW_GAP, AMOUNT_FONT, CHECKBOX_SIZE, CHECKBOX_RADIUS,
    EMPTY_PAD,
)


def build_receipt_list(receipts: List[Receipt], tab_mode: str,
                       selected_ids: Set[str], app_state,
                       on_toggle_select: Callable[[str], None],
                       on_edit: Callable) -> ft.Column:
    if not receipts:
        return ft.Column(
            [ft.Container(
                content=ft.Column([
                    ft.Text(tr("transactions.no_records"), size=scaled(FONT_LG), color=t.TEXT_DIMMER,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(tr("transactions.hint_add"), size=scaled(FONT_MD),
                            color=t.TEXT_DIMMER, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=scaled(GAP_MD)),
                padding=scaled(EMPTY_PAD), alignment=ft.Alignment(0, 0),
            )],
            expand=True,
        )

    if tab_mode == "total":
        sorted_receipts = sorted(receipts, key=lambda r: r.created_date, reverse=True)
        rows = [_receipt_row(r, selected_ids, app_state, on_toggle_select, on_edit, show_date=True)
                for r in sorted_receipts]
        return ft.Column(controls=rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)

    rows: List[ft.Control] = []

    if tab_mode == "daily":
        groups = defaultdict(list)
        for r in receipts:
            groups[r.created_date.date()].append(r)

        for day in sorted(groups.keys(), reverse=True):
            day_receipts = sorted(groups[day], key=lambda r: r.created_date, reverse=True)
            day_total = sum(r.effective_total for r in day_receipts)
            rows.append(_day_header(day_receipts[0].created_date, day_total, day_receipts, app_state))
            rows.append(ft.Container(
                content=ft.Divider(height=1, color=t.BORDER),
                padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H)),
            ))
            for receipt in day_receipts:
                rows.append(_receipt_row(receipt, selected_ids, app_state, on_toggle_select, on_edit))

    elif tab_mode == "weekly":
        groups = defaultdict(list)
        for r in receipts:
            d = r.created_date.date()
            week_start = d - datetime.timedelta(days=d.weekday())
            groups[week_start].append(r)

        for week_start in sorted(groups.keys(), reverse=True):
            week_receipts = sorted(groups[week_start], key=lambda r: r.created_date, reverse=True)
            week_total = sum(r.effective_total for r in week_receipts)
            rows.append(_week_header(week_start, week_total, week_receipts, app_state))
            rows.append(ft.Container(
                content=ft.Divider(height=1, color=t.BORDER),
                padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H)),
            ))
            for receipt in week_receipts:
                rows.append(_receipt_row(receipt, selected_ids, app_state, on_toggle_select, on_edit))

    return ft.Column(controls=rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)


def _day_header(date: datetime.datetime, total: float,
                day_receipts: List[Receipt], app_state) -> ft.Container:
    has_expense = any(r.transaction_type == "expense" for r in day_receipts)
    color = t.RED if has_expense else t.BLUE
    day_name = t.get_days_short().get(date.weekday(), date.strftime("%a"))
    settings: AppSettings = app_state.settings
    base_amount_str = f"≈ {t.format_amount(total, currency=settings.default_currency)}"
    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Text(date.strftime("%d"), size=scaled(DATE_DAY_FONT), color=t.TEXT,
                        weight=ft.FontWeight.W_600, font_family="monospace"),
                ft.Text(f"{day_name} · {date.strftime('%m.%y')}",
                        size=scaled(FONT_SM), color=t.TEXT_DIMMER, font_family="monospace"),
            ], spacing=scaled(8)),
            ft.Text(base_amount_str, size=scaled(HEADER_AMOUNT_FONT), color=color, font_family="monospace"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           top=scaled(ROW_PAD_V), bottom=scaled(ROW_HEADER_PAD_BOTTOM)),
    )


def _week_header(week_start: datetime.date, total: float,
                 week_receipts: List[Receipt], app_state) -> ft.Container:
    has_expense = any(r.transaction_type == "expense" for r in week_receipts)
    color = t.RED if has_expense else t.BLUE
    settings: AppSettings = app_state.settings
    week_end = week_start + datetime.timedelta(days=6)
    label = f"{week_start.strftime('%d.%m')} – {week_end.strftime('%d.%m')}"
    base_amount_str = f"≈ {t.format_amount(total, currency=settings.default_currency)}"
    return ft.Container(
        content=ft.Row([
            ft.Text(label, size=scaled(DATE_DAY_FONT), color=t.TEXT,
                    weight=ft.FontWeight.W_600, font_family="monospace"),
            ft.Text(base_amount_str, size=scaled(HEADER_AMOUNT_FONT), color=color, font_family="monospace"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=t.pad_only(left=scaled(PAD_PAGE_H), right=scaled(PAD_PAGE_H),
                           top=scaled(ROW_PAD_V), bottom=scaled(ROW_HEADER_PAD_BOTTOM)),
    )


def _receipt_row(receipt: Receipt, selected_ids: Set[str], app_state,
                 on_toggle_select: Callable[[str], None],
                 on_edit: Callable, show_date: bool = False) -> ft.Container:
    is_sel = receipt.id in selected_ids
    color = t.RED if receipt.transaction_type == "expense" else t.BLUE

    checkbox = ft.Container(
        width=scaled(CHECKBOX_SIZE), height=scaled(CHECKBOX_SIZE), border_radius=scaled(CHECKBOX_RADIUS),
        bgcolor=t.ACCENT if is_sel else "transparent",
        border=t.border_all(1.5, t.ACCENT if is_sel else t.BORDER),
        alignment=ft.Alignment(0, 0),
        on_click=lambda e, r=receipt: on_toggle_select(r.id),
        ink=True,
    )

    settings: AppSettings = app_state.settings
    n_items = len(receipt.items)
    cat_names = list(dict.fromkeys(
        settings.get_category_name(item.category) for item in receipt.items
    ))
    cats_str = ", ".join(cat_names[:3]) + ("..." if len(cat_names) > 3 else "")
    time_str = receipt.created_date.strftime("%d.%m %H:%M") if show_date else receipt.created_date.strftime("%H:%M")
    sub_text = f"{time_str} · {n_items} {tr('transactions.items_suffix')} · {cats_str}"

    base_cur = settings.default_currency
    if receipt.transaction_type == "expense":
        sign = "−"
    elif receipt.transaction_type == "income":
        sign = "+"
    else:
        sign = ""

    if receipt.currency != base_cur and receipt.base_total is not None:
        raw_orig = t.format_amount(receipt.total, sign=False, currency=receipt.currency)
        idx = 0
        while idx < len(raw_orig) and not (raw_orig[idx].isdigit() or raw_orig[idx] in ".,"):
            idx += 1
        orig_numeric = raw_orig[idx:].lstrip()
        orig_part = f"{receipt.currency} {orig_numeric}"
        base_part = t.format_amount(receipt.base_total, sign=False, currency=base_cur)
        amount_str = f"{sign}{orig_part} -> ≈ {base_part}"
    else:
        amount_str = t.format_amount(receipt.total, sign=True, currency=receipt.currency)

    row_content = ft.Container(
        content=ft.Row([
            ft.Column([
                ft.Text(receipt.business_name or tr("transactions.receipt"), size=scaled(FONT_LG),
                        color=t.TEXT, weight=ft.FontWeight.W_500,
                        overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(sub_text, size=scaled(FONT_SM), color=t.TEXT_DIMMER),
            ], spacing=scaled(GAP_XS), expand=True),
            ft.Text(amount_str, size=scaled(AMOUNT_FONT), color=color,
                    font_family="monospace", weight=ft.FontWeight.W_500),
        ], spacing=scaled(ROW_GAP)),
        expand=True,
        on_click=lambda e, r=receipt: on_edit(receipt=r),
        ink=True,
    )

    return ft.Container(
        content=ft.Row([checkbox, row_content], spacing=scaled(ROW_GAP)),
        bgcolor=t.alpha(t.ACCENT, "0f") if is_sel else "transparent",
        padding=t.pad_sym(horizontal=scaled(PAD_PAGE_H), vertical=scaled(ROW_PAD_V)),
    )
