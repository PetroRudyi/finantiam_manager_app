# -*- coding: utf-8 -*-
"""backend/storage/recalculation.py — Batch exchange-rate recalculation."""

from typing import List

from backend.models import Receipt
from backend.storage.receipts import load_receipts, save_receipts


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
