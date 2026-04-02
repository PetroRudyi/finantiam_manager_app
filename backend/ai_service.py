# -*- coding: utf-8 -*-
"""backend/ai_service.py — Gemini AI receipt extraction.

This module provides a single entry point used by the UI:
- `extract_receipt_from_image(...)`
- `merge_duplicate_items(...)`

Implementation is based on the improved "image → validated JSON" approach:
we request `application/json` + a strict schema and retry on validation errors.
"""

import datetime
from typing import List, Optional, Tuple, Dict
from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from backend.config import DEFAULT_CURRENCY, DEFAULT_CATEGORY, CURRENCY_CODES, normalize_currency


class AIInvoiceItem(BaseModel):
    name: str = Field(...)
    quantity: float = Field(default=1.0)
    price: float = Field(...)
    category: str = Field(default=DEFAULT_CATEGORY)

    @field_validator("name", "category", mode="before")
    @classmethod
    def _strip_text(cls, v):
        if v is None:
            return ""
        return str(v).strip()

    @field_validator("quantity", "price", mode="before")
    @classmethod
    def _to_float(cls, v):
        if v is None or v == "":
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        s = str(v).strip()
        # Normalize common decimal formats: "12,34" -> "12.34"
        s = s.replace(" ", "").replace("\u00a0", "").replace(",", ".")
        # Strip currency symbols/letters around numbers (best effort)
        cleaned = "".join(ch for ch in s if (ch.isdigit() or ch in ".-"))
        return float(cleaned) if cleaned else 0.0


class AIReceiptDetail(BaseModel):
    # Валюта з чеку; якщо сервіс не поверне, нижче підставимо default_currency
    currency: str = Field(default=DEFAULT_CURRENCY)
    business_name: Optional[str] = Field(default=None)
    created_date: Optional[datetime.datetime] = Field(default=None)
    invoice_items: List[AIInvoiceItem] = Field(...)


def extract_receipt_from_image(
    image_path: str,
    api_key: str,
    default_currency: str = DEFAULT_CURRENCY,
    categories: Optional[List[str]] = None,
) -> AIReceiptDetail:
    try:
        from google import genai
        from google.genai import types
        from PIL import Image as PIL_Image
    except ImportError as e:
        raise ImportError(
            f"Missing dependency: {e}\n"
            "Run: pip install google-genai pillow"
        )

    if not api_key:
        raise ValueError("Gemini API key is not set.")
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = PIL_Image.open(image_path).convert("RGB")

    # categories може бути як List[str], так і List[Category]; приводимо до назв
    cat_names: List[str] = []
    if categories:
        for c in categories:
            if isinstance(c, str):
                if c.strip():
                    cat_names.append(c.strip())
            else:
                name = getattr(c, "name", None)
                if name and str(name).strip():
                    cat_names.append(str(name).strip())

    cat_hint = (
        "\nAvailable categories (choose closest, or use 'Інше' if unsure): "
        + ", ".join(cat_names)
        if cat_names
        else ""
    )

    currency_list = ", ".join(CURRENCY_CODES)
    prompt = f"""
You are extracting structured data from a receipt image.

Rules (follow exactly):
- Output MUST match the provided JSON schema.
- currency: MUST be one of [{currency_list}]. If not visible, use: {default_currency}. Do NOT use symbols like "Lei", "лей", "₴" — use the ISO code.
- business_name: null if not printed. Do NOT guess.
- created_date: null if not printed. Do NOT guess.
- invoice_items: include each purchased line item. Use a reasonable quantity (1 if missing).
- Numbers: use decimals with a dot. Remove currency symbols from numeric fields.
- category: You MUST ONLY use one of the available categories listed below. Do NOT invent or create new categories. If no category fits, use '{DEFAULT_CATEGORY}'.
Return text in the same language as the receipt (do not translate).
{cat_hint}
""".strip()

    client = genai.Client(api_key=api_key)
    contents = [prompt, img]

    last_err: Optional[Exception] = None
    for _attempt in range(3):
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.9,
                    response_mime_type="application/json",
                    response_schema=AIReceiptDetail,
                ),
            )
            parsed: AIReceiptDetail = resp.parsed
            parsed = AIReceiptDetail.model_validate(parsed.model_dump())
            if not parsed.currency:
                parsed.currency = default_currency
            # Normalize: "Lei" → "RON", "₴" → "UAH", etc.
            parsed.currency = normalize_currency(parsed.currency)
            # created_date deliberately stays None if missing
            return parsed
        except Exception as e:
            last_err = e
            contents = [
                prompt,
                img,
                f"Previous attempt failed with error: {type(e).__name__}: {e}.\n"
                "Return ONLY valid JSON that matches the schema.",
            ]

    raise RuntimeError(f"Failed to extract receipt after retries: {last_err}")


def merge_duplicate_items(items: List[AIInvoiceItem]) -> List[AIInvoiceItem]:
    bucket: Dict[Tuple[str, str], AIInvoiceItem] = {}
    for it in items:
        name = (it.name or "").strip()
        category = (it.category or DEFAULT_CATEGORY).strip() or DEFAULT_CATEGORY
        key: Tuple[str, str] = (name.lower(), category)
        if key not in bucket:
            bucket[key] = AIInvoiceItem(name=name, category=category, quantity=0.0, price=0.0)
        bucket[key].quantity += float(it.quantity)
        bucket[key].price += float(it.price)

    merged = list(bucket.values())
    merged.sort(key=lambda x: (x.category.lower(), x.name.lower()))
    return merged
