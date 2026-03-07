# -*- coding: utf-8 -*-
"""backend/analytics.py — Pure computation on receipt data (no disk I/O)."""

import datetime
from typing import List

from backend.models import Receipt


def filter_receipts_by_period(receipts: List[Receipt], mode: str) -> List[Receipt]:
    if mode == "total":
        return receipts
    start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return [r for r in receipts if r.created_date >= start]


def get_monthly_totals(receipts: List[Receipt], tx_type: str = "expense",
                       target_year: int = None, target_month: int = None) -> dict:
    """Return totals for 6 consecutive months.

    If *target_year*/*target_month* are given the target month is placed at the
    penultimate position (index 4 of 6).  Otherwise the current month is last.
    """
    month_keys = []

    if target_year is not None and target_month is not None:
        for i in range(6):
            abs_m = target_year * 12 + (target_month - 1) + (i - 4)
            y, m = divmod(abs_m, 12)
            month_keys.append((y, m + 1))
    else:
        now = datetime.datetime.now()
        for i in range(6):
            abs_m = now.year * 12 + (now.month - 1) + (i - 5)
            y, m = divmod(abs_m, 12)
            month_keys.append((y, m + 1))

    totals = {}
    for y, m in month_keys:
        key = datetime.date(y, m, 1).strftime("%b")
        totals[key] = 0.0

    ym_set = set(month_keys)
    for r in receipts:
        if r.transaction_type != tx_type:
            continue
        ym = (r.created_date.year, r.created_date.month)
        if ym in ym_set:
            key = datetime.date(ym[0], ym[1], 1).strftime("%b")
            totals[key] += r.effective_total

    return totals


def get_category_totals(receipts: List[Receipt], tx_type: str = "expense") -> dict:
    totals: dict = {}
    for r in receipts:
        if r.transaction_type != tx_type:
            continue
        scale = (r.base_total / r.total) if (r.base_total is not None and r.total > 0) else 1.0
        for item in r.items:
            totals[item.category] = totals.get(item.category, 0.0) + (item.price * scale)
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def get_summary(receipts: List[Receipt]) -> dict:
    income   = sum(r.effective_total for r in receipts if r.transaction_type == "income")
    expenses = sum(r.effective_total for r in receipts if r.transaction_type == "expense")
    return {"income": income, "expenses": expenses, "balance": income - expenses}
