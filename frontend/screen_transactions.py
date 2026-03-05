# -*- coding: utf-8 -*-
"""
frontend/screen_transactions.py
Screen 01 — Transactions list (Daily / Total tabs, multi-select).
Compatible with Flet >= 0.80.0
"""

import datetime
import flet as ft
from collections import defaultdict
from typing import Callable, List, Set

import backend
from backend.models import Receipt
from frontend import theme as t


class TransactionsScreen(ft.Column):
    def __init__(self, app_state: dict, on_add: Callable, on_refresh: Callable):
        super().__init__(spacing=0, expand=True)
        self.app_state = app_state
        self.on_add = on_add
        self.on_refresh = on_refresh
        self.tab_mode = "daily"
        self.selected_ids: Set[str] = set()
        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        self._build()

    def refresh(self):
        self._build()
        self.update()

    def _build(self):
        self.controls.clear()
        receipts = self.app_state.get("receipts", [])

        # Фільтр для підсумків місяця (завжди тільки поточний місяць)
        month_receipts = [
            r
            for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]

        summary = backend.get_summary(month_receipts)

        # Фільтр для списку чеків:
        # - Daily / Total: тільки поточний місяць
        # - Weekly: повний діапазон тижнів, які перетинаються з місяцем
        if self.tab_mode in ("daily", "total"):
            filtered = month_receipts
        elif self.tab_mode == "weekly":
            # перший та останній день місяця
            month_start = datetime.date(self._year, self._month, 1)
            if self._month == 12:
                next_month = datetime.date(self._year + 1, 1, 1)
            else:
                next_month = datetime.date(self._year, self._month + 1, 1)
            month_end = next_month - datetime.timedelta(days=1)

            # розширений діапазон по тижнях (понеділок–неділя),
            # щоб захопити дні із сусідніх місяців, які входять у тижні цього місяця
            start_week = month_start - datetime.timedelta(days=month_start.weekday())
            end_week = month_end + datetime.timedelta(days=(6 - month_end.weekday()))

            filtered = [
                r
                for r in receipts
                if start_week
                <= r.created_date.date()
                <= end_week
            ]
        else:
            filtered = receipts

        self.controls += [
            self._month_header(),
            self._summary_row(summary),
            self._period_tabs(),
        ]
        if self.selected_ids:
            self.controls.append(self._selection_bar())
        self.controls.append(self._receipts_list(filtered))

    # ── Month header ──────────────────────────────────────────

    def _month_header(self) -> ft.Container:
        month_label = f"{t.UA_MONTHS_SHORT[self._month]} {self._year}"
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Container(
                        content=ft.Text("‹", size=14, color=t.TEXT_DIM),
                        on_click=lambda e: self._prev_month(),
                        ink=True, padding=t.pad_sym(horizontal=4, vertical=2),
                    ),
                    ft.Text(month_label, size=14, color=t.TEXT,
                            weight=ft.FontWeight.W_600),
                    ft.Container(
                        content=ft.Text("›", size=14, color=t.TEXT_DIM),
                        on_click=lambda e: self._next_month(),
                        ink=True, padding=t.pad_sym(horizontal=4, vertical=2),
                    ),
                ], spacing=5),
                ft.Row([
                    ft.Container(
                        content=ft.Text("✓", size=12, color=t.TEXT_DIM,
                                        font_family="monospace"),
                        width=30, height=30, border_radius=8,
                        bgcolor=t.SURFACE2, border=t.border_all(),
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda e: self._toggle_select_all(),
                        ink=True,
                    ),
                    ft.Container(
                        content=ft.Text("···", size=12, color=t.TEXT_DIM,
                                        font_family="monospace"),
                        width=30, height=30, border_radius=8,
                        bgcolor=t.SURFACE2, border=t.border_all(),
                        alignment=ft.Alignment(0, 0),
                        ink=True,
                    ),
                ], spacing=6),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=18, right=18, top=8, bottom=6),
        )

    # ── Summary ──────────────────────────────────────────────

    def _summary_row(self, summary: dict) -> ft.Container:
        base_cur = self.app_state["settings"].default_currency
        def stat(lbl, val, color):
            return ft.Column([
                ft.Text(lbl.upper(), size=9, color=t.TEXT_DIMMER,
                        font_family="monospace",
                        style=ft.TextStyle(letter_spacing=1.2)),
                ft.Text(t.format_amount(val, currency=base_cur), size=14, color=color,
                        weight=ft.FontWeight.W_600, font_family="monospace"),
            ], spacing=3, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        return ft.Container(
            content=ft.Row([
                stat("Дохід",   summary["income"],   t.BLUE),
                ft.VerticalDivider(width=1, color=t.BORDER),
                stat("Витрати", summary["expenses"], t.RED),
                ft.VerticalDivider(width=1, color=t.BORDER),
                stat("Залишок", summary["balance"],  t.TEXT),
            ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            padding=t.pad_only(left=18, right=18, bottom=10, top=4),
            border=t.border_bottom(),
        )

    # ── Period tabs ───────────────────────────────────────────

    def _period_tabs(self) -> ft.Container:
        def tab(label, mode):
            active = self.tab_mode == mode
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=11,
                            color=t.TEXT if active else t.TEXT_DIMMER,
                            font_family="monospace",
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(
                        height=2,
                        bgcolor=t.ACCENT if active else "transparent",
                        border_radius=2,
                        margin=t.mar_only(top=6),
                    ),
                ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=True,
                padding=t.pad_sym(vertical=9),
                on_click=lambda e, m=mode: self._set_tab(m),
                ink=True,
            )

        return ft.Container(
            content=ft.Row(
                [
                    tab("Daily", "daily"),
                    tab("Weekly", "weekly"),
                    tab("Total", "total"),
                ],
                spacing=0,
            ),
            border=t.border_bottom(),
        )

    # ── Selection bar ─────────────────────────────────────────

    def _selection_bar(self) -> ft.Container:
        count = len(self.selected_ids)
        return ft.Container(
            content=ft.Row([
                ft.Text(f"{count} обрано", size=10, color=t.ACCENT,
                        font_family="monospace"),
                ft.Row([
                    ft.TextButton("Видалити",
                                  style=ft.ButtonStyle(color=t.RED),
                                  on_click=self._delete_selected),
                    ft.Text("·", size=10, color=t.TEXT_DIMMER),
                    ft.TextButton("Змінити дату",
                                  style=ft.ButtonStyle(color=t.TEXT_DIM),
                                  on_click=self._change_date_selected),
                ], spacing=0),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=t.alpha(t.ACCENT, "18"),
            padding=t.pad_sym(horizontal=18, vertical=5),
            border=t.border_bottom(color=t.alpha(t.ACCENT, "28")),
        )

    # ── Receipts list ─────────────────────────────────────────

    def _receipts_list(self, receipts: List[Receipt]) -> ft.Column:
        if not receipts:
            return ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Немає записів",
                                    size=13,
                                    color=t.TEXT_DIMMER,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Text(
                                    "Натисніть + щоб додати чек",
                                    size=11,
                                    color=t.TEXT_DIMMER,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                        ),
                        padding=40,
                        alignment=ft.Alignment(0, 0),
                    )
                ],
                expand=True,
            )

        # TOTAL: плоский список без групування, від новішого до старішого
        if self.tab_mode == "total":
            sorted_receipts = sorted(
                receipts, key=lambda r: r.created_date, reverse=True
            )
            rows = [self._receipt_row(r) for r in sorted_receipts]
            return ft.Column(
                controls=rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0
            )

        # DAILY / WEEKLY — з групуванням
        rows: List[ft.Control] = []

        if self.tab_mode == "daily":
            groups = defaultdict(list)
            for r in receipts:
                day = r.created_date.date()
                groups[day].append(r)

            for day in sorted(groups.keys(), reverse=True):
                day_receipts = sorted(
                    groups[day], key=lambda r: r.created_date, reverse=True
                )
                day_total = sum(r.effective_total for r in day_receipts)
                rows.append(
                    self._day_header(day_receipts[0].created_date, day_total, day_receipts)
                )
                # Розділювач між заголовком дня та списком чеків
                rows.append(
                    ft.Container(
                        content=ft.Divider(height=1, color=t.BORDER),
                        padding=t.pad_sym(horizontal=18),
                    )
                )
                for receipt in day_receipts:
                    rows.append(self._receipt_row(receipt))

        elif self.tab_mode == "weekly":
            groups = defaultdict(list)
            for r in receipts:
                d = r.created_date.date()
                # початок тижня (понеділок)
                week_start = d - datetime.timedelta(days=d.weekday())
                groups[week_start].append(r)

            for week_start in sorted(groups.keys(), reverse=True):
                week_receipts = sorted(
                    groups[week_start], key=lambda r: r.created_date, reverse=True
                )
                week_total = sum(r.effective_total for r in week_receipts)
                rows.append(self._week_header(week_start, week_total, week_receipts))
                rows.append(
                    ft.Container(
                        content=ft.Divider(height=1, color=t.BORDER),
                        padding=t.pad_sym(horizontal=18),
                    )
                )
                for receipt in week_receipts:
                    rows.append(self._receipt_row(receipt))

        return ft.Column(
            controls=rows, scroll=ft.ScrollMode.AUTO, expand=True, spacing=0
        )

    def _day_header(self, date: datetime.datetime, total: float,
                    day_receipts: List[Receipt]) -> ft.Container:
        has_expense = any(r.transaction_type == "expense" for r in day_receipts)
        color = t.RED if has_expense else t.BLUE
        day_name = t.UA_DAYS_SHORT.get(date.weekday(), date.strftime("%a"))
        settings = self.app_state["settings"]
        base_amount_str = f"≈ {t.format_amount(total, currency=settings.default_currency)}"
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Text(date.strftime("%d"), size=19, color=t.TEXT,
                            weight=ft.FontWeight.W_600, font_family="monospace"),
                    ft.Text(f"{day_name} · {date.strftime('%m.%y')}",
                            size=9, color=t.TEXT_DIMMER, font_family="monospace"),
                ], spacing=8),
                ft.Text(base_amount_str,
                        size=11, color=color, font_family="monospace"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=t.pad_only(left=18, right=18, top=8, bottom=3),
        )

    def _week_header(
        self,
        week_start: datetime.date,
        total: float,
        week_receipts: List[Receipt],
    ) -> ft.Container:
        has_expense = any(r.transaction_type == "expense" for r in week_receipts)
        color = t.RED if has_expense else t.BLUE
        settings = self.app_state["settings"]
        week_end = week_start + datetime.timedelta(days=6)
        label = f"{week_start.strftime('%d.%m')} – {week_end.strftime('%d.%m')}"
        base_amount_str = f"≈ {t.format_amount(total, currency=settings.default_currency)}"
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        label,
                        size=13,
                        color=t.TEXT,
                        weight=ft.FontWeight.W_600,
                        font_family="monospace",
                    ),
                    ft.Text(
                        base_amount_str,
                        size=11,
                        color=color,
                        font_family="monospace",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=t.pad_only(left=18, right=18, top=8, bottom=3),
        )

    def _receipt_row(self, receipt: Receipt) -> ft.Container:
        is_sel = receipt.id in self.selected_ids
        color  = t.RED if receipt.transaction_type == "expense" else t.BLUE
        sign   = "−" if receipt.transaction_type == "expense" else "+"

        # Checkbox — toggles selection on click
        checkbox = ft.Container(
            width=16, height=16, border_radius=6,
            bgcolor=t.ACCENT if is_sel else "transparent",
            border=t.border_all(1.5, t.ACCENT if is_sel else t.BORDER),
            # content=ft.Text("✓", size=10, color=t.WHITE,
            #                 text_align=ft.TextAlign.CENTER) if is_sel else None,
            alignment=ft.Alignment(0, 0),
            on_click=lambda e, r=receipt: self._toggle_select(r.id),
            ink=True,
        )

        # categories_summary тепер містить ID; для виводу беремо назви з settings
        settings = self.app_state["settings"]
        n_items = len(receipt.items)
        cat_names = list(
            dict.fromkeys(
                settings.get_category_name(item.category) for item in receipt.items
            )
        )
        cats_str = ", ".join(cat_names[:3]) + ("..." if len(cat_names) > 3 else "")
        dt_str = receipt.created_date.strftime("%d.%m %H:%M")
        sub_text = f"{dt_str} · {n_items} позицій · {cats_str}"
        # Основна сума чеку: якщо валюта ≠ базова й є конвертація,
        # показуємо "CUR X -> ≈ base", інакше — стандартний формат.
        base_cur = settings.default_currency
        if receipt.transaction_type == "expense":
            sign = "−"
        elif receipt.transaction_type == "income":
            sign = "+"
        else:
            sign = ""

        if receipt.currency != base_cur and receipt.base_total is not None:
            # Оригінальна сума без знаку; t.format_amount повертає "<symbol><amount>"
            raw_orig = t.format_amount(receipt.total, sign=False, currency=receipt.currency)
            # Знаходимо, де починається числова частина
            idx = 0
            while idx < len(raw_orig) and not (raw_orig[idx].isdigit() or raw_orig[idx] in ".,"):
                idx += 1
            orig_numeric = raw_orig[idx:].lstrip()
            orig_part = f"{receipt.currency} {orig_numeric}"

            base_part = t.format_amount(receipt.base_total, sign=False, currency=base_cur)
            amount_str = f"{sign}{orig_part} -> ≈ {base_part}"
        else:
            amount_str = t.format_amount(receipt.total, sign=True, currency=receipt.currency)

        # Row content — opens receipt for viewing/editing on click
        row_content = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(receipt.business_name or "Чек", size=13,
                            color=t.TEXT, weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(sub_text, size=9, color=t.TEXT_DIMMER),
                ], spacing=2, expand=True),
                ft.Text(amount_str, size=12, color=color,
                        font_family="monospace", weight=ft.FontWeight.W_500),
            ], spacing=9),
            expand=True,
            on_click=lambda e, r=receipt: self.on_add(receipt=r),
            ink=True,
        )

        return ft.Container(
            content=ft.Row([checkbox, row_content], spacing=9),
            bgcolor=t.alpha(t.ACCENT, "0f") if is_sel else "transparent",
            padding=t.pad_sym(horizontal=18, vertical=8),
        )

    # ── Handlers ─────────────────────────────────────────────

    def _prev_month(self):
        if self._month == 1:
            self._month = 12
            self._year -= 1
        else:
            self._month -= 1
        self.selected_ids.clear()
        self._build()
        self.update()

    def _next_month(self):
        if self._month == 12:
            self._month = 1
            self._year += 1
        else:
            self._month += 1
        self.selected_ids.clear()
        self._build()
        self.update()

    def _toggle_select_all(self):
        receipts = self.app_state.get("receipts", [])
        month_receipts = [
            r for r in receipts
            if r.created_date.year == self._year
            and r.created_date.month == self._month
        ]
        all_ids = {r.id for r in month_receipts}
        if self.selected_ids == all_ids:
            self.selected_ids.clear()
        else:
            self.selected_ids = all_ids
        self._build()
        self.update()

    def _set_tab(self, mode: str):
        self.tab_mode = mode
        self.selected_ids.clear()
        self._build()
        self.update()

    def _toggle_select(self, rid: str):
        if rid in self.selected_ids:
            self.selected_ids.discard(rid)
        else:
            self.selected_ids.add(rid)
        self._build()
        self.update()

    def _delete_selected(self, e):
        if not self.selected_ids:
            return
        self.app_state["receipts"] = backend.delete_receipts(list(self.selected_ids))
        self.selected_ids.clear()
        self._build()
        self.update()

    def _change_date_selected(self, e):
        def on_picked(ev):
            picked = ev.control.value
            if picked:
                new_dt = datetime.datetime.combine(picked, datetime.time(12, 0))
                self.app_state["receipts"] = backend.update_receipts_date(
                    list(self.selected_ids), new_dt)
                self.selected_ids.clear()
                self._build()
                self.update()

        dp = ft.DatePicker(
            first_date=datetime.datetime(2020, 1, 1),
            last_date=datetime.datetime(2030, 12, 31),
            on_change=on_picked,
        )
        self.page.show_dialog(dp)
