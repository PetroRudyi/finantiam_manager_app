# -*- coding: utf-8 -*-
"""backend/storage/export.py — CSV export."""

import csv
from typing import List

from backend.models import Receipt, AppSettings
from backend.storage._paths import EXPORT_FILE, ensure_data_dir


def export_to_csv(receipts: List[Receipt], settings: AppSettings | None = None) -> str:
    ensure_data_dir()
    rows = []
    for r in receipts:
        for item in r.items:
            cat_value = item.category
            if settings is not None:
                cat_value = settings.get_category_name(item.category)
            rows.append({
                "created_date": r.created_date.strftime("%d.%m.%Y %H:%M"),
                "business_name": r.business_name or "",
                "currency": r.currency,
                "transaction_type": r.transaction_type,
                "name": item.name,
                "category": cat_value,
                "quantity": item.quantity, "price": item.price,
                "exchange_rate": r.exchange_rate or "",
                "base_currency": r.base_currency or "",
                "base_total": r.base_total or "",
            })
    fields = ["created_date", "business_name", "currency", "transaction_type",
              "name", "category", "quantity", "price",
              "exchange_rate", "base_currency", "base_total"]
    with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    return str(EXPORT_FILE)
