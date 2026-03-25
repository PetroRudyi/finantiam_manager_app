# -*- coding: utf-8 -*-
"""backend/storage/_paths.py — Shared file paths and directory setup."""

import os
import sys
from pathlib import Path

# On Android/iOS FLET_APP_STORAGE_DATA points to a persistent directory
# that survives APK updates. On desktop use platform-specific app data dir.
_storage = os.getenv("FLET_APP_STORAGE_DATA")

if _storage:
    DATA_DIR = Path(_storage)
else:
    # Desktop fallback — keep data outside the project directory
    if sys.platform == "win32":
        _base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        _base = Path.home() / "Library" / "Application Support"
    else:
        _base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    DATA_DIR = _base / "finance_manager"

RECEIPTS_FILE  = DATA_DIR / "receipts.json"
SETTINGS_FILE  = DATA_DIR / "settings.json"
EXPORT_FILE    = DATA_DIR / "export.csv"
API_KEY_FILE   = DATA_DIR / "gemini_api_key.json"


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
