# -*- coding: utf-8 -*-
"""backend/storage/_paths.py — Shared file paths and directory setup."""

import os
from pathlib import Path

# On Android/iOS FLET_APP_STORAGE_DATA points to a persistent directory
# that survives APK updates. On desktop fallback to local "data" folder.
_storage = os.getenv("FLET_APP_STORAGE_DATA")
DATA_DIR = Path(_storage) if _storage else Path("data")

RECEIPTS_FILE  = DATA_DIR / "receipts.json"
SETTINGS_FILE  = DATA_DIR / "settings.json"
EXPORT_FILE    = DATA_DIR / "export.csv"
API_KEY_FILE   = DATA_DIR / "gemini_api_key.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
