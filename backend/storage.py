# -*- coding: utf-8 -*-
"""backend/storage.py — JSON/CSV data layer."""

import json, csv, os, datetime
from typing import List
from pathlib import Path
from backend.models import Receipt, AppSettings

DATA_DIR       = Path("data")
RECEIPTS_FILE  = DATA_DIR / "receipts.json"
SETTINGS_FILE  = DATA_DIR / "settings.json"
EXPORT_FILE    = DATA_DIR / "export.csv"
API_KEY_FILE   = DATA_DIR / "gemini_api_key.json"


def _ensure():
    DATA_DIR.mkdir(exist_ok=True)


# ── Settings ─────────────────────────────────────────────────

def load_settings() -> AppSettings:
    _ensure()
    settings = AppSettings()
    if SETTINGS_FILE.exists():
        try:
            settings = AppSettings.from_dict(
                json.loads(SETTINGS_FILE.read_text("utf-8"))
            )
        except Exception:
            pass
    # Підтягуємо API ключ з окремого локального файлу, якщо він є
    if API_KEY_FILE.exists():
        try:
            data = json.loads(API_KEY_FILE.read_text("utf-8"))
            settings.gemini_api_key = str(data.get("gemini_api_key") or "")
        except Exception:
            settings.gemini_api_key = ""
    return settings


def save_settings(s: AppSettings):
    _ensure()
    # Основні налаштування (без API ключа) — у settings.json
    SETTINGS_FILE.write_text(
        json.dumps(s.to_dict(), ensure_ascii=False, indent=2),
        "utf-8",
    )
    # API ключ — в окремому локальному файлі
    API_KEY_FILE.write_text(
        json.dumps({"gemini_api_key": s.gemini_api_key}, ensure_ascii=False, indent=2),
        "utf-8",
    )


# ── Receipts ──────────────────────────────────────────────────

def load_receipts() -> List[Receipt]:
    _ensure()
    if not RECEIPTS_FILE.exists():
        return []
    try:
        return [Receipt.from_dict(r) for r in json.loads(RECEIPTS_FILE.read_text("utf-8"))]
    except Exception:
        return []


def save_receipts(receipts: List[Receipt]):
    _ensure()
    RECEIPTS_FILE.write_text(
        json.dumps([r.to_dict() for r in receipts], ensure_ascii=False, indent=2), "utf-8")


def add_receipt(r: Receipt) -> List[Receipt]:
    rs = load_receipts(); rs.insert(0, r); save_receipts(rs); return rs

def update_receipt(r: Receipt) -> List[Receipt]:
    rs = load_receipts()
    for i, x in enumerate(rs):
        if x.id == r.id: rs[i] = r; break
    save_receipts(rs); return rs

def delete_receipts(ids: List[str]) -> List[Receipt]:
    rs = [r for r in load_receipts() if r.id not in ids]
    save_receipts(rs); return rs

def update_receipts_date(ids: List[str], dt: datetime.datetime) -> List[Receipt]:
    rs = load_receipts()
    for r in rs:
        if r.id in ids: r.created_date = dt
    save_receipts(rs); return rs


# ── Filtering / analytics ────────────────────────────────────

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
    month_keys = []  # [(year, month), …]

    if target_year is not None and target_month is not None:
        # 4 months before target, target (penultimate), 1 month after
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
        if r.transaction_type != tx_type: continue
        # Масштаб для конвертації елементів у базову валюту
        scale = (r.base_total / r.total) if (r.base_total is not None and r.total > 0) else 1.0
        for item in r.items:
            totals[item.category] = totals.get(item.category, 0.0) + (item.price * scale)
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def get_summary(receipts: List[Receipt]) -> dict:
    income   = sum(r.effective_total for r in receipts if r.transaction_type == "income")
    expenses = sum(r.effective_total for r in receipts if r.transaction_type == "expense")
    return {"income": income, "expenses": expenses, "balance": income - expenses}


# ── Currency recalculation ────────────────────────────────────

def recalculate_all_receipts(new_base_currency: str,
                             progress_callback=None) -> List[Receipt]:
    """Re-fetch exchange rates and recalculate base_total for all receipts."""
    from backend.exchange_service import get_rate_for_receipt, convert_amount

    receipts = load_receipts()
    total = len(receipts)
    ok, fail, skip = 0, 0, 0

    for i, r in enumerate(receipts):
        if r.currency == new_base_currency:
            r.exchange_rate = None
            r.base_currency = new_base_currency
            r.base_total = None
            skip += 1
        else:
            rate = get_rate_for_receipt(r.currency, new_base_currency, r.created_date)
            r.exchange_rate = rate
            r.base_currency = new_base_currency
            r.base_total = convert_amount(r.total, rate)
            if rate is not None:
                ok += 1
            else:
                fail += 1

        if progress_callback:
            progress_callback(i + 1, total)

    print(f"[recalculate] {total} receipts: {ok} converted, {fail} failed, {skip} same currency")
    save_receipts(receipts)
    return receipts


# ── CSV export ───────────────────────────────────────────────

def export_to_csv(receipts: List[Receipt], settings: AppSettings | None = None) -> str:
    _ensure()
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
    fields = ["created_date","business_name","currency","transaction_type",
              "name","category","quantity","price",
              "exchange_rate","base_currency","base_total"]
    with open(EXPORT_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    return str(EXPORT_FILE)
