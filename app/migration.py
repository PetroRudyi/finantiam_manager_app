# -*- coding: utf-8 -*-
"""app/migration.py — Background exchange rate migration on startup."""

import backend


def run_background_migration(app_state, on_complete=None):
    """Check and recalculate exchange rates for existing receipts if needed.

    Call this in a background thread at startup.
    """
    s = app_state.settings
    rs = app_state.receipts
    needs = any(
        r.base_currency is None and r.currency != s.default_currency
        for r in rs
    ) or any(
        r.base_currency is not None and r.base_currency != s.default_currency
        for r in rs
    ) or any(
        r.currency != s.default_currency and r.exchange_rate is None
        for r in rs
    )
    if needs:
        print(f"[migration] Recalculating exchange rates → {s.default_currency}")
        app_state.receipts = backend.recalculate_all_receipts(s.default_currency)
        if on_complete:
            try:
                on_complete()
            except Exception:
                pass
        print("[migration] Done")
