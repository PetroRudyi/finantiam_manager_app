# -*- coding: utf-8 -*-
"""backend/models.py — Pydantic data models."""

import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.config import (
    DEFAULT_CURRENCY,
    DEFAULT_CATEGORY_DEFS,
    DEFAULT_CATEGORY_ID,
    normalize_currency,
)

# Original default category names (from categories.json) keyed by ID
_DEFAULT_CAT_NAMES: dict = {c.id: c.name for c in DEFAULT_CATEGORY_DEFS}


class Category(BaseModel):
    """User category stored in settings (ID + display name)."""

    id: str
    name: str
    deleted: bool = False


class InvoiceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    quantity: float = 1.0
    price: float
    # category field зберігає саме ID категорії
    category: str = DEFAULT_CATEGORY_ID

    def to_dict(self) -> dict:
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> "InvoiceItem":
        # Підтримка старого формату: якщо колись буде поле category_name,
        # беремо саме category як ID
        return cls(**data)


class Receipt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    business_name: Optional[str] = None
    # currency зберігає ID / код валюти (з дефолтного конфігу)
    currency: str = DEFAULT_CURRENCY
    transaction_type: str = "expense"   # "expense" | "income"
    items: List[InvoiceItem] = Field(default_factory=list)

    # Курс валют: конвертація receipt.currency → base_currency
    exchange_rate: Optional[float] = None    # курс на дату чеку
    base_currency: Optional[str] = None      # базова валюта на момент збереження
    base_total: Optional[float] = None       # сума в базовій валюті

    @property
    def total(self) -> float:
        return sum(item.price for item in self.items)

    @property
    def effective_total(self) -> float:
        """Total in base currency, falling back to original total."""
        return self.base_total if self.base_total is not None else self.total

    @property
    def categories_summary(self) -> str:
        # Повертаємо у вигляді ID-шників; UI сам мапить у назви з settings
        cats = list(dict.fromkeys(item.category for item in self.items))
        return ", ".join(cats[:3]) + ("..." if len(cats) > 3 else "")

    def to_dict(self) -> dict:
        d = self.model_dump()
        d["created_date"] = self.created_date.isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Receipt":
        if isinstance(data.get("created_date"), str):
            data["created_date"] = datetime.datetime.fromisoformat(data["created_date"])
        if "items" in data:
            data["items"] = [InvoiceItem.from_dict(i) for i in data["items"]]
        # Normalize currency: "Lei" → "RON", "₴" → "UAH", etc.
        if "currency" in data:
            data["currency"] = normalize_currency(data["currency"])
        return cls(**data)


class AppSettings(BaseModel):
    # ID / код валюти за замовчуванням
    default_currency: str = DEFAULT_CURRENCY
    language: str = "en"
    dark_theme: bool = True
    date_format: str = "DD.MM.YY"
    gemini_api_key: str = ""
    ai_auto_fill: bool = True
    exchange_markup_enabled: bool = False
    exchange_markup_percent: float = 0.0
    # список користувацьких категорій (ID + назва)
    categories: List[Category] = Field(
        default_factory=lambda: [
            Category(id=c.id, name=c.name) for c in DEFAULT_CATEGORY_DEFS
        ]
    )

    def to_dict(self) -> dict:
        # Не зберігаємо API ключ Gemini у файл налаштувань
        data = self.model_dump()
        data["gemini_api_key"] = ""
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        # Міграція зі старого формату, де categories: List[str]
        cats = data.get("categories")
        if cats and isinstance(cats, list) and cats and isinstance(cats[0], str):
            data = dict(data)
            data["categories"] = [
                {"id": name, "name": name} for name in cats
            ]
        return cls(**data)

    # ── Category helpers ───────────────────────────────────────

    def get_category_name(self, category_id: str) -> str:
        for c in self.categories:
            if c.id == category_id:
                # Default categories (ID in defaults): if name hasn't been
                # renamed by user, return translated name for current language.
                if c.id in _DEFAULT_CAT_NAMES and c.name == _DEFAULT_CAT_NAMES[c.id]:
                    from frontend.localisation import t
                    translated = t(f"default_categories.{c.id}")
                    if translated != f"default_categories.{c.id}":
                        return translated
                return c.name
        return category_id

    def get_category_id_by_name(self, name: str) -> Optional[str]:
        for c in self.categories:
            if c.name == name:
                return c.id
        return None

    def _next_category_id(self) -> str:
        """Повертає наступний вільний числовий ID (max + 1)."""
        max_id = 0
        for c in self.categories:
            try:
                max_id = max(max_id, int(c.id))
            except (TypeError, ValueError):
                # Ігноруємо нечислові ID з минулого формату
                continue
        return str(max_id + 1 if max_id > 0 else 1)

    def ensure_category(self, name: str) -> str:
        """Повертає ID для категорії з такою назвою, створюючи нову при потребі."""
        cid = self.get_category_id_by_name(name)
        if cid is not None:
            return cid
        # Нові категорії отримують числовий ID: max(id) + 1
        cid = self._next_category_id()
        self.categories.append(Category(id=cid, name=name))
        return cid
