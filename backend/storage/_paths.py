# -*- coding: utf-8 -*-
"""backend/storage/_paths.py — Shared file paths and directory setup."""

from pathlib import Path

DATA_DIR       = Path("data")
RECEIPTS_FILE  = DATA_DIR / "receipts.json"
SETTINGS_FILE  = DATA_DIR / "settings.json"
EXPORT_FILE    = DATA_DIR / "export.csv"
API_KEY_FILE   = DATA_DIR / "gemini_api_key.json"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
