# -*- coding: utf-8 -*-
"""backend/storage/settings.py — Settings persistence (JSON)."""

import json

from backend.models import AppSettings
from backend.storage._paths import SETTINGS_FILE, API_KEY_FILE, ensure_data_dir


def load_settings() -> AppSettings:
    ensure_data_dir()
    first_launch = not SETTINGS_FILE.exists()
    settings = AppSettings()
    if not first_launch:
        try:
            settings = AppSettings.from_dict(
                json.loads(SETTINGS_FILE.read_text("utf-8"))
            )
        except Exception:
            pass
    if first_launch:
        from frontend.localisation import detect_system_language
        settings.language = detect_system_language()
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
