# -*- coding: utf-8 -*-
"""app/state.py — Centralized application state with typed access."""

from typing import List

import backend
from backend.models import AppSettings, Receipt


class AppState:
    """Typed wrapper around shared application state.

    Replaces the raw ``{"settings": ..., "receipts": ..., "current_tab": 0}``
    dictionary that was previously passed to every screen.
    """

    def __init__(self):
        self.settings: AppSettings = backend.load_settings()
        self.receipts: List[Receipt] = backend.load_receipts()
        self.current_tab: int = 0

    def reload(self):
        """Reload both settings and receipts from disk."""
        self.settings = backend.load_settings()
        self.receipts = backend.load_receipts()

    def reload_settings(self):
        self.settings = backend.load_settings()

    def reload_receipts(self):
        self.receipts = backend.load_receipts()

    @property
    def default_currency(self) -> str:
        return self.settings.default_currency
