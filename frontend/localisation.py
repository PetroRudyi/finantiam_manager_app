# -*- coding: utf-8 -*-
"""frontend/localisation.py — Translation module.

Loads JSON translation files from locales/ directory.
Supported languages are read from backend.config.SUPPORTED_LANGUAGES.
"""

import json
import locale
from pathlib import Path


_translations: dict = {}
_current_lang: str = "en"

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"


def detect_system_language() -> str:
    """Detect language from system locale. Called once at first startup."""
    from backend.config import SUPPORTED_LANGUAGES
    try:
        sys_locale = locale.getdefaultlocale()[0] or ""
        lang_prefix = sys_locale.split("_")[0]
        if lang_prefix in SUPPORTED_LANGUAGES:
            return lang_prefix
    except Exception:
        pass
    return "en"


def init(language: str):
    """Load translations for given language code."""
    from backend.config import SUPPORTED_LANGUAGES
    global _translations, _current_lang
    _current_lang = language if language in SUPPORTED_LANGUAGES else "en"
    path = _LOCALES_DIR / f"{_current_lang}.json"
    try:
        _translations = json.loads(path.read_text("utf-8")) if path.exists() else {}
    except Exception:
        _translations = {}


def t(key: str) -> str:
    """Get translated string by dot-notation key. Fallback to key itself."""
    parts = key.split(".")
    node = _translations
    for p in parts:
        if isinstance(node, dict):
            node = node.get(p)
        else:
            return key
    return node if isinstance(node, str) else key


def current_language() -> str:
    return _current_lang
