# -*- coding: utf-8 -*-
"""backend/config.py — Centralized currency and category configuration.

Цей модуль читає дефолтні конфіги з папки config/.
"""

import json
from pathlib import Path
from typing import Dict, List, NamedTuple


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"


class CurrencyDef(NamedTuple):
    id: str           # stable ID, зазвичай дорівнює коду
    code: str         # короткий код (UAH, USD, ...)
    symbol: str       # грошовий символ
    name: str         # локалізована назва


class CategoryDef(NamedTuple):
    id: str           # stable ID, з яким працюють чеки
    name: str         # поточна назва для відображення


def _load_json(name: str):
    path = CONFIG_DIR / name
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text("utf-8"))
    except Exception:
        return []


def _load_currencies() -> List[CurrencyDef]:
    data = _load_json("currencies.json")
    items: List[CurrencyDef] = []
    for row in data:
        try:
            items.append(
                CurrencyDef(
                    id=str(row.get("id") or row.get("code")),
                    code=str(row.get("code") or row.get("id")),
                    symbol=str(row.get("symbol") or ""),
                    name=str(row.get("name") or str(row.get("code") or row.get("id"))),
                )
            )
        except Exception:
            continue
    return items


def _load_categories() -> List[CategoryDef]:
    data = _load_json("categories.json")
    items: List[CategoryDef] = []
    for row in data:
        try:
            cid = str(row.get("id") or row.get("name"))
            name = str(row.get("name") or cid)
            items.append(CategoryDef(id=cid, name=name))
        except Exception:
            continue
    return items


CURRENCIES: List[CurrencyDef] = _load_currencies()
CURRENCY_CODES: List[str] = [c.code for c in CURRENCIES]
CURRENCY_MAP: Dict[str, CurrencyDef] = {c.code: c for c in CURRENCIES}


# ── Languages ─────────────────────────────────────────

def _load_languages() -> Dict[str, str]:
    """Load supported languages from config/languages.json → {code: name}."""
    data = _load_json("languages.json")
    result: Dict[str, str] = {}
    for row in data:
        code = str(row.get("code", ""))
        name = str(row.get("name", code))
        if code:
            result[code] = name
    return result if result else {"en": "English"}


SUPPORTED_LANGUAGES: Dict[str, str] = _load_languages()
LANGUAGE_CODES: List[str] = list(SUPPORTED_LANGUAGES.keys())

# Map: symbol / name / id → canonical code  (for normalizing "Lei" → "RON" etc.)
_ALIAS_TO_CODE: Dict[str, str] = {}
for _c in CURRENCIES:
    _ALIAS_TO_CODE[_c.code] = _c.code
    _ALIAS_TO_CODE[_c.symbol] = _c.code
    _ALIAS_TO_CODE[_c.symbol.lower()] = _c.code
    _ALIAS_TO_CODE[_c.name] = _c.code
    _ALIAS_TO_CODE[_c.name.lower()] = _c.code
    _ALIAS_TO_CODE[_c.id] = _c.code

DEFAULT_CURRENCY: str = (CURRENCIES[0].code if CURRENCIES else "UAH")


def normalize_currency(raw: str) -> str:
    """Normalize a currency symbol/name/alias to its canonical code.

    'Lei' → 'RON', 'lei' → 'RON', '₴' → 'UAH', etc.
    Falls back to raw value if unknown.
    """
    return _ALIAS_TO_CODE.get(raw) or _ALIAS_TO_CODE.get(raw.strip()) or raw


def get_symbol(code: str) -> str:
    """Return the currency symbol for a given code, or the code itself as fallback."""
    cur = CURRENCY_MAP.get(code)
    return cur.symbol if cur else code


DEFAULT_CATEGORY_DEFS: List[CategoryDef] = _load_categories()
DEFAULT_CATEGORY_ID: str = (
    DEFAULT_CATEGORY_DEFS[-1].id if DEFAULT_CATEGORY_DEFS else "Інше"
)

# Backwards-compatible aliases for old imports
# - DEFAULT_CATEGORY: string назви дефолтної категорії
# - DEFAULT_CATEGORIES: список назв усіх дефолтних категорій
DEFAULT_CATEGORY: str = (
    DEFAULT_CATEGORY_DEFS[-1].name if DEFAULT_CATEGORY_DEFS else "Інше"
)
DEFAULT_CATEGORIES: List[str] = [c.name for c in DEFAULT_CATEGORY_DEFS]


# ── Gemini models ───────────────────────────────────────

GEMINI_MODELS: List[str] = [
    "models/gemini-2.5-flash",
    "models/gemini-3-flash-preview",
    "models/gemini-flash-latest",
    "models/gemini-flash-lite-latest",
    "models/gemma-4-26b-a4b-it",
]

DEFAULT_GEMINI_MODEL: str = GEMINI_MODELS[0]


# ── App meta (version, update URLs) ─────────────────────

_app_cfg = _load_json("app.json") if (CONFIG_DIR / "app.json").exists() else {}
if isinstance(_app_cfg, list):
    _app_cfg = {}

APP_VERSION: str = _app_cfg.get("version", "1.0.0")

_window_cfg = _app_cfg.get("window", {})
BASE_WIDTH: int = _window_cfg.get("base_width", 390)
BASE_HEIGHT: int = _window_cfg.get("base_height", 720)
WINDOW_RESIZABLE: bool = _window_cfg.get("resizable", False)

_update_cfg = _app_cfg.get("update", {})
UPDATE_VERSION_URL: str = _update_cfg.get("version_url", "")
UPDATE_APK_URL: str = _update_cfg.get("apk_url", "")
