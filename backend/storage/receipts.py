# -*- coding: utf-8 -*-
"""backend/storage/receipts.py — Receipt persistence (JSON)."""

import json
import datetime
from typing import List

from backend.models import Receipt
from backend.storage._paths import RECEIPTS_FILE, ensure_data_dir


def load_receipts() -> List[Receipt]:
    ensure_data_dir()
    if not RECEIPTS_FILE.exists():
        return []
    try:
        return [Receipt.from_dict(r) for r in json.loads(RECEIPTS_FILE.read_text("utf-8"))]
    except Exception:
        return []


def save_receipts(receipts: List[Receipt]):
    ensure_data_dir()
    RECEIPTS_FILE.write_text(
        json.dumps([r.to_dict() for r in receipts], ensure_ascii=False, indent=2), "utf-8")


def add_receipt(r: Receipt) -> List[Receipt]:
    rs = load_receipts()
    rs.insert(0, r)
    save_receipts(rs)
    return rs


def update_receipt(r: Receipt) -> List[Receipt]:
    rs = load_receipts()
    for i, x in enumerate(rs):
        if x.id == r.id:
            rs[i] = r
            break
    save_receipts(rs)
    return rs


def delete_receipts(ids: List[str]) -> List[Receipt]:
    rs = [r for r in load_receipts() if r.id not in ids]
    save_receipts(rs)
    return rs


def update_receipts_date(ids: List[str], dt: datetime.datetime) -> List[Receipt]:
    rs = load_receipts()
    for r in rs:
        if r.id in ids:
            r.created_date = dt
    save_receipts(rs)
    return rs
