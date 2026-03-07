# -*- coding: utf-8 -*-
"""backend/storage/settings.py — Settings persistence (JSON)."""

import json

from backend.models import AppSettings
from backend.storage._paths import SETTINGS_FILE, API_KEY_FILE, ensure_data_dir


def load_settings() -> AppSettings:
    ensure_data_dir()
    settings = AppSettings()
    if SETTINGS_FILE.exists():
        try:
            settings = AppSettings.from_dict(
                json.loads(SETTINGS_FILE.read_text("utf-8"))
            )
        except Exception:
            pass
    if API_KEY_FILE.exists():
        try:
            data = json.loads(API_KEY_FILE.read_text("utf-8"))
            settings.gemini_api_key = str(data.get("gemini_api_key") or "")
        except Exception:
            settings.gemini_api_key = ""
    return settings


def save_settings(s: AppSettings):
    ensure_data_dir()
    SETTINGS_FILE.write_text(
        json.dumps(s.to_dict(), ensure_ascii=False, indent=2),
        "utf-8",
    )
    API_KEY_FILE.write_text(
        json.dumps({"gemini_api_key": s.gemini_api_key}, ensure_ascii=False, indent=2),
        "utf-8",
    )
